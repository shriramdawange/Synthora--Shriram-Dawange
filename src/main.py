"""CLI entry point for the arXiv Paper Digest Agent - Rich Interactive Version."""

import uuid
import json
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.columns import Columns
from rich.text import Text
from rich import box

from src.graph import build_graph
from src.state import AgentState
from src.nodes.qa_loop import qa_node

console = Console()


BANNER = """[bold cyan]
     _        ____  _     _     _                  _   
    / \\   ___|  _ \\(_)___| |__ | |__  _   _  __ _| |_ 
   / _ \\ / _ \\ | | | / __| '_ \\| '_ \\| | | |/ _` | __|
  / ___ \\  __/ |_| | \\__ \\ | | | |_) | |_| | (_| | |_ 
 /_/   \\_\\___|____/|_|___/_| |_|_.__/ \\__,_|\\__,_|\\__|
[/]
[dim]Offline AI Paper Digest Agent | Powered by Ollama + LangGraph[/]"""


def print_briefing(briefing) -> None:
    console.print()
    console.print(Panel(
        f"[bold]{briefing.title}[/]\n"
        f"[dim]Authors: {', '.join(briefing.authors[:3])}[/]\n"
        f"[dim]arXiv: {briefing.arxiv_id} | {briefing.published}[/]",
        title="[bold green]PAPER FOUND[/]",
        border_style="green",
        box=box.DOUBLE,
    ))

    console.print(Panel(briefing.summary, title="[bold]SUMMARY[/]", border_style="cyan"))

    if briefing.problem_statement:
        t = Table(show_header=False, box=None, padding=(0, 1))
        t.add_column(style="bold red")
        t.add_column()
        for p in briefing.problem_statement:
            t.add_row(">>", p)
        console.print(Panel(t, title="[bold red]PROBLEM[/]", border_style="red"))

    if briefing.method:
        t = Table(show_header=False, box=None, padding=(0, 1))
        t.add_column(style="bold yellow")
        t.add_column()
        for m in briefing.method:
            t.add_row(">>", m)
        console.print(Panel(t, title="[bold yellow]METHOD[/]", border_style="yellow"))

    if briefing.key_results:
        t = Table(show_header=False, box=None, padding=(0, 1))
        t.add_column(style="bold green")
        t.add_column()
        for r in briefing.key_results:
            t.add_row(">>", r)
        console.print(Panel(t, title="[bold green]RESULTS[/]", border_style="green"))

    if briefing.limitations:
        t = Table(show_header=False, box=None, padding=(0, 1))
        t.add_column(style="bold magenta")
        t.add_column()
        for l in briefing.limitations:
            t.add_row(">>", l)
        console.print(Panel(t, title="[bold magenta]LIMITATIONS[/]", border_style="magenta"))

    if briefing.suggested_questions:
        console.print("\n[bold cyan]SUGGESTED QUESTIONS:[/]")
        for q in briefing.suggested_questions:
            console.print(f"  [dim]>[/] {q}")

    console.print("=" * 60)


def print_authors(author_info: list) -> None:
    if not author_info:
        return
    console.print()
    for author in author_info:
        t = Table(show_header=False, box=box.ROUNDED, title=f"[bold]{author['name']}[/]")
        t.add_column(style="bold")
        t.add_column()
        t.add_row("Fields", ", ".join(author.get("fields", [])[:3]))
        t.add_row("Papers", str(author.get("paper_count", 0)))
        if author.get("recent_papers"):
            for p in author["recent_papers"][:3]:
                t.add_row("  ", f"[dim]{p['title'][:60]}[/]")
        console.print(t)


def print_recommendations(recs: list) -> None:
    if not recs:
        return
    console.print()
    console.print(Panel("[bold]PAPERS LIKE THIS[/]", border_style="cyan"))
    for i, r in enumerate(recs[:5], 1):
        console.print(f"  [bold cyan]{i}.[/] {r['title'][:70]}")
        console.print(f"     [dim]{r.get('arxiv_id', '')} | {r.get('published', '')}[/]")
        console.print(f"     [dim]{r.get('summary', '')[:100]}...[/]")
        console.print()


def print_comparison(papers: list, result: dict) -> None:
    if not papers or len(papers) < 2:
        return
    console.print()
    t = Table(title="[bold]PAPER COMPARISON[/]", box=box.DOUBLE_EDGE)
    t.add_column(papers[0]["title"][:30], style="cyan", ratio=1)
    t.add_column(papers[1]["title"][:30], style="yellow", ratio=1)

    t.add_row(f"arXiv: {papers[0]['arxiv_id']}", f"arXiv: {papers[1]['arxiv_id']}")
    t.add_row(f"Date: {papers[0]['published']}", f"Date: {papers[1]['published']}")

    if result:
        sims = result.get("similarities", [])
        diffs = result.get("differences", [])
        if sims:
            t.add_row("[bold]Similarities:[/]", "")
            for s in sims:
                t.add_row(f"  - {s}", "")
        if diffs:
            t.add_row("[bold]Differences:[/]", "")
            for d in diffs:
                t.add_row(f"  - {d}", "")
        rec = result.get("recommendation", "")
        if rec:
            t.add_row(f"[bold]Recommendation:[/]", rec)

    console.print(t)


def print_synthesis(synthesis: dict) -> None:
    if not synthesis:
        return
    console.print()
    console.print(Panel("[bold]MULTI-PAPER SYNTHESIS[/]", border_style="green", box=box.DOUBLE))

    if synthesis.get("common_themes"):
        console.print("[bold]Common Themes:[/]")
        for t in synthesis["common_themes"]:
            console.print(f"  >> {t}")

    if synthesis.get("evolution"):
        console.print(f"\n[bold]Field Evolution:[/]\n  {synthesis['evolution']}")

    if synthesis.get("key_findings"):
        console.print("\n[bold]Key Findings:[/]")
        for f in synthesis["key_findings"]:
            console.print(f"  >> {f}")

    if synthesis.get("open_questions"):
        console.print("\n[bold]Open Questions:[/]")
        for q in synthesis["open_questions"]:
            console.print(f"  >> {q}")

    if synthesis.get("future_directions"):
        console.print("\n[bold]Future Directions:[/]")
        for d in synthesis["future_directions"]:
            console.print(f"  >> {d}")


def print_qa(exchange) -> None:
    console.print()
    console.print(Panel(
        exchange.grounded_answer,
        title=f"[bold]ANSWER (Turn {exchange.turn})[/]",
        border_style="green",
    ))


def save_session(state: dict, filepath: str) -> None:
    serializable = {
        "user_input": state.get("user_input", ""),
        "query_type": state.get("query_type", ""),
        "arxiv_id": state.get("arxiv_id", ""),
        "selected_paper": state.get("selected_paper", {}),
        "conversation_history": [
            {
                "turn": ex.turn if hasattr(ex, "turn") else ex.get("turn", 0),
                "user_question": ex.user_question if hasattr(ex, "user_question") else ex.get("user_question", ""),
                "grounded_answer": ex.grounded_answer if hasattr(ex, "grounded_answer") else ex.get("grounded_answer", ""),
            }
            for ex in state.get("conversation_history", [])
        ],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)


def main():
    console.print(BANNER)
    console.print()

    graph = build_graph()

    console.print("[bold]COMMANDS:[/]")
    console.print("  [cyan]1706.03762[/]           - Analyze paper by ID")
    console.print("  [cyan]topic search query[/]   - Search by topic")
    console.print("  [cyan]compare ID1 ID2[/]      - Compare two papers")
    console.print("  [cyan]synthesize topic[/]     - Synthesize multiple papers")
    console.print("  [cyan]quit[/]                 - Exit")
    console.print()

    user_input = Prompt.ask("[bold cyan]Enter command[/]")

    if not user_input.strip():
        console.print("[red]No input provided.[/]")
        return

    parts = user_input.strip().split()
    command = parts[0].lower()

    if command == "quit" or command == "exit":
        console.print("[dim]Goodbye![/]")
        return

    initial_state: AgentState = {
        "user_input": user_input.strip(),
        "query_type": "",
        "arxiv_id": None,
        "compare_ids": [],
        "search_results": [],
        "selected_paper": None,
        "raw_pdf_text": "",
        "sections": {},
        "chunks": [],
        "vector_store_path": None,
        "briefing": None,
        "conversation_history": [],
        "author_info": [],
        "recommendations": [],
        "comparison_papers": [],
        "comparison_result": None,
        "synthesis": None,
        "error": None,
    }

    if command == "compare" and len(parts) >= 3:
        initial_state["query_type"] = "compare"
        initial_state["compare_ids"] = [parts[1], parts[2]]
    elif command == "synthesize":
        initial_state["query_type"] = "synthesize"
        initial_state["user_input"] = " ".join(parts[1:])
    elif len(parts) == 1 and parts[0].replace(".", "").isdigit():
        initial_state["query_type"] = "arxiv_id"
        initial_state["arxiv_id"] = parts[0]
    else:
        initial_state["query_type"] = "topic_search"

    with console.status("[bold green]Processing...", spinner="dots"):
        result = graph.invoke(initial_state)

    if result.get("error") and not result.get("briefing") and not result.get("comparison_result") and not result.get("synthesis"):
        console.print(f"\n[red]Error: {result['error']}[/]")
        return

    if result.get("comparison_result"):
        print_comparison(result.get("comparison_papers", []), result["comparison_result"])
    elif result.get("synthesis"):
        print_synthesis(result["synthesis"])
    else:
        if result.get("briefing"):
            print_briefing(result["briefing"])
        if result.get("author_info"):
            print_authors(result["author_info"])
        if result.get("recommendations"):
            print_recommendations(result["recommendations"])

    while True:
        question = Prompt.ask("\n[bold cyan]Ask about the paper (or 'quit')[/]")
        if not question or question.lower() in {"quit", "exit", "done", "q"}:
            break

        qa_state = dict(result)
        qa_state["user_input"] = question
        qa_result = qa_node(qa_state)
        if qa_result.get("conversation_history"):
            result["conversation_history"] = qa_result["conversation_history"]
            latest = result["conversation_history"][-1]
            print_qa(latest)

    session_id = uuid.uuid4().hex[:8]
    session_path = f"session_{session_id}.json"
    save_session(result, session_path)
    console.print(f"\n[dim]Session saved to {session_path}[/]")


if __name__ == "__main__":
    main()
