"""Node 1: Query Understanding - classify input as arXiv ID or topic search."""

import re
from src.state import AgentState


ARXIV_ID_PATTERN = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")


def query_understanding_node(state: AgentState) -> dict:
    user_input = state["user_input"].strip()

    if ARXIV_ID_PATTERN.match(user_input):
        return {"query_type": "arxiv_id", "arxiv_id": user_input}

    if "arxiv.org" in user_input:
        match = re.search(r"(\d{4}\.\d{4,5})", user_input)
        if match:
            return {"query_type": "arxiv_id", "arxiv_id": match.group(1)}

    if not user_input:
        return {"query_type": "invalid", "error": "Empty input."}

    return {"query_type": "topic_search", "arxiv_id": None}
