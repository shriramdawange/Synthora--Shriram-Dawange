"""Node 4: Fetch & Parse PDF - download and extract text from paper."""

from src.state import AgentState
from src.utils.pdf_parser import fetch_and_parse_pdf


def fetch_parse_pdf_node(state: AgentState) -> dict:
    selected_paper = state.get("selected_paper")
    if not selected_paper:
        return {"error": "No paper selected for PDF download."}

    arxiv_id = selected_paper.get("arxiv_id", "")
    abstract = selected_paper.get("summary", "")

    raw_text, sections = fetch_and_parse_pdf(arxiv_id, abstract)

    if not raw_text or len(raw_text.strip()) < 50:
        return {
            "raw_pdf_text": abstract,
            "sections": {"abstract": abstract},
        }

    return {
        "raw_pdf_text": raw_text,
        "sections": sections if sections else {"abstract": abstract},
    }
