"""TalentMatch: a LangGraph agent that screens resumes against a job description.

Graph (see docs/state_machine.md)::

    START -> parse_jd -> extract_requirements -> search_resumes -> rank_candidates
          -> generate_report -> human_feedback --(router)--> refine_requirements -> search_resumes ...
                                               |-> compare_candidates  -> human_feedback
                                               |-> explain_ranking     -> human_feedback
                                               |-> interview_questions -> human_feedback
                                               |-> candidate_report    -> human_feedback
                                               |-> chat_agent (LLM + tools loop) -> human_feedback
                                               |-> parse_jd (a brand-new search)
                                               '-> END

Multi-round screening lives in the middle of the pipeline:

* Round 1 (``search_resumes``): RAG retrieval + quick must-have screen over all 100 resumes -> top 10.
* Round 2 (``rank_candidates``): per-requirement evidence analysis of the 10 (years per skill,
  quotes from the resume, strengths, gaps, score).
* Round 3 (``rank_candidates``): Strong Hire / Hire / Borderline / No Hire + improvement
  suggestions for borderline candidates; ``generate_report`` writes the explainable match report.

``human_feedback`` pauses the graph with ``interrupt()``; the chat UI resumes it with
``Command(resume=<user text>)``. State is checkpointed (``InMemorySaver``) per conversation thread.

The numbers always come from deterministic tools (``matching_tools.py``). An LLM, when one is
configured, is used where language matters: routing ambiguous requests, parsing unusual
refinements, writing the summaries, and open-ended questions through a tool-calling loop.
Without one the agent runs fully offline.
"""

from __future__ import annotations

import json
import operator
import re
from typing import Annotated, Any, Callable, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt
from pydantic import BaseModel, Field

import fs_tools
import matching_tools as mt
from rag_search import ResumeIndex, get_index, rag_search

REPORT_DIR = "output/reports"
MAX_CHAT_TOOL_ROUNDS = 6
_NUM_WORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "both": 2}


# --------------------------------------------------------------------------- #
# State
# --------------------------------------------------------------------------- #

class MatchState(TypedDict, total=False):
    # conversation history (Human / AI messages), appended by every turn
    messages: Annotated[list[AnyMessage], add_messages]
    # job understanding
    jd_source: str                      # file path or "chat"
    jd_text: str
    requirements: dict[str, Any]
    requirements_history: Annotated[list[dict[str, Any]], operator.add]
    # screening rounds
    screen: dict[str, Any]              # round 1 summary
    shortlist: list[dict[str, Any]]     # round 2+3 analyses, ranked
    previous_shortlist: list[dict[str, Any]]
    ranking_changes: list[dict[str, Any]]
    # reasoning + output
    reasoning: Annotated[list[str], operator.add]   # step-by-step trace shown in the UI
    pending: dict[str, Any]             # routed intent for the current user turn
    response: str                       # what the agent says this turn (markdown)
    report_path: str
    turn: int


# --------------------------------------------------------------------------- #
# Structured-output schemas for the LLM paths
# --------------------------------------------------------------------------- #

class _ReqItem(BaseModel):
    skill: str = Field(description="Technology or skill, e.g. 'React', 'PostgreSQL'")
    min_years: float = Field(0, description="Minimum years for this skill if stated, else 0")


class _Requirements(BaseModel):
    title: str = Field("", description="Job title")
    must_have: list[_ReqItem] = Field(default_factory=list)
    nice_to_have: list[_ReqItem] = Field(default_factory=list)
    min_total_years: float = Field(0, description="Minimum total professional years, 0 if not stated")


class _Intent(BaseModel):
    intent: Literal["refine", "new_search", "compare", "explain", "questions", "detail", "report", "chat", "end"]
    candidates: list[str] = Field(default_factory=list, description="Candidate names mentioned, in order")
    top_n: int = Field(0, description="'top 3' -> 3; 0 if not stated")


# --------------------------------------------------------------------------- #
# Intent routing (rules first, LLM for whatever the rules can't place)
# --------------------------------------------------------------------------- #

_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("end", re.compile(r"^\s*(/?exit|/?quit|bye|done|that'?s all|end|stop)\W*$", re.I)),
    ("questions", re.compile(r"\b(interview|screening)\s+questions?\b|\bwhat (?:should|could) i ask\b", re.I)),
    ("explain", re.compile(r"\bwhy\b.*\b(rank|score|above|higher|lower|below|ahead|better|beat|over|top)\b|\bexplain\b.*\brank", re.I)),
    ("compare", re.compile(r"\b(compare|comparison|side[- ]by[- ]side|head[- ]to[- ]head|versus|vs\.?)\b", re.I)),
    ("new_search", re.compile(r"\b(find|search|look|looking)\b.*\b(candidates?|people|engineers?|developers?|someone)\b|"
                              r"job_descriptions/\S+|\.txt\b", re.I)),
    ("refine", re.compile(r"\b(must[- ]have|nice[- ]to[- ]have|relax|require[sd]?|drop|remove|ignore|optional|"
                          r"prioriti[sz]e|actually|instead|bonus|at least|\d+\+?\s*(?:years?|yrs?))\b", re.I)),
    ("report", re.compile(r"^\s*(?:show|give|display|see)\b.*\b(shortlist|recommendations?|summary|report|results)\b|"
                          r"\bwho should (?:we|i) hire\b", re.I)),
    ("detail", re.compile(r"\b(tell me (?:more )?about|details?|profile|report for|match report|strengths|gaps|"
                          r"deep dive|show me)\b", re.I)),
    ("chat", re.compile(r"^\s*(which|who|does|do|has|have|what|how|is|are|any|list)\b", re.I)),
]


def mentioned_candidates(text: str, index: ResumeIndex, shortlist_ids: list[str]) -> list[str]:
    """Candidate ids mentioned in ``text``, in order of appearance.

    Full names match anyone in the pool; a bare first name ("John") only matches the current
    shortlist, so "John" means the shortlisted John Carter, not John Doe from another role.
    """
    found: list[tuple[int, str]] = []
    spans: list[tuple[int, int]] = []
    low = text.lower()
    for cid, p in index.profiles.items():
        m = re.search(r"\b" + re.escape(p.name.lower()) + r"\b", low)
        if m:
            found.append((m.start(), cid))
            spans.append(m.span())

    def first_name_hit(cid: str) -> int | None:
        m = re.search(r"\b" + re.escape(index.profiles[cid].first_name.lower()) + r"(?:'s)?\b", low)
        if m and not any(s <= m.start() < e for s, e in spans):
            return m.start()
        return None

    taken = {cid for _, cid in found}
    for cid in shortlist_ids:
        if cid not in taken and (pos := first_name_hit(cid)) is not None:
            found.append((pos, cid))
            taken.add(cid)
    # Outside the shortlist a bare first name counts only if exactly one person in the pool has it.
    by_first: dict[str, list[str]] = {}
    for cid, p in index.profiles.items():
        by_first.setdefault(p.first_name.lower(), []).append(cid)
    shortlisted_firsts = {index.profiles[c].first_name.lower() for c in shortlist_ids}
    for first, cids in by_first.items():
        if len(cids) == 1 and cids[0] not in taken and first not in shortlisted_firsts and len(first) > 2:
            if (pos := first_name_hit(cids[0])) is not None:
                found.append((pos, cids[0]))
    found.sort()
    out: list[str] = []
    for _, cid in found:
        if cid not in out:
            out.append(cid)
    return out


def _top_n(text: str) -> int:
    m = re.search(r"\btop\s+(\d+|two|three|four|five|six)\b", text, re.I)
    if m:
        v = m.group(1).lower()
        return int(v) if v.isdigit() else _NUM_WORDS[v]
    m = re.search(r"\b(both)\b", text, re.I)
    return 2 if m else 0


def route_intent(text: str, state: MatchState, index: ResumeIndex, llm: Any | None) -> dict[str, Any]:
    shortlist_ids = [a["candidate_id"] for a in state.get("shortlist", [])]
    names = mentioned_candidates(text, index, shortlist_ids)
    intent, how = None, "rules"
    for name, pattern in _RULES:
        if pattern.search(text):
            intent = name
            break
    # A skill mention plus "must/need" is a refinement even if it also says "find".
    if intent == "new_search" and state.get("requirements") and re.search(r"\b(also|instead|now|actually)\b", text, re.I):
        intent = "refine"
    if intent in (None, "detail") and not names and llm is not None:
        try:
            out = llm.with_structured_output(_Intent).invoke([
                SystemMessage("Classify a recruiter's message to a resume-screening agent. intents: refine (change "
                              "the job requirements, e.g. make a skill must-have, relax years), new_search (a brand-new "
                              "role or query), compare (side-by-side of named/top candidates), explain (why one "
                              "candidate ranks above another), questions (interview questions for a candidate), "
                              "detail (one named candidate's match report), report (re-display the current shortlist "
                              "table only), chat (any question about candidates' skills, experience or resumes that "
                              "needs searching), end (finish)."),
                HumanMessage(text)])
            intent, how = out.intent, "llm"
            names = names or [c for n in out.candidates if (c := index.find_candidate(n, shortlist_ids))]
        except Exception as exc:  # noqa: BLE001 - model errors fall back to rules
            how = f"rules (llm failed: {type(exc).__name__})"
    if intent is None:
        intent = "detail" if names else "chat"
    if intent == "detail" and not names:
        intent = "chat"
    return {"intent": intent, "text": text, "candidates": names, "top_n": _top_n(text), "router": how}


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #

_VERDICT_ICON = {"Strong Hire": "++", "Hire": "+", "Borderline": "~", "No Hire": "-"}


def _shortlist_table(shortlist: list[dict[str, Any]]) -> str:
    rows = ["| # | Candidate | Score | Verdict | Top strength | Main gap |", "|---|---|---|---|---|---|"]
    for a in shortlist:
        rows.append(f"| {a['rank']} | {a['name']} | {a['score']:g} | {a['recommendation']['verdict']} | "
                    f"{(a['strengths'] or ['-'])[0]} | {(a['gaps'] or ['-'])[0]} |")
    return "\n".join(rows)


def candidate_markdown(a: dict[str, Any]) -> str:
    rec = a["recommendation"]
    lines = [f"### {a['rank']}. {a['name']} - {a['headline']}  ({a['score']:g}/100, {rec['verdict']})",
             f"*{a['filepath']} | {a['total_years']:g} yrs total*", "",
             f"**Recommendation:** {rec['rationale']}", "",
             "| Requirement | Type | Status | Evidence |", "|---|---|---|---|"]
    for b in a["breakdown"]:
        ev = b["evidence"][0][:90] if b["evidence"] else b["detail"]
        lines.append(f"| {b['requirement']}{' ' + format(b['min_years'], 'g') + '+ yrs' if b['min_years'] else ''} "
                     f"| {b['kind']} | {b['status']} | {ev} |")
    lines += ["", "**Strengths:** " + ("; ".join(a["strengths"]) or "-"),
              "**Gaps:** " + ("; ".join(a["gaps"]) or "none")]
    if rec["suggestions"]:
        lines += ["", "**Improvement suggestions:**"] + [f"- {s}" for s in rec["suggestions"]]
    return "\n".join(lines)


def _llm_prose(llm: Any | None, instruction: str, facts: Any, fallback: str) -> str:
    """Let the LLM phrase grounded facts; any failure returns the deterministic fallback."""
    if llm is None:
        return fallback
    try:
        msg = llm.invoke([
            SystemMessage("You are a recruiting assistant. Use ONLY the facts provided; never invent experience, "
                          "numbers or names. Be concise (<= 120 words), plain text, no headings."),
            HumanMessage(f"{instruction}\n\nFACTS (JSON):\n{json.dumps(facts, default=str)[:12000]}"),
        ])
        text = msg.content if isinstance(msg.content, str) else "".join(
            p.get("text", "") for p in msg.content if isinstance(p, dict))
        return text.strip() or fallback
    except Exception:  # noqa: BLE001
        return fallback


# --------------------------------------------------------------------------- #
# Agent
# --------------------------------------------------------------------------- #

class MatchingAgent:
    """Builds and runs the LangGraph. ``llm=None`` runs fully offline."""

    def __init__(self, llm: Any | None = None, resume_dir: str = "resumes", checkpointer: Any | None = None):
        self.llm = llm
        self.index = get_index(resume_dir)
        self.graph = self.build_graph(checkpointer or InMemorySaver())

    # ------------------------------------------------------------------ nodes
    def parse_jd(self, state: MatchState) -> dict[str, Any]:
        pending = state.get("pending") or {}
        text = pending.get("text") or state.get("jd_text") or ""
        if not text and state.get("messages"):
            text = next((m.content for m in reversed(state["messages"]) if isinstance(m, HumanMessage)), "")
        source = state.get("jd_source") if not pending else "chat"
        path_match = re.search(r"[\w./\\-]+\.(?:txt|pdf|docx)\b", text)
        if path_match:
            res = fs_tools.read_file(path_match.group(0).replace("\\", "/"))
            if res.get("success"):
                source, text = res["filepath"], res["content"]
        elif state.get("jd_source") and not pending:
            res = fs_tools.read_file(state["jd_source"])
            if res.get("success"):
                text = res["content"]
        words = len(text.split())
        return {"jd_text": text, "jd_source": source or "chat", "previous_shortlist": [], "ranking_changes": [],
                "shortlist": [], "turn": state.get("turn", 0),
                "reasoning": [f"[parse_jd] Read the job brief from {source or 'chat'} ({words} words)."]}

    def extract_requirements(self, state: MatchState) -> dict[str, Any]:
        reqs = mt.extract_requirements(state["jd_text"])
        how = "rule-based parser"
        if self.llm is not None and len(state["jd_text"].split()) > 25:
            try:
                out = self.llm.with_structured_output(_Requirements).invoke([
                    SystemMessage("Extract hiring requirements from the job description. Must-have = required; "
                                  "nice-to-have = preferred/bonus. Use short canonical skill names."),
                    HumanMessage(state["jd_text"])])
                reqs = _merge_llm_requirements(reqs, out)
                how = "LLM extraction, merged with the rule-based parser"
            except Exception as exc:  # noqa: BLE001
                how = f"rule-based parser (LLM failed: {type(exc).__name__})"
        must = ", ".join(r["skill"] + (f" {r['min_years']:g}+y" if r["min_years"] else "") for r in reqs["must_have"])
        nice = ", ".join(r["skill"] for r in reqs["nice_to_have"]) or "none"
        return {"requirements": reqs, "requirements_history": [reqs],
                "reasoning": [f"[extract_requirements] {how}: must-have = {must or 'none'}; nice-to-have = {nice}"
                              + (f"; {reqs['min_total_years']:g}+ yrs total" if reqs.get("min_total_years") else "")]}

    def search_resumes(self, state: MatchState) -> dict[str, Any]:
        screen = mt.initial_screen(self.index, state["requirements"])
        cut = ", ".join(f"{k} ({v})" for k, v in list(screen["cut_reasons"].items())[:3])
        return {"screen": screen,
                "reasoning": [f"[search_resumes] Round 1: RAG query '{mt.requirements_query(state['requirements'])}' "
                              f"over {screen['screened']} resumes -> kept top {len(screen['kept'])} "
                              f"(cut-off quick score {screen['cutoff_score']}). Most common misses: {cut or 'none'}."]}

    def rank_candidates(self, state: MatchState) -> dict[str, Any]:
        kept = state["screen"]["kept"]
        top = max((k["quick_score"] for k in kept), default=1) or 1
        relevance = {k["candidate_id"]: k["quick_score"] / top for k in kept}
        ranked = mt.rank(self.index, state["requirements"], [k["candidate_id"] for k in kept], relevance)
        previous = state.get("shortlist") or []
        changes = mt.ranking_changes(previous, ranked) if previous else []
        counts: dict[str, int] = {}
        for a in ranked:
            counts[a["recommendation"]["verdict"]] = counts.get(a["recommendation"]["verdict"], 0) + 1
        verdicts = ", ".join(f"{v} {counts[v]}" for v in ("Strong Hire", "Hire", "Borderline", "No Hire") if v in counts)
        notes = [f"[rank_candidates] Round 2: scored {len(ranked)} candidates requirement by requirement "
                 f"(evidenced years, resume quotes). Leader: {ranked[0]['name']} ({ranked[0]['score']:g})."
                 if ranked else "[rank_candidates] No candidates to rank.",
                 f"[rank_candidates] Round 3: hire/no-hire -> {verdicts}."]
        if changes:
            notes.append(f"[rank_candidates] Re-ranked after the requirement change: {len(changes)} candidates moved.")
        return {"shortlist": ranked, "previous_shortlist": previous, "ranking_changes": changes, "reasoning": notes}

    def generate_report(self, state: MatchState) -> dict[str, Any]:
        reqs, shortlist, screen = state["requirements"], state["shortlist"], state["screen"]
        title = reqs.get("title") or "Role"
        parts = [f"## Shortlist: {title}", mt.describe_requirements(reqs), "",
                 f"Screened **{screen['screened']}** resumes -> deep-analysed **{len(shortlist)}** -> "
                 f"recommendations below.", "", _shortlist_table(shortlist)]
        changes = state.get("ranking_changes") or []
        if changes:
            parts += ["", "### What changed"] + [_change_line(c) for c in changes]
        if shortlist:
            top = shortlist[0]
            fallback = (f"{top['name']} leads with {top['score']:g}/100: {', '.join(top['strengths'][:3]) or 'solid fit'}."
                        + (f" Watch: {top['gaps'][0]}." if top["gaps"] else ""))
            summary = _llm_prose(self.llm, "Write a 2-3 sentence executive summary of this shortlist for a hiring "
                                 "manager: who to interview first and why, and the main risk.",
                                 {"requirements": reqs, "top3": [_brief(a) for a in shortlist[:3]],
                                  "changes": changes[:5]}, fallback)
            parts += ["", "### Agent assessment", summary]
            borderline = [a for a in shortlist if a["recommendation"]["verdict"] == "Borderline"]
            if borderline:
                parts += ["", "### Borderline - what would make them a hire"]
                for a in borderline[:3]:
                    parts.append(f"- **{a['name']}**: " + " ".join(a["recommendation"]["suggestions"][:2]))
        path = self._write_report(state, title)
        parts += ["", f"Full match report (all {len(shortlist)} candidates, evidence per requirement): `{path}`",
                  "", "_Try: \"Compare the top 3\", \"Why did X rank higher than Y?\", \"Make GraphQL a must-have\", "
                      "\"Interview questions for X\", \"Tell me about X\"._"]
        response = "\n".join(parts)
        return {"response": response, "report_path": path, "messages": [AIMessage(response)],
                "reasoning": [f"[generate_report] Wrote the explainable match report to {path}."]}

    def human_feedback(self, state: MatchState) -> dict[str, Any]:
        # interrupt() pauses the graph here; nothing before it has side effects (the node re-runs on resume).
        user_text = interrupt({"response": state.get("response", ""), "report_path": state.get("report_path")})
        user_text = str(user_text).strip()
        pending = route_intent(user_text, state, self.index, self.llm)
        names = [self.index.profiles[c].name for c in pending["candidates"]]
        return {"messages": [HumanMessage(user_text)], "pending": pending, "turn": state.get("turn", 0) + 1,
                "reasoning": [f"[human_feedback] Routed to '{pending['intent']}' via {pending['router']}"
                              + (f"; candidates: {', '.join(names)}" if names else "")
                              + (f"; top {pending['top_n']}" if pending["top_n"] else "")]}

    def refine_requirements(self, state: MatchState) -> dict[str, Any]:
        text = state["pending"]["text"]
        new, changes = mt.refine_requirements(state["requirements"], text)
        how = "rule-based"
        if not changes and self.llm is not None:
            try:
                out = self.llm.with_structured_output(_Requirements).invoke([
                    SystemMessage("Apply the recruiter's change to the current requirements and return the full "
                                  "updated requirements."),
                    HumanMessage(f"CURRENT: {json.dumps(state['requirements'])}\nCHANGE: {text}")])
                new = _merge_llm_requirements(mt.empty_requirements() | {"title": state["requirements"]["title"]}, out)
                changes, how = _diff_requirements(state["requirements"], new), "LLM"
            except Exception as exc:  # noqa: BLE001
                how = f"rule-based (LLM failed: {type(exc).__name__})"
        if not changes:
            response = ("I couldn't find a requirement change in that. Try e.g. \"make GraphQL a must-have\", "
                        "\"relax React to 2 years\" or \"drop CSS\".")
            return {"response": response, "messages": [AIMessage(response)], "pending": {"intent": "noop"},
                    "reasoning": ["[refine_requirements] No change detected; asking the user to rephrase."]}
        return {"requirements": new, "requirements_history": [new], "pending": {"intent": "rerank"},
                "reasoning": [f"[refine_requirements] ({how}) " + "; ".join(changes) + ". Re-screening the pool."]}

    def compare_candidates(self, state: MatchState) -> dict[str, Any]:
        p = state["pending"]
        shortlist = state.get("shortlist", [])
        ids = p["candidates"] or [a["candidate_id"] for a in shortlist[: (p["top_n"] or 3)]]
        result = tool_compare(self.index, state, ids)
        if "error" in result:
            return self._say(result["error"], "[compare_candidates] " + result["error"])
        names = result["candidates"]
        lines = [f"## Head-to-head: {' vs '.join(names)}", "",
                 "| Requirement | " + " | ".join(names) + " | Edge |", "|---" * (len(names) + 2) + "|"]
        for row in result["rows"]:
            lines.append(f"| {row['requirement']} ({row['kind']}) | "
                         + " | ".join(f"{_status_icon(row['cells'][n]['status'])} {row['cells'][n]['detail']}" for n in names)
                         + f" | {row['winner']} |")
        lines.append("| **Score / verdict** | " + " | ".join(
            f"**{s['score']:g}** {s['verdict']}" for s in result["summary"]) + f" | {result['overall_winner']} |")
        wins = {n: sum(n in r["winner"].split(" & ") for r in result["rows"]) for n in names}
        fallback = (f"{result['overall_winner']} comes out ahead overall, leading or sharing the lead on "
                    f"{wins[result['overall_winner']]} of {len(result['rows'])} requirement rows. " + " ".join(
                        f"{s['name']}: {s['verdict']} ({s['score']:g})." for s in result["summary"]))
        lines += ["", _llm_prose(self.llm, "Summarise this head-to-head comparison in 3 sentences: who wins, "
                                 "the decisive differences, and when you might still pick the runner-up.",
                                 result, fallback)]
        return self._say("\n".join(lines), f"[compare_candidates] Compared {', '.join(names)}; "
                                             f"winner {result['overall_winner']}.", tool_result=result)

    def explain_ranking(self, state: MatchState) -> dict[str, Any]:
        p = state["pending"]
        shortlist = state.get("shortlist", [])
        by_id = {a["candidate_id"]: a for a in shortlist}
        ids = p["candidates"]
        if len(ids) == 1 and ids[0] in by_id:
            a = by_id[ids[0]]
            neighbour = shortlist[a["rank"]] if a["rank"] < len(shortlist) else shortlist[a["rank"] - 2] if a["rank"] > 1 else None
            ids = [ids[0]] + ([neighbour["candidate_id"]] if neighbour else [])
        if len(ids) < 2:
            ids = [a["candidate_id"] for a in shortlist[:2]]
        missing = [self.index.profiles[c].name for c in ids[:2] if c not in by_id]
        analyses = [by_id.get(c) or _ad_hoc(self.index, state, c) for c in ids[:2]]
        e = mt.explain_pair(*analyses)
        hi = next(a for a in analyses if a["name"] == e["higher"])
        lo = next(a for a in analyses if a["name"] == e["lower"])
        lines = [f"## Why {e['higher']} (#{hi.get('rank', '-')}, {hi['score']:g}) ranks above "
                 f"{e['lower']} (#{lo.get('rank', '-')}, {lo['score']:g})", "",
                 f"Gap: **{e['score_gap']:g} points**. Where it comes from:"]
        lines += [f"- {d['component']}: {d['points']:+g} pts for {e['higher']}" for d in e["component_deltas"]]
        if e["requirement_differences"]:
            lines += ["", "| Requirement | " + e["higher"] + " | " + e["lower"] + " |", "|---|---|---|"]
            for r in e["requirement_differences"]:
                lines.append(f"| {r['requirement']} ({r['kind']}) | {r[e['higher']]} | {r[e['lower']]} |")
        if missing:
            lines.append(f"\n_Note: {', '.join(missing)} is not on the current shortlist; scored ad hoc for this answer._")
        fallback = _explain_fallback(e)
        lines += ["", _llm_prose(self.llm, "Explain in 2-3 plain sentences why the first candidate ranks higher, "
                                 "citing the biggest point differences.", e, fallback)]
        return self._say("\n".join(lines), f"[explain_ranking] {e['higher']} vs {e['lower']}: gap {e['score_gap']:g} pts, "
                                           f"biggest driver {e['component_deltas'][0]['component'] if e['component_deltas'] else 'n/a'}.")

    def interview_questions(self, state: MatchState) -> dict[str, Any]:
        p = state["pending"]
        cid = (p["candidates"] or [a["candidate_id"] for a in state.get("shortlist", [])[:1]] or [None])[0]
        if cid is None:
            return self._say("Run a search first so I know who to prepare questions for.", "[interview_questions] no candidate")
        result = tool_questions(self.index, state, cid)
        lines = [f"## Screening questions for {result['name']}", ""]
        for i, q in enumerate(result["questions"], 1):
            lines.append(f"{i}. **[{q['type']} - {q['area']}]** {q['question']}")
        return self._say("\n".join(lines), f"[interview_questions] {len(result['questions'])} questions for "
                                           f"{result['name']} (depth on evidenced skills, probes on gaps).")

    def candidate_report(self, state: MatchState) -> dict[str, Any]:
        cids = state["pending"]["candidates"][:2]
        by_id = {a["candidate_id"]: a for a in state.get("shortlist", [])}
        blocks = []
        for cid in cids:
            a = by_id.get(cid) or _ad_hoc(self.index, state, cid)
            blocks.append(candidate_markdown(a))
        return self._say("\n\n".join(blocks), "[candidate_report] Match report for "
                         + ", ".join(self.index.profiles[c].name for c in cids) + ".")

    def chat_agent(self, state: MatchState) -> dict[str, Any]:
        question = state["pending"]["text"]
        tools = build_tools(self.index, state)
        if self.llm is None:
            hits = rag_search(question, top_k=4)["results"]
            lines = ["Offline mode: here is what the resumes say (RAG retrieval):", ""]
            lines += [f"- **{h['name']}** ({h['section']}): {h['text'].splitlines()[0][:140]}" for h in hits] or ["- nothing relevant found"]
            return self._say("\n".join(lines), f"[chat_agent] offline: answered from {len(hits)} retrieved chunks.")
        bound = self.llm.bind_tools(tools)
        by_name = {t.name: t for t in tools}
        context = {"requirements": mt.describe_requirements(state["requirements"]) if state.get("requirements") else None,
                   "shortlist": [f"#{a['rank']} {a['name']} [{a['filepath']}] {a['score']:g} "
                                 f"{a['recommendation']['verdict']}" for a in state.get("shortlist", [])]}
        msgs: list[AnyMessage] = [SystemMessage(
            "You are TalentMatch, a recruiting agent. Answer the recruiter using the tools; ground every claim in "
            "tool results and cite candidate names. Prefer search_candidates for 'who has X' questions (one call "
            "covers the whole shortlist). Use at most 3 tool calls, then answer. Current context:\n" + json.dumps(context, default=str)[:8000])]
        # Earlier user turns give conversational context; long AI reports are left out to save context.
        msgs += [m for m in state.get("messages", [])[-8:] if isinstance(m, HumanMessage)][-3:-1]
        msgs.append(HumanMessage(question))
        trace = []
        for _ in range(MAX_CHAT_TOOL_ROUNDS):
            try:
                reply = bound.invoke(msgs)
            except Exception as exc:  # noqa: BLE001
                return self._say(f"The language model failed ({type(exc).__name__}: {str(exc)[:160]}).",
                                 "[chat_agent] LLM error")
            msgs.append(reply)
            if not getattr(reply, "tool_calls", None):
                break
            for call in reply.tool_calls:
                tool = by_name.get(call["name"])
                try:
                    out = tool.invoke(call["args"]) if tool else {"error": f"unknown tool {call['name']}"}
                except Exception as exc:  # noqa: BLE001
                    out = {"error": str(exc)}
                trace.append(f"{call['name']}({', '.join(f'{k}={v!r}' for k, v in call['args'].items())[:80]})")
                msgs.append(ToolMessage(json.dumps(out, default=str)[:6000], tool_call_id=call["id"]))
        if getattr(reply, "tool_calls", None):  # ran out of rounds: force a final answer from what we have
            msgs.append(HumanMessage("Stop calling tools and answer the original question now from the results above."))
            try:
                reply = self.llm.invoke(msgs)
            except Exception:  # noqa: BLE001
                pass
        answer = reply.content if isinstance(reply.content, str) else "".join(
            p.get("text", "") for p in reply.content if isinstance(p, dict))
        return self._say(answer or "(no answer)", "[chat_agent] Tool calls: " + (", ".join(trace) or "none"))

    # ------------------------------------------------------------------ routing
    @staticmethod
    def route_feedback(state: MatchState) -> str:
        intent = (state.get("pending") or {}).get("intent", "chat")
        return {"refine": "refine_requirements", "new_search": "parse_jd", "compare": "compare_candidates",
                "explain": "explain_ranking", "questions": "interview_questions", "detail": "candidate_report",
                "report": "generate_report", "chat": "chat_agent", "end": END}.get(intent, "chat_agent")

    @staticmethod
    def route_after_refine(state: MatchState) -> str:
        return "search_resumes" if (state.get("pending") or {}).get("intent") == "rerank" else "human_feedback"

    # ------------------------------------------------------------------ graph
    def build_graph(self, checkpointer: Any) -> Any:
        g = StateGraph(MatchState)
        for name in ("parse_jd", "extract_requirements", "search_resumes", "rank_candidates", "generate_report",
                     "human_feedback", "refine_requirements", "compare_candidates", "explain_ranking",
                     "interview_questions", "candidate_report", "chat_agent"):
            g.add_node(name, getattr(self, name))
        g.add_edge(START, "parse_jd")
        g.add_edge("parse_jd", "extract_requirements")
        g.add_edge("extract_requirements", "search_resumes")
        g.add_edge("search_resumes", "rank_candidates")
        g.add_edge("rank_candidates", "generate_report")
        g.add_edge("generate_report", "human_feedback")
        g.add_conditional_edges("human_feedback", self.route_feedback, {
            "refine_requirements": "refine_requirements", "parse_jd": "parse_jd",
            "compare_candidates": "compare_candidates", "explain_ranking": "explain_ranking",
            "interview_questions": "interview_questions", "candidate_report": "candidate_report",
            "generate_report": "generate_report", "chat_agent": "chat_agent", END: END})
        g.add_conditional_edges("refine_requirements", self.route_after_refine,
                                {"search_resumes": "search_resumes", "human_feedback": "human_feedback"})
        for n in ("compare_candidates", "explain_ranking", "interview_questions", "candidate_report", "chat_agent"):
            g.add_edge(n, "human_feedback")
        return g.compile(checkpointer=checkpointer)

    # ------------------------------------------------------------------ helpers
    def _say(self, text: str, note: str, tool_result: Any = None) -> dict[str, Any]:
        return {"response": text, "messages": [AIMessage(text)], "reasoning": [note]}

    def _write_report(self, state: MatchState, title: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_") or "role"
        path = f"{REPORT_DIR}/{slug}_v{len(state.get('requirements_history', [])) or 1}.md"
        reqs = state["requirements"]
        body = [f"# Match report: {title}", "", mt.describe_requirements(reqs), "",
                f"Round 1: screened {state['screen']['screened']} resumes, kept {len(state['screen']['kept'])} "
                f"(quick-score cut-off {state['screen']['cutoff_score']}).",
                "Round 2: deep analysis per requirement. Round 3: hire / no-hire recommendation.", "",
                _shortlist_table(state["shortlist"]), ""]
        body += [candidate_markdown(a) + "\n" for a in state["shortlist"]]
        fs_tools.write_file(path, "\n".join(body), overwrite=True)
        return path

    # ------------------------------------------------------------------ public API
    def start(self, query_or_path: str, thread_id: str = "default") -> dict[str, Any]:
        """Begin a screening run; returns at the first human_feedback pause."""
        cfg = {"configurable": {"thread_id": thread_id}}
        inp: dict[str, Any] = {"messages": [HumanMessage(query_or_path)], "pending": {"text": query_or_path}}
        return self._run(inp, cfg)

    def send(self, text: str, thread_id: str = "default") -> dict[str, Any]:
        """Resume the paused graph with the user's message."""
        cfg = {"configurable": {"thread_id": thread_id}}
        snap = self.graph.get_state(cfg)
        if not snap.next:  # conversation ended (or never started): treat as a fresh search
            return self.start(text, thread_id)
        return self._run(Command(resume=text), cfg)

    def _run(self, inp: Any, cfg: dict[str, Any], on_step: Callable[[str, dict[str, Any]], None] | None = None) -> dict[str, Any]:
        before = len(self.graph.get_state(cfg).values.get("reasoning", []) if self.graph.get_state(cfg).values else [])
        steps: list[str] = []
        for chunk in self.graph.stream(inp, cfg, stream_mode="updates"):
            for node, update in chunk.items():
                if node == "__interrupt__":
                    continue
                steps.append(node)
                if on_step and isinstance(update, dict):
                    on_step(node, update)
        snap = self.graph.get_state(cfg)
        values = snap.values
        done = not snap.next
        return {"response": "Session ended. Reports are in output/reports/." if done else values.get("response", ""),
                "reasoning": values.get("reasoning", [])[before:],
                "nodes": steps, "done": done, "state": values}

    def stream(self, inp: Any, thread_id: str, on_step: Callable[[str, dict[str, Any]], None]) -> dict[str, Any]:
        return self._run(inp, {"configurable": {"thread_id": thread_id}}, on_step)


# --------------------------------------------------------------------------- #
# Tools (plain functions + LangChain wrappers for the tool-calling chat node)
# --------------------------------------------------------------------------- #

def _ad_hoc(index: ResumeIndex, state: MatchState, cid: str) -> dict[str, Any]:
    a = mt.analyze_candidate(index, cid, state["requirements"])
    a["recommendation"] = mt.recommend(a)
    a.setdefault("rank", "-")
    return a


def _resolve_ids(index: ResumeIndex, state: MatchState, ids: list[str]) -> list[str]:
    shortlist_ids = [a["candidate_id"] for a in state.get("shortlist", [])]
    out = []
    for i in ids:
        cid = index.find_candidate(str(i), shortlist_ids)
        if cid and cid not in out:
            out.append(cid)
    return out


def tool_compare(index: ResumeIndex, state: MatchState, candidate_ids: list[str]) -> dict[str, Any]:
    ids = _resolve_ids(index, state, candidate_ids)
    if len(ids) < 2:
        return {"error": "Need at least two known candidates to compare (names or ids)."}
    by_id = {a["candidate_id"]: a for a in state.get("shortlist", [])}
    return mt.compare_candidates([by_id.get(c) or _ad_hoc(index, state, c) for c in ids[:5]])


def tool_questions(index: ResumeIndex, state: MatchState, candidate_id: str) -> dict[str, Any]:
    ids = _resolve_ids(index, state, [candidate_id])
    if not ids:
        return {"error": f"Unknown candidate '{candidate_id}'."}
    by_id = {a["candidate_id"]: a for a in state.get("shortlist", [])}
    a = by_id.get(ids[0]) or _ad_hoc(index, state, ids[0])
    return mt.generate_interview_questions(a, state["requirements"], index)


def build_tools(index: ResumeIndex, state: MatchState) -> list[StructuredTool]:
    """Everything the chat node's LLM may call: Milestone 1 file tools, RAG search, matching tools."""

    def list_files(directory: str = "resumes", extension: str | None = None) -> Any:
        """List files in a sandboxed directory (e.g. 'resumes', 'job_descriptions')."""
        try:
            return fs_tools.list_files(directory, extension)[:120]
        except fs_tools.FsToolError as exc:
            return {"error": str(exc)}

    def read_file(filepath: str) -> dict[str, Any]:
        """Read a resume or JD (PDF/DOCX/TXT) and return its text."""
        return fs_tools.read_file(filepath, max_chars=8000)

    def search_in_file(filepath: str, keyword: str) -> dict[str, Any]:
        """Case-insensitive keyword search in one file, with context."""
        return fs_tools.search_in_file(filepath, keyword)

    def write_file(filepath: str, content: str) -> dict[str, Any]:
        """Write a text/markdown file under output/."""
        if not filepath.replace("\\", "/").startswith("output/"):
            return {"error": "Writes are limited to the output/ folder."}
        return fs_tools.write_file(filepath, content, overwrite=True)

    def rag_search_tool(query: str, top_k: int = 5) -> dict[str, Any]:
        """Semantic search over all resume chunks; returns the best-matching snippets with candidate names."""
        return rag_search(query, top_k)

    def extract_requirements(jd: str) -> dict[str, Any]:
        """Parse a job description into must-have vs nice-to-have requirements."""
        return mt.extract_requirements(jd)

    def compare_candidates(candidate_ids: list[str]) -> dict[str, Any]:
        """Head-to-head comparison of 2-5 candidates (names or ids) against the current requirements."""
        return tool_compare(index, state, candidate_ids)

    def generate_interview_questions(candidate_id: str) -> dict[str, Any]:
        """Tailored screening questions for one candidate (name or id)."""
        return tool_questions(index, state, candidate_id)

    def search_candidates(keyword: str, scope: str = "shortlist") -> dict[str, Any]:
        """Keyword search across every shortlisted resume (scope='shortlist') or the whole pool (scope='all').
        Returns, per candidate with a hit, up to 2 matching lines with context."""
        ids = ([a["candidate_id"] for a in state.get("shortlist", [])] if scope != "all" else list(index.profiles))
        hits = {}
        for cid in ids:
            res = fs_tools.search_in_file(index.profiles[cid].filepath, keyword, context_chars=70, max_matches=2)
            if res.get("success") and res["total_matches"]:
                hits[index.profiles[cid].name] = [m["context"] for m in res["matches"]]
        return {"keyword": keyword, "scope": scope, "searched": len(ids), "candidates_with_hits": hits}

    def get_match_report(candidate_id: str) -> dict[str, Any]:
        """Detailed per-requirement match analysis for one candidate (name or id)."""
        ids = _resolve_ids(index, state, [candidate_id])
        if not ids:
            return {"error": f"Unknown candidate '{candidate_id}'."}
        by_id = {a["candidate_id"]: a for a in state.get("shortlist", [])}
        return by_id.get(ids[0]) or _ad_hoc(index, state, ids[0])

    fns = [list_files, read_file, search_in_file, write_file, rag_search_tool, extract_requirements,
           compare_candidates, generate_interview_questions, get_match_report, search_candidates]
    return [StructuredTool.from_function(f, name=("rag_search" if f is rag_search_tool else f.__name__)) for f in fns]


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #

def _merge_llm_requirements(base: dict[str, Any], out: _Requirements) -> dict[str, Any]:
    reqs = {**base, "must_have": [dict(r) for r in base["must_have"]], "nice_to_have": [dict(r) for r in base["nice_to_have"]]}
    reqs["title"] = reqs.get("title") or out.title
    reqs["min_total_years"] = max(reqs.get("min_total_years") or 0, out.min_total_years or 0)
    have = {s for r in reqs["must_have"] + reqs["nice_to_have"] for s in mt.req_skills(r)}
    for kind, items in (("must_have", out.must_have), ("nice_to_have", out.nice_to_have)):
        for item in items:
            skill = mt.canonical_skill(item.skill)
            if skill in have or skill not in mt.known_skill_names():
                continue  # unknown skills can't be evidenced by the parser; keep the list honest
            reqs[kind].append({"skill": skill, "min_years": float(item.min_years or 0), "weight": 1.0})
            have.add(skill)
    return reqs


def _diff_requirements(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    def m(r: dict[str, Any]) -> dict[str, float]:
        return {x["skill"]: x["min_years"] for x in r}
    out = []
    om, nm, on, nn = m(old["must_have"]), m(new["must_have"]), m(old["nice_to_have"]), m(new["nice_to_have"])
    for s, y in nm.items():
        if s not in om:
            out.append(f"{s} is now a must-have")
        elif om[s] != y:
            out.append(f"{s} requirement changed from {om[s]:g}+ to {y:g}+ years")
    for s in om:
        if s not in nm:
            out.append(f"{s} moved to nice-to-have" if s in nn else f"Removed {s}")
    for s in nn:
        if s not in on and s not in om:
            out.append(f"Added nice-to-have {s}")
    return out


def _brief(a: dict[str, Any]) -> dict[str, Any]:
    return {"name": a["name"], "rank": a.get("rank"), "score": a["score"], "verdict": a["recommendation"]["verdict"],
            "strengths": a["strengths"][:4], "gaps": a["gaps"][:4]}


def _status_icon(status: str) -> str:
    return {"met": "[+]", "partial": "[~]", "listed": "[?]", "missing": "[-]"}.get(status, "")


def _change_line(c: dict[str, Any]) -> str:
    if c["from"] is None:
        return f"- **{c['name']}** entered at #{c['to']} ({c['score_to']:g}): {c['reason']}"
    if c["to"] is None:
        return f"- **{c['name']}** dropped out (was #{c['from']}, {c['score_from']:g})"
    arrow = "up" if c["to"] < c["from"] else "down" if c["to"] > c["from"] else "same rank"
    return f"- **{c['name']}** #{c['from']} -> #{c['to']} ({arrow}; {c['score_from']:g} -> {c['score_to']:g}): {c['reason']}"


def _explain_fallback(e: dict[str, Any]) -> str:
    if not e["component_deltas"]:
        return f"{e['higher']} and {e['lower']} are effectively tied."
    top = e["component_deltas"][0]
    diffs = [r for r in e["requirement_differences"] if r["advantage"] == e["higher"]][:2]
    detail = "; ".join(f"{r['requirement']}: {r[e['higher']]} vs {r[e['lower']]}" for r in diffs)
    return (f"{e['higher']} is ahead by {e['score_gap']:g} points, mostly from {top['component']} "
            f"({top['points']:+g})." + (f" Key differences - {detail}." if detail else ""))
