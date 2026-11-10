"""Run the scripted conversation flows and save transcripts.

    python run_scenarios.py                 # offline (deterministic) - what the tests check
    python run_scenarios.py --provider ollama --model ornith-1.5:9b   # same flows with an LLM

Writes ``output/scenarios/<name>.md`` (readable transcript: user turn, agent reasoning trace,
agent answer) and ``output/scenarios/scenarios.json`` (consumed by the Remotion demo video).
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import llm as llm_mod
from matching_agent import MatchingAgent

SCENARIOS: list[dict] = [
    {"name": "01_jd_to_shortlist",
     "title": "JD file -> 3-round screen -> report",
     "goal": "Parse a JD, extract must/nice requirements, screen 100 resumes to 10, recommend hire/no-hire.",
     "turns": ["job_descriptions/senior_frontend_react.txt", "Show me the shortlist again"]},
    {"name": "02_natural_language_compare",
     "title": "Natural-language search + side-by-side comparison",
     "goal": "Start from a one-line ask, then compare the top 3 head to head.",
     "turns": ["Find me candidates with React and 3+ years experience", "Compare the top 3 matches side by side"]},
    {"name": "03_explain_ranking",
     "title": "Why did John rank higher than Jane?",
     "goal": "Explain a ranking with point deltas and requirement-level evidence.",
     "turns": ["job_descriptions/senior_frontend_react.txt", "Why did John rank higher than Jane?",
               "Tell me about Jane"]},
    {"name": "04_iterative_refinement",
     "title": "Change requirements mid-conversation, re-rank, explain the moves",
     "goal": "Make GraphQL a must-have, relax React years, then undo GraphQL; the agent re-screens each time.",
     "turns": ["job_descriptions/senior_frontend_react.txt",
               "Make GraphQL a must-have and relax React to 2 years",
               "Actually GraphQL is nice to have again"]},
    {"name": "05_backend_interview_prep",
     "title": "Backend role: candidate deep dive + interview questions",
     "goal": "Different JD; drill into a candidate and generate tailored screening questions.",
     "turns": ["job_descriptions/backend_python.txt", "Tell me about Nina Petrova",
               "Interview questions for John Doe"]},
    {"name": "06_borderline_ml",
     "title": "Borderline candidates and improvement suggestions",
     "goal": "ML role: inspect a borderline candidate, compare them with the leader, end the session.",
     "turns": ["job_descriptions/ml_engineer.txt", "Tell me about Vera Takahashi",
               "Compare Omar Haddad and Vera Takahashi", "done"]},
]


def run(agent: MatchingAgent, scenario: dict) -> dict:
    thread = scenario["name"]
    turns = []
    for i, text in enumerate(scenario["turns"]):
        t0 = time.perf_counter()
        result = agent.start(text, thread) if i == 0 else agent.send(text, thread)
        state = result["state"]
        turns.append({
            "user": text,
            "nodes": result["nodes"],
            "reasoning": result["reasoning"],
            "response": result["response"],
            "seconds": round(time.perf_counter() - t0, 2),
            "shortlist": [{"rank": a["rank"], "name": a["name"], "score": a["score"],
                           "verdict": a["recommendation"]["verdict"]} for a in state.get("shortlist", [])],
            "ranking_changes": state.get("ranking_changes", []) if "refine_requirements" in result["nodes"] else [],
            "requirements": state.get("requirements"),
            "done": result["done"],
        })
    return {**scenario, "turns": turns}


def to_markdown(s: dict) -> str:
    out = [f"# {s['title']}", "", f"_{s['goal']}_", ""]
    for i, t in enumerate(s["turns"], 1):
        out += [f"## Turn {i}", "", f"**User:** {t['user']}", "", "**Agent reasoning (graph nodes):**", "```"]
        out += t["reasoning"] or ["(none)"]
        out += ["```", "", "**Agent:**", "", t["response"], ""]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider")
    ap.add_argument("--model")
    ap.add_argument("--out", default="output/scenarios")
    args = ap.parse_args(argv)
    model = llm_mod.create_chat_model(args.provider, args.model) if args.provider else None
    agent = MatchingAgent(llm=model)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    results = []
    for s in SCENARIOS:
        r = run(agent, s)
        results.append(r)
        (out / f"{s['name']}.md").write_text(to_markdown(r), encoding="utf-8")
        print(f"{s['name']:<32} {len(r['turns'])} turns  "
              f"nodes: {sum(len(t['nodes']) for t in r['turns'])}  ({sum(t['seconds'] for t in r['turns']):.1f}s)")
    (out / "scenarios.json").write_text(json.dumps({"llm": llm_mod.describe(model), "scenarios": results},
                                                   indent=1, default=str), encoding="utf-8")
    print(f"transcripts -> {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
