"""Offline tests: parsing, requirements, scoring, explainability, routing, the graph and the 6 flows.

No network or API key is needed; the LLM paths use a scripted fake chat model.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from langchain_core.messages import AIMessage
from langgraph.types import Command

import matching_tools as mt
from matching_agent import MatchingAgent, build_tools, mentioned_candidates, route_intent
from profiles import canonical_skill, find_skills, parse_resume
from rag_search import get_index, rag_search
from run_scenarios import SCENARIOS, run

FRONTEND_JD = open("job_descriptions/senior_frontend_react.txt", encoding="utf-8").read()


@pytest.fixture(scope="module")
def index():
    return get_index()


@pytest.fixture(scope="module")
def frontend(index):
    reqs = mt.extract_requirements(FRONTEND_JD)
    screen = mt.initial_screen(index, reqs)
    ranked = mt.rank(index, reqs, [k["candidate_id"] for k in screen["kept"]], {})
    return reqs, screen, ranked


def by_name(ranked, name):
    return next(a for a in ranked if a["name"] == name)


# --------------------------------------------------------------------------- profiles
def test_skill_taxonomy_aliases_and_guards():
    assert find_skills("ReactJS, React.js and react") == ["React"]
    assert "React" not in find_skills("Shipped React Native apps")
    assert "Java" not in find_skills("Strong JavaScript skills")
    assert canonical_skill("reactjs") == "React" and canonical_skill("k8s") == "Kubernetes"


def test_parse_resume_evidence_and_listed_only(index):
    jane = index.profiles["resume_jane_brooks"]
    assert jane.name == "Jane Brooks"
    assert jane.skill_years["React"] >= 4
    assert "TypeScript" in jane.listed_only and "TypeScript" not in jane.skill_years  # "learning TypeScript"
    sofia = index.profiles["resume_sofia_rossi"]
    assert sofia.skill_years["React"] == 1          # "started ... React ... in 2025" only counts from 2025
    assert sofia.skill_years["React Native"] == 6


def test_parse_handles_every_format(index):
    assert len(index.profiles) == 100
    assert {p.filepath.rsplit(".", 1)[1] for p in index.profiles.values()} == {"pdf", "docx", "txt"}
    assert all(p.roles for p in index.profiles.values())


def test_parse_resume_minimal_text():
    text = "ADA LOVELACE\nEngineer\n\nEXPERIENCE\n----------\nEngineer - Analytical Co (2020 - 2023)\n  * Built Python tools.\n"
    p = parse_resume(text, "ada", "x.txt")
    assert p.name == "Ada Lovelace" and p.total_years == 3 and p.skill_years["Python"] == 3


# --------------------------------------------------------------------------- RAG
def test_rag_search_alias_expansion(index):
    hits = index.search("reactjs graphql", top_k=5)
    assert hits and all("skill:react" in " ".join(__import__("rag_search").tokenize(h["text"])) or
                        "graphql" in h["text"].lower() for h in hits)
    res = rag_search("Kubernetes platform", 3)
    assert res["success"] and res["count"] == 3


def test_find_candidate_prefers_shortlist(index):
    assert index.find_candidate("John", prefer=["resume_john_carter"]) == "resume_john_carter"
    assert index.find_candidate("john doe") == "resume_john_doe"
    assert index.find_candidate("nobody-here") is None


# --------------------------------------------------------------------------- requirements
def test_extract_requirements_from_jd():
    reqs = mt.extract_requirements(FRONTEND_JD)
    must = {r["skill"]: r["min_years"] for r in reqs["must_have"]}
    nice = [r["skill"] for r in reqs["nice_to_have"]]
    assert must["React"] == 3 and "TypeScript" in must
    assert {"Next.js", "GraphQL", "AWS", "Jest or Cypress"} <= set(nice)
    assert reqs["min_total_years"] == 5 and reqs["seniority"] == "senior"


def test_extract_requirements_conversational():
    reqs = mt.extract_requirements("Find me candidates with React and 3+ years experience")
    assert reqs["must_have"] == [{"skill": "React", "min_years": 3.0, "weight": 1.0}]
    reqs = mt.extract_requirements("Python developers with Django, nice to have Kubernetes")
    assert [r["skill"] for r in reqs["nice_to_have"]] == ["Kubernetes"]


def test_any_of_group():
    reqs = mt.extract_requirements(open("job_descriptions/backend_python.txt", encoding="utf-8").read())
    group = next(r for r in reqs["must_have"] if r.get("any_of"))
    assert group["any_of"] == ["Django", "FastAPI"]


@pytest.mark.parametrize("instruction,check", [
    ("Make GraphQL a must-have", lambda r: any(x["skill"] == "GraphQL" for x in r["must_have"])),
    ("relax React to 2 years", lambda r: next(x for x in r["must_have"] if x["skill"] == "React")["min_years"] == 2),
    ("drop CSS", lambda r: all(x["skill"] != "CSS" for x in r["must_have"])),
    ("TypeScript is nice to have", lambda r: any(x["skill"] == "TypeScript" for x in r["nice_to_have"])),
    ("prioritise accessibility", lambda r: next(x for x in r["nice_to_have"] if x["skill"] == "Accessibility")["weight"] == 2),
    ("at least 7 years of experience", lambda r: r["min_total_years"] == 7),
])
def test_refine_requirements(instruction, check):
    reqs = mt.extract_requirements(FRONTEND_JD)
    new, changes = mt.refine_requirements(reqs, instruction)
    assert changes and check(new)
    assert reqs == mt.extract_requirements(FRONTEND_JD)  # original untouched


def test_refine_without_a_change():
    _, changes = mt.refine_requirements(mt.extract_requirements(FRONTEND_JD), "hello there")
    assert changes == []


# --------------------------------------------------------------------------- scoring rounds
def test_round1_screens_100_to_10(frontend):
    _, screen, _ = frontend
    assert screen["screened"] == 100 and len(screen["kept"]) == 10
    assert screen["cut_reasons"]["no React"] > 50


def test_round2_and_3(frontend):
    _, _, ranked = frontend
    assert ranked[0]["name"] == "John Carter" and ranked[0]["recommendation"]["verdict"] == "Strong Hire"
    jane = by_name(ranked, "Jane Brooks")
    assert jane["recommendation"]["verdict"] == "Borderline"
    assert any("TypeScript" in s for s in jane["recommendation"]["suggestions"])
    ts = next(b for b in jane["breakdown"] if b["requirement"] == "TypeScript")
    assert ts["status"] == "listed"
    assert [a["rank"] for a in ranked] == list(range(1, 11))
    assert all(ranked[i]["score"] >= ranked[i + 1]["score"] for i in range(9))


def test_missing_must_have_cannot_be_hire(index):
    reqs = mt.extract_requirements("Must have: React, Angular")
    ken = mt.analyze_candidate(index, "resume_ken_watanabe", reqs)
    assert ken["knockouts"] == ["React"]
    assert mt.recommend(ken)["verdict"] == "No Hire"


def test_explain_pair(frontend):
    _, _, ranked = frontend
    e = mt.explain_pair(by_name(ranked, "Jane Brooks"), by_name(ranked, "John Carter"))
    assert e["higher"] == "John Carter" and e["score_gap"] > 10
    assert any(d["requirement"] == "TypeScript" for d in e["requirement_differences"])
    assert round(sum(d["points"] for d in e["component_deltas"]), 0) == round(e["score_gap"], 0)


def test_compare_and_questions(index, frontend):
    reqs, _, ranked = frontend
    cmp = mt.compare_candidates(ranked[:3])
    assert cmp["overall_winner"] == "John Carter" and len(cmp["rows"]) == len(ranked[0]["breakdown"])
    qs = mt.generate_interview_questions(by_name(ranked, "Jane Brooks"), reqs, index)
    types = [q["type"] for q in qs["questions"]]
    assert "gap probe" in types and "depth" in types
    assert any("TypeScript" in q["question"] for q in qs["questions"] if q["type"] == "gap probe")


def test_ranking_changes_explain_moves(index, frontend):
    reqs, _, ranked = frontend
    new_reqs, _ = mt.refine_requirements(reqs, "Make GraphQL a must-have")
    screen = mt.initial_screen(index, new_reqs)
    new = mt.rank(index, new_reqs, [k["candidate_id"] for k in screen["kept"]], {})
    changes = mt.ranking_changes(ranked, new)
    alex = next(c for c in changes if c["name"] == "Alex Chen")
    assert alex["to"] is None or alex["to"] > alex["from"]
    if alex["to"]:
        assert "GraphQL (must-have) missing" in alex["reason"]


# --------------------------------------------------------------------------- routing
@pytest.mark.parametrize("text,intent", [
    ("Find me candidates with React and 3+ years experience", "new_search"),
    ("Compare the top 3 matches side by side", "compare"),
    ("Why did John rank higher than Jane?", "explain"),
    ("Make GraphQL a must-have", "refine"),
    ("Actually, relax React to 2 years", "refine"),
    ("Interview questions for Jane", "questions"),
    ("Tell me about Sofia", "detail"),
    ("Which candidates know Kubernetes?", "chat"),
    ("show me the shortlist again", "report"),
    ("done", "end"),
])
def test_route_intent(index, frontend, text, intent):
    _, _, ranked = frontend
    out = route_intent(text, {"shortlist": ranked, "requirements": frontend[0]}, index, llm=None)
    assert out["intent"] == intent


def test_first_names_resolve_against_shortlist(index, frontend):
    ids = [a["candidate_id"] for a in frontend[2]]
    assert mentioned_candidates("Why did John rank higher than Jane?", index, ids) == [
        "resume_john_carter", "resume_jane_brooks"]
    assert route_intent("compare the top 3", {"shortlist": frontend[2]}, index, None)["top_n"] == 3


# --------------------------------------------------------------------------- graph
def test_graph_structure():
    g = MatchingAgent().graph.get_graph()
    nodes = set(g.nodes)
    for n in ("parse_jd", "extract_requirements", "search_resumes", "rank_candidates", "generate_report",
              "human_feedback", "refine_requirements", "compare_candidates", "explain_ranking",
              "interview_questions", "candidate_report", "chat_agent"):
        assert n in nodes
    edges = {(e.source, e.target) for e in g.edges}
    assert ("__start__", "parse_jd") in edges and ("human_feedback", "__end__") in edges
    assert ("refine_requirements", "search_resumes") in edges


def test_interrupt_pauses_and_resumes():
    agent = MatchingAgent()
    cfg = {"configurable": {"thread_id": "t-int"}}
    out = agent.graph.invoke({"pending": {"text": FRONTEND_JD}}, cfg)
    assert "__interrupt__" in out
    assert agent.graph.get_state(cfg).next == ("human_feedback",)
    agent.graph.invoke(Command(resume="Compare the top 2"), cfg)
    state = agent.graph.get_state(cfg).values
    assert state["response"].startswith("## Head-to-head") and state["turn"] == 1
    agent.graph.invoke(Command(resume="done"), cfg)
    assert agent.graph.get_state(cfg).next == ()


def test_report_written(tmp_path):
    agent = MatchingAgent()
    r = agent.start("job_descriptions/senior_frontend_react.txt", "t-report")
    path = r["state"]["report_path"]
    text = open(path, encoding="utf-8").read()
    assert "John Carter" in text and "Improvement suggestions" in text


# --------------------------------------------------------------------------- the six conversation flows
@pytest.fixture(scope="module")
def flows():
    agent = MatchingAgent()
    return {s["name"]: run(agent, s) for s in SCENARIOS}


def test_at_least_five_flows(flows):
    assert len(flows) >= 5 and all(len(f["turns"]) >= 2 for f in flows.values())


def test_flow_jd_to_shortlist(flows):
    t = flows["01_jd_to_shortlist"]["turns"]
    assert t[0]["nodes"] == ["parse_jd", "extract_requirements", "search_resumes", "rank_candidates", "generate_report"]
    assert t[0]["shortlist"][0]["name"] == "John Carter"
    assert t[1]["nodes"] == ["human_feedback", "generate_report"]


def test_flow_compare(flows):
    t = flows["02_natural_language_compare"]["turns"][1]
    assert "compare_candidates" in t["nodes"] and "Head-to-head" in t["response"]


def test_flow_explain(flows):
    t = flows["03_explain_ranking"]["turns"]
    assert "Why John Carter" in t[1]["response"] and "Jane Brooks" in t[1]["response"]
    assert "Improvement suggestions" in t[2]["response"]


def test_flow_refinement_reranks_and_explains(flows):
    t = flows["04_iterative_refinement"]["turns"]
    assert t[1]["nodes"][:3] == ["human_feedback", "refine_requirements", "search_resumes"]
    assert t[1]["ranking_changes"] and "### What changed" in t[1]["response"]
    musts = [r["skill"] for r in t[1]["requirements"]["must_have"]]
    assert "GraphQL" in musts
    assert "GraphQL" not in [r["skill"] for r in t[2]["requirements"]["must_have"]]


def test_flow_backend_questions(flows):
    t = flows["05_backend_interview_prep"]["turns"]
    assert t[0]["shortlist"][0]["name"] == "Nina Petrova"
    assert "Screening questions for John Doe" in t[2]["response"]


def test_flow_borderline_and_end(flows):
    t = flows["06_borderline_ml"]["turns"]
    assert "Borderline" in t[1]["response"] and "Improvement suggestions" in t[1]["response"]
    assert t[-1]["done"] is True


# --------------------------------------------------------------------------- LLM paths (scripted fake model)
class FakeLLM:
    """Minimal stand-in for a LangChain chat model: structured output, plain text, tool calls."""

    def __init__(self, tool_script: list[AIMessage] | None = None, structured: Any = None):
        self.tool_script = list(tool_script or [])
        self.structured = structured
        self.calls = 0

    def with_structured_output(self, schema):
        parent = self

        class _S:
            def invoke(self, _msgs):
                if parent.structured is None:
                    raise RuntimeError("no structured output scripted")
                return parent.structured(schema)
        return _S()

    def bind_tools(self, tools):
        parent = self

        class _Bound:
            def invoke(self, _msgs):
                return parent.tool_script.pop(0) if parent.tool_script else AIMessage("(no script)")
        return _Bound()

    def invoke(self, _msgs):
        self.calls += 1
        return AIMessage("LLM summary grounded in facts.")


def test_llm_chat_agent_tool_loop():
    script = [AIMessage("", tool_calls=[{"name": "search_candidates", "args": {"keyword": "AWS"}, "id": "c1"}]),
              AIMessage("John Carter and Yusuf Yilmaz have AWS experience.")]
    agent = MatchingAgent(llm=FakeLLM(tool_script=script))
    agent.start("job_descriptions/senior_frontend_react.txt", "t-llm")
    r = agent.send("Which shortlisted candidates have AWS experience?", "t-llm")
    assert r["response"] == "John Carter and Yusuf Yilmaz have AWS experience."
    assert "search_candidates(keyword='AWS')" in r["reasoning"][-1]


def test_llm_failure_falls_back_to_rules():
    agent = MatchingAgent(llm=FakeLLM())  # structured output raises -> rule-based parser
    r = agent.start("job_descriptions/senior_frontend_react.txt", "t-fallback")
    assert "rule-based parser (LLM failed" in r["reasoning"][1]
    assert r["state"]["shortlist"][0]["name"] == "John Carter"


def test_tools_exposed_to_llm(index):
    names = {t.name for t in build_tools(index, {"shortlist": [], "requirements": mt.extract_requirements(FRONTEND_JD)})}
    assert {"read_file", "list_files", "search_in_file", "write_file", "rag_search", "extract_requirements",
            "compare_candidates", "generate_interview_questions"} <= names


def test_write_tool_is_limited_to_output(index):
    tools = {t.name: t for t in build_tools(index, {"shortlist": []})}
    assert "error" in tools["write_file"].invoke({"filepath": "resumes/x.txt", "content": "x"})
    assert json.dumps(tools["compare_candidates"].invoke({"candidate_ids": ["John Carter"]})).count("error") == 1
