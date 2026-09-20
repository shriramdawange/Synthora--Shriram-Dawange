"""Node 5: Chunk & Embed - create vector embeddings in ChromaDB."""

from src.state import AgentState
from src.utils.embeddings import chunk_text, build_vector_store


def chunk_embed_node(state: AgentState) -> dict:
    raw_text = state.get("raw_pdf_text", "")
    selected_paper = state.get("selected_paper", {})
    arxiv_id = selected_paper.get("arxiv_id", "unknown")

    if not raw_text or len(raw_text.strip()) < 50:
        return {
            "chunks": [],
            "vector_store_path": None,
            "error": "Insufficient text to chunk.",
        }

    chunks = chunk_text(raw_text)
    if not chunks:
        return {"chunks": [], "vector_store_path": None, "error": "No chunks created."}

    store_path = build_vector_store(chunks, arxiv_id)

    return {
        "chunks": chunks,
        "vector_store_path": store_path,
    }
