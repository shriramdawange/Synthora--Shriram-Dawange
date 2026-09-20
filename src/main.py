"""CLI entry point for the arXiv Paper Digest Agent."""

import uuid
import json
import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_graph
from src.state import AgentState, PaperBriefing
from src.nodes.qa_loop import qa_node


BANNER = """
============================================================
  arXiv Paper Digest Agent
  Powered by LangGraph + Groq (free tier)
============================================================"""


def print_briefing(briefing) -> None:
    print("\n" + "=" * 60)
    print(f"  {briefing.title}")
    authors = ", ".join(briefing.authors[:3])
    if len(briefing.authors) > 3:
        authors += " et al."
    print(f"  Authors: {authors}")
    print(f"  arXiv: {briefing.arxiv_id} | {briefing.published}")
    print("=" * 60)

    print(f"\nSUMMARY\n{briefing.summary}")

    if briefing.problem_statement:
        print("\nPROBLEM")
        for item in briefing.problem_statement:
            print(f"  - {item}")

    if briefing.method:
        print("\nMETHOD")
        for item in briefing.method:
            print(f"  - {item}")

    if briefing.key_results:
        print("\nRESULTS")
        for item in briefing.key_results:
            print(f"  - {item}")

    if briefing.limitations:
        print("\nLIMITATIONS")
        for item in briefing.limitations:
            print(f"  - {item}")

    if briefing.suggested_questions:
        print("\nSUGGESTED QUESTIONS")
        for item in briefing.suggested_questions:
            print(f"  - {item}")

    print("=" * 60 + "\n")


def print_qa(exchange) -> None:
    print(f"\nAnswer (Source: {', '.join(exchange.sources)}):")
    print(f"{exchange.grounded_answer}\n")


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
                "sources": ex.sources if hasattr(ex, "sources") else ex.get("sources", []),
            }
            for ex in state.get("conversation_history", [])
        ],
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2, ensure_ascii=False)


def main():
    print(BANNER)
    graph = build_graph()

    user_input = input("\nEnter a research topic or arXiv paper ID:\n> ").strip()
    if not user_input:
        print("No input provided. Exiting.")
        return

    initial_state: AgentState = {
        "user_input": user_input,
        "query_type": "",
        "arxiv_id": None,
        "search_results": [],
        "selected_paper": None,
        "raw_pdf_text": "",
        "sections": {},
        "chunks": [],
        "vector_store_path": None,
        "briefing": None,
        "conversation_history": [],
        "error": None,
    }

    print("\nProcessing...")
    result = graph.invoke(initial_state)

    if result.get("error") and not result.get("briefing"):
        print(f"\nError: {result['error']}")
        return

    if result.get("briefing"):
        print_briefing(result["briefing"])

    while True:
        question = input("Ask a question about the paper (or 'exit' to quit):\n> ").strip()
        if not question or question.lower() in {"exit", "quit", "q", "done"}:
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
    print(f"\nSession saved to {session_path}")


if __name__ == "__main__":
    main()
