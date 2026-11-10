"""Export real agent output for the Remotion demo video (video/src/data/demo.json).

Everything the video shows (reasoning lines, shortlist, comparison matrix, score deltas, ranking
moves, interview questions) is produced here by running the actual agent offline, so the video
reflects what the code really does. Re-run after changing the agent:  python export_video_data.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import matching_tools as mt
from matching_agent import MatchingAgent

OUT = Path(__file__).resolve().parent / "video" / "src" / "data" / "demo.json"


def slim(a: dict) -> dict:
    return {"rank": a["rank"], "name": a["name"], "score": a["score"], "verdict": a["recommendation"]["verdict"],
            "headline": a["headline"], "years": a["total_years"],
            "strength": (a["strengths"] or ["-"])[0], "gap": (a["gaps"] or ["-"])[0]}


def strip_tag(line: str) -> tuple[str, str]:
    node, _, text = line.partition("] ")
    return node.lstrip("["), text


def main() -> int:
    agent = MatchingAgent(llm=None)
    idx = agent.index

    # Flow 1: JD -> shortlist
    r1 = agent.start("job_descriptions/senior_frontend_react.txt", "v1")
    s1 = r1["state"]
    reqs = s1["requirements"]
    counts: dict[str, int] = {}
    for a in s1["shortlist"]:
        counts[a["recommendation"]["verdict"]] = counts.get(a["recommendation"]["verdict"], 0) + 1

    # Flow 2: natural-language query + compare top 3
    r2 = agent.start("Find me candidates with React and 3+ years experience", "v2")
    r2c = agent.send("Compare the top 3 matches side by side", "v1")  # on the Senior Frontend shortlist
    cmp = mt.compare_candidates(s1["shortlist"][:3])
    nl_top = [slim(a) for a in r2["state"]["shortlist"][:5]]
    nl_must = [r["skill"] + (f" {r['min_years']:g}+ yrs" if r["min_years"] else "")
               for r in r2["state"]["requirements"]["must_have"]]

    # Flow 3: explain John vs Jane
    r3 = agent.send("Why did John rank higher than Jane?", "v1")
    by = {a["name"]: a for a in s1["shortlist"]}
    explain = mt.explain_pair(by["John Carter"], by["Jane Brooks"])

    # Flow 4: refinement
    before = [slim(a) for a in s1["shortlist"]]
    r4 = agent.send("Make GraphQL a must-have and relax React to 2 years", "v1")
    s4 = r4["state"]
    after = [slim(a) for a in s4["shortlist"]]

    # Flow 5: interview questions + borderline
    r5 = agent.send("Interview questions for Jane", "v1")
    qs = mt.generate_interview_questions(by["Jane Brooks"], reqs, idx)
    ml = agent.start("job_descriptions/ml_engineer.txt", "v6")
    vera = next(a for a in ml["state"]["shortlist"] if a["name"] == "Vera Takahashi")

    tests = subprocess.run([sys.executable, "-m", "pytest", "-q", "-o", "addopts=--basetemp=.pytest_tmp"], capture_output=True, text=True)
    summary_line = [l for l in tests.stdout.splitlines() if " passed" in l or " failed" in l][-1:]

    data = {
        "pool": {"resumes": len(idx.profiles), "chunks": len(idx.chunks),
                 "formats": {ext: sum(p.filepath.endswith(ext) for p in idx.profiles.values()) for ext in ("pdf", "docx", "txt")}},
        "requirements": {"title": reqs["title"],
                         "must": [r["skill"] + (f" {r['min_years']:g}+ yrs" if r["min_years"] else "") for r in reqs["must_have"]],
                         "nice": [r["skill"] for r in reqs["nice_to_have"]], "minYears": reqs["min_total_years"]},
        "flow1": {"user": "job_descriptions/senior_frontend_react.txt",
                  "steps": [dict(zip(("node", "text"), strip_tag(l))) for l in r1["reasoning"]],
                  "screen": {"screened": s1["screen"]["screened"], "kept": len(s1["screen"]["kept"]),
                             "cutoff": s1["screen"]["cutoff_score"], "cutReasons": s1["screen"]["cut_reasons"]},
                  "verdicts": counts, "shortlist": before},
        "flow2": {"user": "Find me candidates with React and 3+ years experience",
                  "steps": [dict(zip(("node", "text"), strip_tag(l))) for l in r2["reasoning"]],
                  "nlTop": nl_top, "nlMust": nl_must,
                  "followUp": "Compare the top 3 matches side by side",
                  "followSteps": [dict(zip(("node", "text"), strip_tag(l))) for l in r2c["reasoning"]],
                  "compare": {"names": cmp["candidates"], "summary": cmp["summary"],
                              "rows": [{"req": r["requirement"], "kind": r["kind"], "winner": r["winner"],
                                        "cells": [r["cells"][n] for n in cmp["candidates"]]} for r in cmp["rows"]]}},
        "flow3": {"user": "Why did John rank higher than Jane?",
                  "steps": [dict(zip(("node", "text"), strip_tag(l))) for l in r3["reasoning"]],
                  "explain": explain, "scores": {"John Carter": by["John Carter"]["score"], "Jane Brooks": by["Jane Brooks"]["score"]}},
        "flow4": {"user": "Make GraphQL a must-have and relax React to 2 years",
                  "steps": [dict(zip(("node", "text"), strip_tag(l))) for l in r4["reasoning"]],
                  "before": before, "after": after,
                  "changes": s4["ranking_changes"],
                  "mustAfter": [r["skill"] + (f" {r['min_years']:g}+ yrs" if r["min_years"] else "") for r in s4["requirements"]["must_have"]]},
        "flow5": {"user": "Interview questions for Jane",
                  "steps": [dict(zip(("node", "text"), strip_tag(l))) for l in r5["reasoning"]],
                  "questions": qs["questions"],
                  "borderline": {"name": vera["name"], "score": vera["score"], "verdict": vera["recommendation"]["verdict"],
                                 "rationale": vera["recommendation"]["rationale"],
                                 "suggestions": vera["recommendation"]["suggestions"],
                                 "breakdown": [{"req": b["requirement"], "kind": b["kind"], "status": b["status"],
                                                "detail": b["detail"]} for b in vera["breakdown"]]}},
        "tests": {"summary": summary_line[0].strip() if summary_line else "", "flows": 6},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, indent=1, default=str), encoding="utf-8")
    print(f"wrote {OUT.relative_to(Path.cwd()) if OUT.is_relative_to(Path.cwd()) else OUT}  | tests: {data['tests']['summary']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
