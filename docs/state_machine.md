# State machine

![TalentMatch LangGraph](state_machine.png)

`state_machine.png` is rendered from the Remotion diagram (`video/src/components/StateMachine.tsx`,
still `StateMachineDiagram`). The Mermaid below is exported **from the compiled graph itself**
(`MatchingAgent().graph.get_graph().draw_mermaid()`), so it is the authoritative edge list.
Dotted arrows are conditional edges chosen by the router after `human_feedback`.

```mermaid
graph TD;
	__start__([START]):::first
	parse_jd(parse_jd)
	extract_requirements(extract_requirements)
	search_resumes(search_resumes<br/>Round 1: 100 to 10)
	rank_candidates(rank_candidates<br/>Rounds 2-3)
	generate_report(generate_report)
	human_feedback(human_feedback<br/>interrupt)
	refine_requirements(refine_requirements)
	compare_candidates(compare_candidates)
	explain_ranking(explain_ranking)
	interview_questions(interview_questions)
	candidate_report(candidate_report)
	chat_agent(chat_agent<br/>LLM + tools)
	__end__([END]):::last
	__start__ --> parse_jd;
	parse_jd --> extract_requirements;
	extract_requirements --> search_resumes;
	search_resumes --> rank_candidates;
	rank_candidates --> generate_report;
	generate_report --> human_feedback;
	human_feedback -.->|refine| refine_requirements;
	human_feedback -.->|compare| compare_candidates;
	human_feedback -.->|explain| explain_ranking;
	human_feedback -.->|questions| interview_questions;
	human_feedback -.->|detail| candidate_report;
	human_feedback -.->|chat| chat_agent;
	human_feedback -.->|report| generate_report;
	human_feedback -.->|new search| parse_jd;
	human_feedback -.->|done| __end__;
	refine_requirements -.->|changed| search_resumes;
	refine_requirements -.->|no change| human_feedback;
	compare_candidates --> human_feedback;
	explain_ranking --> human_feedback;
	interview_questions --> human_feedback;
	candidate_report --> human_feedback;
	chat_agent --> human_feedback;
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

The raw export is in `state_machine.mmd` (regenerate with
`python -c "from matching_agent import MatchingAgent; print(MatchingAgent().graph.get_graph().draw_mermaid())"`).

## Node responsibilities

| Node | Brief step | What it does |
|---|---|---|
| `parse_jd` | Parse JD | Loads a JD file through Milestone 1 `read_file`, or takes the chat text |
| `extract_requirements` | Extract Requirements | Must-have / nice-to-have / years (rule parser; LLM merge when configured) |
| `search_resumes` | Search Resumes | **Round 1**: RAG query + quick must-have screen over all 100 → top 10 |
| `rank_candidates` | Rank Candidates | **Round 2** per-requirement evidence scoring, **Round 3** verdicts; diff against the previous shortlist |
| `generate_report` | Generate Report | Shortlist + changes + borderline advice; full match report written to `output/reports/` |
| `human_feedback` | Human Feedback Loop | `interrupt()`; routes the reply (rules first, LLM for ambiguous text) |
| `refine_requirements` | (loop) | Applies "make X a must-have", "relax X to N years", "drop X", "prioritise X" |
| `compare_candidates` / `explain_ranking` / `interview_questions` / `candidate_report` | (loop) | The interactive features; each returns to `human_feedback` |
| `chat_agent` | (loop) | Open questions: the LLM calls file, RAG and matching tools in a loop (max 6 rounds) |
