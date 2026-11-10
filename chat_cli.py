"""Terminal chat interface for the TalentMatch LangGraph agent.

    python chat_cli.py                                   # interactive; type a JD path or a request
    python chat_cli.py --jd job_descriptions/senior_frontend_react.txt
    python chat_cli.py --provider ollama --model llama3.1:8b
    python chat_cli.py --offline                         # no LLM: deterministic reasoning only

Every graph node that runs is printed live with the agent's reasoning, then the answer.
Commands: /state (show requirements + shortlist), /graph (print the mermaid diagram), /new, /exit.
"""

from __future__ import annotations

import argparse
import sys
import uuid

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule

from langchain_core.messages import HumanMessage
from langgraph.types import Command

import llm as llm_mod
from matching_agent import MatchingAgent
from matching_tools import describe_requirements

NODE_STYLE = {
    "parse_jd": "cyan", "extract_requirements": "cyan", "search_resumes": "magenta", "rank_candidates": "magenta",
    "generate_report": "green", "human_feedback": "yellow", "refine_requirements": "yellow",
    "compare_candidates": "blue", "explain_ranking": "blue", "interview_questions": "blue",
    "candidate_report": "blue", "chat_agent": "red",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="TalentMatch resume-screening agent (LangGraph)")
    ap.add_argument("--jd", help="job description file to start with (e.g. job_descriptions/senior_frontend_react.txt)")
    ap.add_argument("--provider", help="anthropic | openai | gemini | openrouter | ollama | none")
    ap.add_argument("--model", help="model name for the provider")
    ap.add_argument("--offline", action="store_true", help="run without an LLM")
    ap.add_argument("--resumes", default="resumes", help="resume folder (default: resumes)")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    console = Console()
    try:
        model = None if args.offline else llm_mod.create_chat_model(args.provider, args.model)
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]LLM setup failed:[/red] {exc}\nFalling back to offline mode.")
        model = None
    with console.status("Indexing resumes..."):
        agent = MatchingAgent(llm=model, resume_dir=args.resumes)
    console.print(Panel.fit(
        f"[bold]TalentMatch[/bold] - LangGraph resume-matching agent\n"
        f"{len(agent.index.profiles)} resumes indexed ({len(agent.index.chunks)} RAG chunks) | LLM: {llm_mod.describe(model)}\n"
        "Start with a JD path or a request like [italic]Find me candidates with React and 3+ years experience[/italic].\n"
        "Commands: /state  /graph  /new  /exit", border_style="cyan"))

    thread = uuid.uuid4().hex[:8]
    cfg = {"configurable": {"thread_id": thread}}

    def on_step(node: str, update: dict) -> None:
        for note in update.get("reasoning", []) or []:
            text = note.split("] ", 1)[-1] if note.startswith("[") else note
            console.print(f"  [{NODE_STYLE.get(node, 'white')}]* {node:<21}[/] {text}")

    def run(inp) -> bool:
        console.print(Rule("agent reasoning", style="grey50"))
        result = agent.stream(inp, thread, on_step)
        console.print(Rule(style="grey50"))
        console.print(Markdown(result["response"]))
        return result["done"]

    pending = args.jd
    while True:
        if pending is None:
            try:
                pending = console.input("\n[bold cyan]you>[/bold cyan] ").strip()
            except (EOFError, KeyboardInterrupt):
                console.print()
                return 0
        text, pending = pending, None
        if not text:
            continue
        if text in ("/exit", "/quit"):
            return 0
        if text == "/graph":
            console.print(agent.graph.get_graph().draw_mermaid())
            continue
        if text == "/new":
            thread = uuid.uuid4().hex[:8]
            cfg = {"configurable": {"thread_id": thread}}
            console.print("[grey50]New conversation.[/grey50]")
            continue
        snap = agent.graph.get_state(cfg)
        if text == "/state":
            v = snap.values or {}
            if v.get("requirements"):
                console.print(Markdown(describe_requirements(v["requirements"])))
                for a in v.get("shortlist", []):
                    console.print(f"  #{a['rank']:<2} {a['name']:<18} {a['score']:>5}  {a['recommendation']['verdict']}")
                console.print(f"  turns: {v.get('turn', 0)}  | requirement versions: {len(v.get('requirements_history', []))}")
            else:
                console.print("[grey50]No search yet.[/grey50]")
            continue
        if snap.next:  # paused at human_feedback -> resume with the user's message
            done = run(Command(resume=text))
        else:          # fresh conversation (or the last one ended): start from START -> parse_jd
            done = run({"messages": [HumanMessage(text)], "pending": {"text": text}})
        if done:
            console.print("[grey50]Conversation ended. Type a new request to start again, or /exit.[/grey50]")


if __name__ == "__main__":
    raise SystemExit(main())
