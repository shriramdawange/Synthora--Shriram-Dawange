"""Node 2: arXiv Retrieval - fetch papers from arXiv API."""

import arxiv
from src.state import AgentState


MAX_RESULTS = 10


def arxiv_retrieval_node(state: AgentState) -> dict:
    query_type = state.get("query_type", "invalid")
    arxiv_id = state.get("arxiv_id")
    user_input = state.get("user_input", "")

    if query_type == "invalid":
        return {"error": "Invalid query type. Please provide a topic or arXiv ID."}

    if query_type == "arxiv_id" and arxiv_id:
        client = arxiv.Client()
        search = arxiv.Search(id_list=[arxiv_id])
        results = list(client.results(search))
        if not results:
            return {"error": f"No paper found for ID: {arxiv_id}"}
        paper = results[0]
        return {
            "search_results": [_paper_to_dict(paper)],
            "selected_paper": _paper_to_dict(paper),
        }

    if query_type == "topic_search":
        client = arxiv.Client()
        search = arxiv.Search(
            query=user_input,
            max_results=MAX_RESULTS,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = list(client.results(search))
        if not results:
            return {
                "search_results": [],
                "error": f"No papers found for '{user_input}'. Try different keywords.",
            }
        papers = [_paper_to_dict(p) for p in results]
        return {"search_results": papers}

    return {"error": "Unexpected query state."}


def _paper_to_dict(paper: arxiv.Result) -> dict:
    return {
        "title": paper.title,
        "authors": [a.name for a in paper.authors],
        "arxiv_id": paper.entry_id.split("/")[-1].split("v")[0],
        "summary": paper.summary,
        "published": paper.published.strftime("%Y-%m-%d"),
        "categories": paper.categories,
        "pdf_url": paper.pdf_url,
    }
