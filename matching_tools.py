"""Matching tools: requirement extraction, multi-round scoring, comparison, interview questions.

Every function here is deterministic and works offline. The agent (``matching_agent.py``)
optionally lets an LLM improve two steps (requirement extraction and refinement parsing) and
write the prose, but the *numbers* always come from this module, so a ranking can be
reproduced and explained line by line.

Scoring model (round 2, out of 100)::

    55  must-have coverage   per skill: evidenced years / required years (listed-only = weak credit)
     5  depth                 evidenced years *beyond* the bar on must-haves (rewards seniority on ties)
    20  nice-to-have          evidenced = full credit, listed-only = half
    15  experience fit        total years / required total years (capped at 1)
     5  retrieval relevance   normalised BM25 score from the RAG screen

Recommendation (round 3): Strong Hire / Hire / Borderline / No Hire from the score *and* the
must-have status, so a high scorer who is missing a must-have can never be a Strong Hire.
"""

from __future__ import annotations

import copy
import re
from typing import Any

from profiles import SKILL_ALIASES, CandidateProfile, canonical_skill, find_skills
from rag_search import ResumeIndex

def _yrs(y: float) -> str:
    return f"{y:g} yr" + ("" if y == 1 else "s")


WEIGHTS = {"must": 55.0, "depth": 5.0, "nice": 20.0, "experience": 15.0, "relevance": 5.0}
SHORTLIST_SIZE = 10
KNOCKOUT_PENALTY = 15.0  # per must-have with no trace at all on the resume

_YEARS = r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)"
_MUST_HDR = re.compile(r"(must[- ]?have|required|requirements|qualifications|you have|what you.?ll need)", re.I)
_NICE_HDR = re.compile(r"(nice[- ]?to[- ]?have|preferred|bonus|plus|good to have|desirable)", re.I)
_OTHER_HDR = re.compile(r"(about|responsibilit|what you.?ll do|benefits|perks|who we are|the role)", re.I)


# --------------------------------------------------------------------------- #
# Requirements
# --------------------------------------------------------------------------- #

def empty_requirements() -> dict[str, Any]:
    return {"title": "", "must_have": [], "nice_to_have": [], "min_total_years": 0, "seniority": None}


def _req(skill: str, min_years: float = 0, weight: float = 1.0) -> dict[str, Any]:
    return {"skill": skill, "min_years": min_years, "weight": weight}


def _add(lst: list[dict[str, Any]], skill: str, min_years: float = 0) -> None:
    for r in lst:
        if r["skill"] == skill:
            r["min_years"] = max(r["min_years"], min_years)
            return
    lst.append(_req(skill, min_years))


def _add_group(lst: list[dict[str, Any]], alts: list[str], min_years: float = 0) -> None:
    label = " or ".join(alts)
    if not any(r["skill"] == label for r in lst):
        lst.append({**_req(label, min_years), "any_of": list(alts)})


def req_skills(r: dict[str, Any]) -> list[str]:
    """The concrete skills a requirement accepts (one, or several for an any-of group)."""
    return list(r.get("any_of") or [r["skill"]])


def extract_requirements(jd: str) -> dict[str, Any]:
    """Parse a job description *or* a one-line request into must-have vs nice-to-have skills.

    Handles markdown JDs with "Must have / Nice to have" sections and conversational asks such as
    "Find me candidates with React and 3+ years experience" (everything is a must-have there;
    "nice to have X" / "bonus: X" phrases are still honoured).
    """
    reqs = empty_requirements()
    lines = _unwrap(jd)
    for l in lines[:3]:
        m = re.match(r"^(?:#+\s*|(?:role|title|position)\s*:\s*)(.+)$", l, re.I)
        if m:
            reqs["title"] = m.group(1).strip()
            break
    low = jd.lower()
    reqs["seniority"] = ("senior" if re.search(r"\b(senior|staff|lead|principal|sr\.?)\b", low)
                         else "junior" if re.search(r"\b(junior|entry[- ]level|graduate|jr\.?)\b", low)
                         else "mid" if re.search(r"\bmid[- ]level\b", low) else None)

    def header_kind(line: str) -> str | None:
        is_bullet = bool(re.match(r"^([-*\u2022]|\d+[.)])\s", line))
        is_header = not is_bullet and len(line) < 60 and (
            line.startswith("#") or line.endswith(":") or line.isupper() or re.match(r"^\*\*.+\*\*:?$", line))
        if not is_header:
            return None
        return ("nice" if _NICE_HDR.search(line) else "must" if _MUST_HDR.search(line)
                else "ignore" if _OTHER_HDR.search(line) else "keep")

    # "Must have: React, Angular" on one line = a header plus its content.
    expanded: list[str] = []
    for line in lines:
        m_inline = re.match(r"^\W*((?:must[- ]?have|required|requirements|nice[- ]?to[- ]?have|preferred|bonus)"
                            r"[\w ]{0,15}):\s*(\S.*)$", line, re.I)
        expanded += [m_inline.group(1) + ":", m_inline.group(2)] if m_inline else [line]
    lines = expanded

    has_sections = any(header_kind(l) in ("must", "nice") for l in lines)
    mode = "must" if not has_sections else "ignore"
    for line in lines:
        kind = header_kind(line)
        if has_sections and kind is not None:
            mode = mode if kind == "keep" else kind
            continue
        if mode == "ignore":
            # still catch "N+ years of experience" phrasing in an About/Role section
            _maybe_total_years(line, reqs, require_no_skill=True)
            continue
        _parse_line(line, mode, reqs)

    # nice skills that also appear as must stay must
    musts = {s for r in reqs["must_have"] for s in req_skills(r)}
    reqs["nice_to_have"] = [r for r in reqs["nice_to_have"] if not set(req_skills(r)) <= musts]
    if not reqs["title"]:
        reqs["title"] = ("Candidates with " + ", ".join(
            r["skill"] + (f" {r['min_years']:g}+ yrs" if r["min_years"] else "") for r in reqs["must_have"][:3])
            if reqs["must_have"] else "Open role")
    return reqs


def _unwrap(text: str) -> list[str]:
    """Join hard-wrapped prose lines; keep headings and bullets as their own lines."""
    out: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            out.append("")
            continue
        starts_block = re.match(r"^([-*\u2022]|\d+[.)]|#|\*\*)", line)
        if out and out[-1] and not starts_block and not out[-1].endswith(":") and not re.match(r"^(#|\*\*.*\*\*:?$)", out[-1]):
            out[-1] += " " + line
        else:
            out.append(line)
    return [l for l in out if l]


def _maybe_total_years(line: str, reqs: dict[str, Any], require_no_skill: bool = False) -> bool:
    m = re.search(_YEARS + r"(?:\s+of)?(?:\s+(?:professional|industry|relevant|total|hands-on))?\s+(?:experience|exp\b)", line, re.I)
    if m and (not require_no_skill or not find_skills(line)):
        reqs["min_total_years"] = max(reqs["min_total_years"], float(m.group(1)))
        return True
    return False


def _parse_line(line: str, mode: str, reqs: dict[str, Any]) -> None:
    # Inline "nice to have: X, Y" / "bonus X" inside a conversational request.
    inline_nice = re.split(r"\b(?:nice[- ]to[- ]have|bonus(?: points)?(?: for)?|ideally|preferably|plus)\b:?", line, flags=re.I)
    segments = [(inline_nice[0], mode)] + [(s, "nice") for s in inline_nice[1:]]
    for text, seg_mode in segments:
        skills = find_skills(text)
        target = reqs["must_have"] if seg_mode == "must" else reqs["nice_to_have"]
        years_for: dict[str, float] = {}
        # "3+ years of React" / "React (3+ years)" / "React with 3+ years"
        for m in re.finditer(_YEARS + r"\s+(?:of\s+|with\s+|in\s+|using\s+)?(?:professional\s+|hands-on\s+)?([A-Za-z][\w.+#/ ]{0,25})", text, re.I):
            after = find_skills(m.group(2))
            if after:
                years_for[after[0]] = float(m.group(1))
        for m in re.finditer(r"([A-Za-z][\w.+#/ ]{0,25}?)\s*[\(,:-]?\s*" + _YEARS, text, re.I):
            before = find_skills(m.group(1))
            if before and before[-1] not in years_for:
                years_for[before[-1]] = float(m.group(2))
        total_hit = _maybe_total_years(text, reqs)
        if total_hit and not years_for and len(skills) == 1 and seg_mode == "must":
            # "React and 3+ years experience": a recruiter means 3 years *of React*.
            years_for[skills[0]] = reqs["min_total_years"]
        grouped: set[str] = set()
        for piece in re.split(r",|;|\band\b", text):
            alts = find_skills(piece)
            if len(alts) >= 2 and re.search(r"\bor\b|\s/\s|\beither\b", piece, re.I):
                _add_group(target, alts, max((years_for.get(a, 0) for a in alts), default=0))
                grouped.update(alts)
        for s in skills:
            if s not in grouped:
                _add(target, s, years_for.get(s, 0))


# --------------------------------------------------------------------------- #
# Refinement: "make GraphQL a must-have", "relax React to 2 years", "drop Jest"
# --------------------------------------------------------------------------- #

def _skills_in(text: str) -> list[str]:
    found = find_skills(text)
    # prefer the specific one when both "React Native" and "React" matched the same words
    if "React Native" in found and "React" in found and not re.search(r"react(?!\s*native)", text, re.I):
        found.remove("React")
    return found


def refine_requirements(reqs: dict[str, Any], instruction: str) -> tuple[dict[str, Any], list[str]]:
    """Apply a natural-language change to the requirements. Returns (new_requirements, change_log)."""
    new = copy.deepcopy(reqs)
    changes: list[str] = []
    text = instruction.strip()
    low = text.lower()

    def find(lst: list[dict[str, Any]], skill: str) -> dict[str, Any] | None:
        return next((r for r in lst if r["skill"] == skill or skill in r.get("any_of", [])), None)

    def remove(skill: str) -> None:
        for key in ("must_have", "nice_to_have"):
            kept = []
            for r in new[key]:
                if r["skill"] == skill:
                    continue
                if skill in r.get("any_of", []):
                    rest = [a for a in r["any_of"] if a != skill]
                    r = {**_req(rest[0], r["min_years"], r["weight"])} if len(rest) == 1 else \
                        {**r, "skill": " or ".join(rest), "any_of": rest}
                kept.append(r)
            new[key] = kept

    clauses = [c for c in re.split(r"[;\n]|,?\s+\band\b\s+(?=(?:make|drop|remove|add|require|relax|ignore|set|also|treat|move|lower|raise|prioriti))|\.\s+", text, flags=re.I) if c.strip()]
    for clause in clauses:
        cl = clause.lower()
        skills = _skills_in(clause)
        years = re.search(_YEARS, clause, re.I)
        total_years = re.search(_YEARS + r"(?:\s+of)?\s+(?:total|overall|professional)?\s*(?:experience|exp)\b", clause, re.I)

        if re.search(r"\b(drop|remove|ignore|don'?t (?:care|need)|no longer|not (?:needed|required)|forget)\b", cl):
            for s in skills:
                remove(s)
                changes.append(f"Removed {s} from the requirements")
            continue
        if re.search(r"\b(nice[- ]to[- ]have|optional|bonus|preferred|not a must)\b", cl):
            for s in skills:
                cur = find(new["must_have"], s) or find(new["nice_to_have"], s)
                remove(s)
                new["nice_to_have"].append(_req(s, 0, cur["weight"] if cur else 1.0))
                changes.append(f"{s} is now nice-to-have")
            continue
        if re.search(r"\b(prioriti[sz]e|weight|more important|emphasi[sz]e|focus on)\b", cl):
            for s in skills:
                cur = find(new["must_have"], s) or find(new["nice_to_have"], s)
                if cur is None:
                    cur = _req(s)
                    new["nice_to_have"].append(cur)
                cur["weight"] = 2.0
                changes.append(f"{s} now carries double weight")
            continue
        if total_years and not skills:
            new["min_total_years"] = float(total_years.group(1))
            changes.append(f"Minimum total experience set to {total_years.group(1)}+ years")
            continue
        if skills and (years or re.search(r"\b(must|require|need|mandatory|essential|add|make|also|want)\b", cl)):
            for s in skills:
                min_y = float(years.group(1)) if years and len(skills) == 1 else 0.0
                existing = find(new["must_have"], s)
                if existing:
                    if years and len(skills) == 1:
                        old = existing["min_years"]
                        existing["min_years"] = min_y
                        changes.append(f"{s} requirement changed from {old:g}+ to {min_y:g}+ years")
                else:
                    was_nice = find(new["nice_to_have"], s)
                    remove(s)
                    new["must_have"].append(_req(s, min_y, was_nice["weight"] if was_nice else 1.0))
                    changes.append(f"{s} is now a must-have" + (f" ({min_y:g}+ years)" if min_y else "")
                                   + (" (was nice-to-have)" if was_nice else ""))
            continue
    if re.search(r"\b(senior)\b", low) and new.get("seniority") != "senior" and "not senior" not in low:
        if re.search(r"\b(make it|should be|must be|only)\b.*\bsenior\b", low):
            new["seniority"] = "senior"
            changes.append("Seniority set to senior")
    return new, changes


def describe_requirements(reqs: dict[str, Any]) -> str:
    def fmt(r: dict[str, Any]) -> str:
        s = r["skill"] + (f" ({r['min_years']:g}+ yrs)" if r.get("min_years") else "")
        return s + (" x2" if r.get("weight", 1) > 1 else "")
    parts = [f"**{reqs.get('title') or 'Role'}**"]
    parts.append("Must-have: " + (", ".join(fmt(r) for r in reqs["must_have"]) or "none"))
    parts.append("Nice-to-have: " + (", ".join(fmt(r) for r in reqs["nice_to_have"]) or "none"))
    if reqs.get("min_total_years"):
        parts.append(f"Experience: {reqs['min_total_years']:g}+ years total")
    return "\n".join(parts)


def requirements_query(reqs: dict[str, Any]) -> str:
    """The retrieval query used for the RAG screen (must-haves repeated to weight them)."""
    must = [s for r in reqs["must_have"] for s in req_skills(r)]
    nice = [s for r in reqs["nice_to_have"] for s in req_skills(r)]
    title = reqs.get("title") or ""
    return " ".join(must * 2 + nice + ([title] if title and not title.startswith("Candidates with") else []))


# --------------------------------------------------------------------------- #
# Round 1: initial screen (whole pool -> top 10)
# --------------------------------------------------------------------------- #

def initial_screen(index: ResumeIndex, reqs: dict[str, Any], keep: int = SHORTLIST_SIZE) -> dict[str, Any]:
    """Cheap pass over every resume: must-have presence + years fit + RAG relevance."""
    retrieved = {h["candidate_id"]: h["score"] for h in index.search_candidates(requirements_query(reqs), top_k=len(index.profiles))}
    top_rel = max(retrieved.values(), default=1.0) or 1.0
    rows = []
    reasons: dict[str, int] = {}
    for cid, p in index.profiles.items():
        must = reqs["must_have"]
        present = [r for r in must if any(s in p.skill_years or s in p.skills for s in req_skills(r))]
        coverage = (len(present) / len(must)) if must else 1.0
        exp_fit = min(1.0, p.total_years / reqs["min_total_years"]) if reqs.get("min_total_years") else 1.0
        rel = retrieved.get(cid, 0.0) / top_rel
        quick = 100 * (0.65 * coverage + 0.15 * exp_fit + 0.20 * rel)
        rows.append({"candidate_id": cid, "name": p.name, "quick_score": round(quick, 1), "coverage": coverage})
        for r in must:
            if not any(s in p.skills for s in req_skills(r)):
                reasons[f"no {r['skill']}"] = reasons.get(f"no {r['skill']}", 0) + 1
    rows.sort(key=lambda r: (-r["quick_score"], r["name"]))
    return {
        "screened": len(rows),
        "kept": rows[:keep],
        "cut_reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1])),
        "cutoff_score": rows[keep - 1]["quick_score"] if len(rows) >= keep else None,
    }


# --------------------------------------------------------------------------- #
# Round 2: deep analysis of one candidate
# --------------------------------------------------------------------------- #

def _credit(p: CandidateProfile, r: dict[str, Any], must: bool) -> tuple[float, str, str]:
    if r.get("any_of"):
        best = max((_credit(p, {**r, "skill": a, "any_of": None}, must) + (a,) for a in r["any_of"]),
                   key=lambda t: t[0])
        credit, status, detail, alt = best
        return credit, status, (f"{alt}: {detail}" if status != "missing" else "none of " + r["skill"] + " found")
    skill, need = r["skill"], float(r.get("min_years") or 0)
    years = p.skill_years.get(skill, 0.0)
    listed = skill in p.skills or skill in p.listed_only
    if years > 0:
        if need and years < need:
            return min(1.0, years / need), "partial", f"{years:g} of {need:g} required years evidenced"
        return 1.0, "met", f"{_yrs(years)} evidenced" + (f" (needs {need:g})" if need else "")
    if listed:
        return (0.25 if must else 0.5), "listed", "listed on resume but no work experience shows it"
    return 0.0, "missing", "not found on resume"


def _evidence(index: ResumeIndex, p: CandidateProfile, cid: str, r: dict[str, Any]) -> list[str]:
    alts = sorted(req_skills(r), key=lambda s: -p.skill_years.get(s, 0))
    for s in alts:
        quotes = index.evidence(cid, s, top_k=1)
        if quotes:
            return quotes
    return []


def analyze_candidate(index: ResumeIndex, cid: str, reqs: dict[str, Any], relevance: float = 0.0) -> dict[str, Any]:
    """Round 2: per-requirement evidence, component scores, strengths and gaps."""
    p = index.profiles[cid]
    breakdown = []
    comp = {"must": 1.0, "depth": 0.0, "nice": 1.0, "experience": 1.0, "relevance": relevance}
    for kind, lst in (("must", reqs["must_have"]), ("nice", reqs["nice_to_have"])):
        total_w = sum(r.get("weight", 1.0) for r in lst)
        acc = 0.0
        for r in lst:
            credit, status, detail = _credit(p, r, kind == "must")
            acc += credit * r.get("weight", 1.0)
            breakdown.append({"requirement": r["skill"], "_skills": req_skills(r), "kind": kind, "min_years": r.get("min_years", 0),
                              "status": status, "credit": round(credit, 2), "detail": detail,
                              "evidence": _evidence(index, p, cid, r) if status in ("met", "partial") else []})
        comp[kind] = (acc / total_w) if total_w else 1.0
    if reqs.get("min_total_years"):
        comp["experience"] = min(1.0, p.total_years / reqs["min_total_years"])
    depth = []
    for r in reqs["must_have"]:
        y = max(p.skill_years.get(s, 0.0) for s in req_skills(r))
        need = float(r.get("min_years") or 0)
        depth.append(min(1.0, (y - need) / max(need, 3.0)) if y > need else 0.0)
    comp["depth"] = sum(depth) / len(depth) if depth else 0.0
    knockouts = [b["requirement"] for b in breakdown if b["kind"] == "must" and b["status"] == "missing"]
    score = max(0.0, sum(WEIGHTS[k] * comp[k] for k in WEIGHTS) - KNOCKOUT_PENALTY * len(knockouts))

    must_rows = [b for b in breakdown if b["kind"] == "must"]
    strengths, gaps = [], []
    for b in must_rows:
        y = max(p.skill_years.get(s, 0) for s in b.get("_skills", [b["requirement"]]))
        if b["status"] == "met" and b["requirement"] in ("HTML", "CSS", "JavaScript", "SQL", "REST") and len(must_rows) > 2:
            continue  # fundamentals implied by the main stack are not worth calling out as strengths
        if b["status"] == "met":
            extra = f", {y - b['min_years']:g} above the bar" if b["min_years"] and y > b["min_years"] else ""
            strengths.append(f"{b['requirement']}: {_yrs(y)} evidenced{extra}")
        else:
            gaps.append(f"{b['requirement']} (must-have): {b['detail']}")
    for b in breakdown:
        if b["kind"] == "nice":
            (strengths if b["status"] == "met" else gaps).append(
                f"{b['requirement']} (nice-to-have): {b['detail']}" if b["status"] != "met" else f"Bonus: {b['requirement']}")
    if reqs.get("min_total_years") and p.total_years < reqs["min_total_years"]:
        gaps.append(f"Experience: {p.total_years:g} of {reqs['min_total_years']:g} required years")
    elif p.total_years >= 6:
        strengths.append(f"{p.total_years:g} years total experience")
    if p.leadership:
        strengths.append("Leadership/mentoring evidence")
    if p.certifications:
        strengths.append("Certified: " + "; ".join(p.certifications[:2]))

    return {
        "candidate_id": cid, "name": p.name, "headline": p.headline, "filepath": p.filepath,
        "total_years": p.total_years, "score": round(score, 1),
        "components": {k: round(v, 3) for k, v in comp.items()}, "knockouts": knockouts,
        "breakdown": breakdown, "strengths": strengths, "gaps": gaps,
    }


# --------------------------------------------------------------------------- #
# Round 3: recommendation + improvement suggestions
# --------------------------------------------------------------------------- #

def recommend(analysis: dict[str, Any]) -> dict[str, Any]:
    must = [b for b in analysis["breakdown"] if b["kind"] == "must"]
    met = sum(b["status"] == "met" for b in must)
    unmet = [b for b in must if b["status"] != "met"]
    hard_missing = [b for b in must if b["status"] == "missing"]
    s = analysis["score"]
    if not unmet and s >= 85:
        verdict, why = "Strong Hire", "meets every must-have with room to spare"
    elif not unmet and s >= 70:
        verdict, why = "Hire", "meets every must-have"
    elif len(unmet) <= 1 and not hard_missing and s >= 60:
        verdict, why = "Borderline", f"close: {unmet[0]['requirement']} is {unmet[0]['detail']}" if unmet else "close on overall fit"
    elif not unmet and s >= 60:
        verdict, why = "Borderline", "meets must-haves but weak on the rest of the profile"
    else:
        verdict = "No Hire"
        why = (f"missing must-have: {', '.join(b['requirement'] for b in hard_missing)}" if hard_missing
               else f"{len(unmet)} must-haves not fully met")
    suggestions = improvement_suggestions(analysis) if verdict in ("Borderline", "No Hire") else []
    return {"verdict": verdict, "rationale": f"{verdict}: {why} (score {s:g}/100, {met}/{len(must)} must-haves met)",
            "suggestions": suggestions}


def improvement_suggestions(analysis: dict[str, Any]) -> list[str]:
    out = []
    for b in analysis["breakdown"]:
        if b["kind"] != "must" or b["status"] == "met":
            continue
        skill = b["requirement"]
        if b["status"] == "listed":
            out.append(f"{skill}: listed but never shown in a role. Ask for a {skill} code sample or a short "
                       f"take-home; if it holds up they clear this bar.")
        elif b["status"] == "partial":
            out.append(f"{skill}: {b['detail']}. Probe adjacent experience in the screen; consider a mid-level "
                       f"offer or revisit in 6-12 months.")
        else:
            out.append(f"{skill}: no evidence. The candidate would need hands-on {skill} work "
                       f"(a shipped project or role) to be competitive for this position.")
    if not out and analysis["components"]["nice"] < 0.5:
        out.append("Meets the bar on must-haves; strengthening the nice-to-haves "
                   + ", ".join(b["requirement"] for b in analysis["breakdown"] if b["kind"] == "nice" and b["status"] != "met")
                   + " would move them up.")
    return out


def rank(index: ResumeIndex, reqs: dict[str, Any], candidate_ids: list[str], relevance: dict[str, float]) -> list[dict[str, Any]]:
    analyses = []
    for cid in candidate_ids:
        a = analyze_candidate(index, cid, reqs, relevance.get(cid, 0.0))
        a["recommendation"] = recommend(a)
        analyses.append(a)
    analyses.sort(key=lambda a: (-a["score"], a["name"]))
    for i, a in enumerate(analyses, 1):
        a["rank"] = i
    return analyses


# --------------------------------------------------------------------------- #
# Explainability: comparisons, "why A > B", ranking diffs
# --------------------------------------------------------------------------- #

_COMPONENT_LABEL = {"must": "must-have coverage", "depth": "depth beyond the bar", "nice": "nice-to-haves", "experience": "experience fit",
                    "relevance": "resume relevance"}


def explain_pair(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Why ``a`` scored higher (or lower) than ``b``: component deltas + per-requirement differences."""
    hi, lo = (a, b) if a["score"] >= b["score"] else (b, a)
    deltas = []
    for k, w in WEIGHTS.items():
        d = (hi["components"][k] - lo["components"][k]) * w
        if abs(d) >= 0.5:
            deltas.append({"component": _COMPONENT_LABEL[k], "points": round(d, 1)})
    ko = len(lo.get("knockouts", [])) - len(hi.get("knockouts", []))
    if ko:
        deltas.append({"component": "missing must-have penalty", "points": round(ko * KNOCKOUT_PENALTY, 1)})
    deltas.sort(key=lambda d: -abs(d["points"]))
    req_diffs = []
    lo_rows = {r["requirement"]: r for r in lo["breakdown"]}
    for r in hi["breakdown"]:
        o = lo_rows.get(r["requirement"])
        if o and r["credit"] != o["credit"]:
            better = hi["name"] if r["credit"] > o["credit"] else lo["name"]
            req_diffs.append({"requirement": r["requirement"], "kind": r["kind"], hi["name"]: r["detail"],
                              lo["name"]: o["detail"], "advantage": better})
    return {"higher": hi["name"], "lower": lo["name"], "score_gap": round(hi["score"] - lo["score"], 1),
            "component_deltas": deltas, "requirement_differences": req_diffs}


def compare_candidates(analyses: list[dict[str, Any]]) -> dict[str, Any]:
    """Head-to-head matrix: one row per requirement, one column per candidate, plus a winner."""
    names = [a["name"] for a in analyses]
    rows = []
    reqs = [(b["requirement"], b["kind"]) for b in analyses[0]["breakdown"]] if analyses else []
    for req, kind in reqs:
        cells = {}
        best, best_credit = [], -1.0
        for a in analyses:
            row = next(b for b in a["breakdown"] if b["requirement"] == req)
            cells[a["name"]] = {"status": row["status"], "detail": row["detail"]}
            if row["credit"] > best_credit:
                best, best_credit = [a["name"]], row["credit"]
            elif row["credit"] == best_credit:
                best.append(a["name"])
        rows.append({"requirement": req, "kind": kind, "cells": cells,
                     "winner": "tie" if len(best) == len(analyses) else " & ".join(best)})
    summary = [{"name": a["name"], "rank": a.get("rank"), "score": a["score"], "years": a["total_years"],
                "verdict": a.get("recommendation", {}).get("verdict")} for a in analyses]
    return {"candidates": names, "summary": summary, "rows": rows,
            "overall_winner": max(analyses, key=lambda a: a["score"])["name"] if analyses else None}


def ranking_changes(old: list[dict[str, Any]], new: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Who moved and why, after the requirements changed."""
    old_by = {a["candidate_id"]: a for a in old}
    new_by = {a["candidate_id"]: a for a in new}
    changes = []
    for a in new:
        o = old_by.get(a["candidate_id"])
        if o is None:
            changes.append({"name": a["name"], "from": None, "to": a["rank"], "score_from": None,
                            "score_to": a["score"], "reason": "newly entered the shortlist"})
            continue
        if o["rank"] == a["rank"] and abs(o["score"] - a["score"]) < 0.1:
            continue
        reason_bits = []
        for k, w in WEIGHTS.items():
            d = (a["components"][k] - o["components"][k]) * w
            if abs(d) >= 1:
                reason_bits.append(f"{_COMPONENT_LABEL[k]} {'+' if d > 0 else ''}{d:.1f}")
        before = {(x["requirement"], x["kind"]): x for x in o["breakdown"]}
        changed_reqs = []
        for r in a["breakdown"]:
            x = before.get((r["requirement"], r["kind"]))
            if x is None or x["credit"] != r["credit"] or x["min_years"] != r["min_years"]:
                label = "must-have" if r["kind"] == "must" else "nice-to-have"
                changed_reqs.append(f"{r['requirement']} ({label}) {r['status']}")
        # surface the requirements that hurt first, then the ones that helped
        changed_reqs.sort(key=lambda s: not s.endswith(("missing", "listed", "partial")))
        if changed_reqs:
            reason_bits.insert(0, ", ".join(changed_reqs[:2]))
        changes.append({"name": a["name"], "from": o["rank"], "to": a["rank"], "score_from": o["score"],
                        "score_to": a["score"], "reason": "; ".join(reason_bits) or "relative shift"})
    for o in old:
        if o["candidate_id"] not in new_by:
            changes.append({"name": o["name"], "from": o["rank"], "to": None, "score_from": o["score"],
                            "score_to": None, "reason": "dropped out of the shortlist"})
    changes.sort(key=lambda c: (c["to"] is None, c["to"] or 99))
    return changes


# --------------------------------------------------------------------------- #
# Interview questions
# --------------------------------------------------------------------------- #

def generate_interview_questions(analysis: dict[str, Any], reqs: dict[str, Any], index: ResumeIndex) -> dict[str, Any]:
    """Screening questions tailored to the candidate's evidence and gaps."""
    p = index.profiles[analysis["candidate_id"]]
    qs: list[dict[str, str]] = []
    met = [b for b in analysis["breakdown"] if b["kind"] == "must" and b["status"] == "met"]
    basics = ("HTML", "CSS", "JavaScript", "SQL", "REST")
    met.sort(key=lambda b: (-(b["min_years"] or 0), b["requirement"] in basics))
    picked = [b for b in met if b["requirement"] not in basics][:3]
    picked += [b for b in met if b["requirement"] in basics][: max(0, 2 - len(picked))]
    depth_ok = {b["requirement"] for b in picked}
    for b in analysis["breakdown"]:
        skill = b["requirement"]
        if b["kind"] == "must" and b["status"] == "met" and skill not in depth_ok:
            continue
        if b["kind"] == "must" and b["status"] == "met":
            quote = b["evidence"][0] if b["evidence"] else ""
            ctx = f'You wrote: "{quote[:110]}". ' if quote else ""
            qs.append({"area": skill, "type": "depth",
                       "question": f"{ctx}Walk me through the hardest {skill} problem in that work: what broke, "
                                   f"how you diagnosed it, and what you would do differently now."})
        elif b["kind"] == "must":
            qs.append({"area": skill, "type": "gap probe",
                       "question": f"This role needs {skill}"
                                   + (f" ({b['min_years']:g}+ years)" if b["min_years"] else "")
                                   + f". Your resume shows: {b['detail']}. Tell me about any {skill} work that "
                                     f"isn't on the resume, and how you would ramp up in your first month."})
    nice_missing = [b["requirement"] for b in analysis["breakdown"] if b["kind"] == "nice" and b["status"] != "met"]
    if nice_missing:
        qs.append({"area": ", ".join(nice_missing[:3]), "type": "learning agility",
                   "question": f"We also use {', '.join(nice_missing[:3])}. Which of these have you touched, and how "
                               f"do you usually pick up a new tool on a deadline?"})
    if p.leadership:
        qs.append({"area": "leadership", "type": "behavioural",
                   "question": "Describe a time you mentored someone or led a technical decision the team disagreed "
                               "with. How did you get to alignment?"})
    if p.roles:
        r0 = p.roles[0]
        qs.append({"area": "motivation", "type": "behavioural",
                   "question": f"Why are you looking to move on from {r0['company']}, and what would make this "
                               f"{reqs.get('title') or 'role'} a step up for you?"})
    return {"candidate_id": analysis["candidate_id"], "name": analysis["name"], "questions": qs}


def known_skill_names() -> list[str]:
    return sorted(SKILL_ALIASES) + ["Go"]


__all__ = [
    "extract_requirements", "refine_requirements", "describe_requirements", "initial_screen",
    "analyze_candidate", "recommend", "rank", "explain_pair", "compare_candidates", "ranking_changes",
    "generate_interview_questions", "canonical_skill", "known_skill_names", "requirements_query",
]
