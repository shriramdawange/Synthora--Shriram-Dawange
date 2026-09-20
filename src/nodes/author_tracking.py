"""Node 9: Author Tracking - get author info and their papers."""

import arxiv
from src.state import AgentState


def author_tracking_node(state: AgentState) -> dict:
    selected_paper = state.get("selected_paper", {})
    authors = selected_paper.get("authors", [])

    if not authors:
        return {"author_info": [], "error": "No authors found."}

    author_data = []
    client = arxiv.Client()

    for author_name in authors[:3]:
        search = arxiv.Search(
            query=f"au:{author_name}",
            max_results=5,
            sort_by=arxiv.SortCriterion.SubmittedDate,
        )
        results = list(client.results(search))
        papers = []
        categories = set()
        for p in results:
            papers.append({
                "title": p.title,
                "arxiv_id": p.entry_id.split("/")[-1].split("v")[0],
                "published": p.published.strftime("%Y-%m-%d"),
            })
            categories.update(p.categories[:3])

        author_data.append({
            "name": author_name,
            "paper_count": len(papers),
            "fields": list(categories)[:5],
            "recent_papers": papers,
        })

    return {"author_info": author_data}
