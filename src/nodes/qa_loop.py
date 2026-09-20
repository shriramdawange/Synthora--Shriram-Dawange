"""Node 7: QA Loop - answer questions using RAG with retrieved chunks."""

import json
from src.state import AgentState, QAExchange
from src.utils.llm_client import invoke_llm
from src.utils.embeddings import retrieve_chunks


QA_SYSTEM = """You are a helpful research paper assistant. Answer the user's question using the retrieved text chunks from the paper below. Synthesize information across chunks to provide a complete answer.

Retrieved paper text:
{chunks}

Rules:
- Use the information above to answer the question
- Synthesize across multiple chunks when needed
- Be specific and cite details from the paper
- If the information is truly not in the chunks, then say so briefly
- Format your answer as a clear, helpful response"""

QA_USER = """Question: {question}"""


def qa_node(state: AgentState) -> dict:
    user_input = state.get("user_input", "")
    conversation_history = state.get("conversation_history", [])
    briefing = state.get("briefing")
    vector_store_path = state.get("vector_store_path")
    selected_paper = state.get("selected_paper", {})
    arxiv_id = selected_paper.get("arxiv_id", "unknown")

    if not briefing:
        return {"error": "No briefing available. Cannot answer questions."}

    question = _get_next_question(user_input, conversation_history)
    if question is None:
        return {}

    if not vector_store_path:
        chunks = []
    else:
        chunks = retrieve_chunks(vector_store_path, question, arxiv_id, top_k=5)
    chunks_text = "\n\n".join(
        [f"[Chunk {i+1}]: {c['text'][:800]}"
         for i, c in enumerate(chunks)]
    ) if chunks else "No relevant chunks found."

    try:
        answer = invoke_llm(
            QA_SYSTEM.format(chunks=chunks_text),
            QA_USER.format(question=question),
        )
    except Exception as e:
        answer = f"Error generating answer: {e}"

    sources = [c.get("section", "unknown") for c in chunks[:3]]

    turn = len(conversation_history) + 1
    exchange = QAExchange(
        turn=turn,
        user_question=question,
        grounded_answer=answer,
        sources=sources,
    )

    return {"conversation_history": conversation_history + [exchange]}


def _get_next_question(user_input: str, history: list) -> str | None:
    exit_commands = {"exit", "quit", "done", "q", "stop", "bye"}
    cleaned = user_input.strip().lower()
    if cleaned in exit_commands:
        return None
    if "ask a question" in cleaned:
        return None
    return user_input.strip()
