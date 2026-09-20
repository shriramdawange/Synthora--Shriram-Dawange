"""Node 3: Selection/Ranking - pick the best paper for topic searches."""

from src.state import AgentState
from src.utils.llm_client import invoke_llm


SELECTION_SYSTEM = """You are a research assistant. Given a user query and a list of arXiv paper titles+abstracts, pick the SINGLE most relevant paper. Return ONLY the arxiv_id (e.g. 2401.12345) and a 1-sentence reason."""

SELECTION_USER = """Query: {query}

Papers:
{papers}

Return ONLY: arxiv_id: <id> | reason: <reason>"""


def selection_ranking_node(state: AgentState) -> dict:
    search_results = state.get("search_results", [])

    if not search_results:
        return {"error": "No search results to rank."}

    if len(search_results) == 1:
        return {"selected_paper": search_results[0]}

    papers_text = ""
    for i, p in enumerate(search_results, 1):
        papers_text += f"{i}. [{p['arxiv_id']}] {p['title']}\n   {p['summary'][:200]}...\n\n"

    user_prompt = SELECTION_USER.format(query=state["user_input"], papers=papers_text)
    try:
        response = invoke_llm(SELECTION_SYSTEM, user_prompt)
        selected_id = ""
        for word in response.split():
            if "arxiv_id:" in word.lower() or "arxiv" in word.lower():
                continue
            if "." in word and any(c.isdigit() for c in word):
                selected_id = word.strip(",:")
                break

        for p in search_results:
            if p["arxiv_id"] in selected_id or selected_id in p["arxiv_id"]:
                return {"selected_paper": p}

        return {"selected_paper": search_results[0]}
    except Exception:
        return {"selected_paper": search_results[0]}
