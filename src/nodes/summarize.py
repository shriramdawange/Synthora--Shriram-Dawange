"""Node 6: Summarize - generate structured briefing, works with small LLMs."""

import json
import re
from src.state import AgentState, PaperBriefing
from src.utils.llm_client import invoke_llm


def _ask(question: str, context: str) -> str:
    resp = invoke_llm("Answer concisely in one sentence.", f"Context: {context}\n\nQuestion: {question}")
    return resp.strip()


def _ask_list(question: str, context: str) -> list[str]:
    resp = invoke_llm(
        "Return ONLY a bullet list, one item per line. No numbers, no dashes, no extra text.",
        f"Context: {context}\n\nQuestion: {question}"
    )
    items = []
    for line in resp.strip().split("\n"):
        line = re.sub(r'^[\-\*\d\.]+\s*', '', line).strip()
        if line:
            items.append(line)
    return items[:5]


def summarize_node(state: AgentState) -> dict:
    selected_paper = state.get("selected_paper", {})
    raw_text = state.get("raw_pdf_text", "")

    if not selected_paper:
        return {"error": "No paper to summarize."}

    title = selected_paper.get("title", "Unknown")
    authors = selected_paper.get("authors", [])
    arxiv_id = selected_paper.get("arxiv_id", "")
    published = selected_paper.get("published", "")
    abstract = selected_paper.get("summary", "")

    context = raw_text[:6000] if raw_text else abstract
    if not context:
        context = abstract

    try:
        summary = _ask(
            f"What is this paper about? Summarize in 2-3 sentences.",
            context
        )

        problems = _ask_list(
            "What are the 2-4 specific problems or challenges this paper addresses?",
            context
        )

        methods = _ask_list(
            "What are the 2-4 key methods or techniques proposed in this paper?",
            context
        )

        results = _ask_list(
            "What are the 2-4 main results or findings?",
            context
        )

        limitations = _ask_list(
            "What are 2-4 limitations or gaps mentioned or apparent?",
            context
        )

        questions = _ask_list(
            "What are 2-3 insightful questions a reader might ask?",
            context
        )

        briefing = PaperBriefing(
            title=title,
            authors=authors,
            arxiv_id=arxiv_id,
            published=published,
            summary=summary or abstract,
            problem_statement=problems or [],
            method=methods or [],
            key_results=results or [],
            limitations=limitations or [],
            suggested_questions=questions or [
                "What are the main contributions?",
                "How does this compare to prior work?",
            ],
        )
        return {"briefing": briefing}

    except Exception as e:
        briefing = PaperBriefing(
            title=title,
            authors=authors,
            arxiv_id=arxiv_id,
            published=published,
            summary=abstract,
        )
        return {"briefing": briefing, "error": f"Summarize failed: {e}"}
