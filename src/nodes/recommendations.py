"""Node 10: Paper Recommendations - find similar papers."""

import arxiv
from src.state import AgentState
from src.utils.llm_client import invoke_llm


def get_keywords(title: str, abstract: str) -> list[str]:
    try:
        resp = invoke_llm(
            "Return ONLY 5 comma-separated keywords from this paper. No explanation.",
            f"Title: {title}\nAbstract: {abstract[:1000]}"
        )
        return [k.strip() for k in resp.split(",") if k.strip()][:5]
    except Exception:
        words = title.split()
        return words[:5]


def recommend_papers_node(state: AgentState) -> dict:
    selected_paper = state.get("selected_paper", {})
    if not selected_paper:
        return {"recommendations": [], "error": "No paper selected."}

    title = selected_paper.get("title", "")
    abstract = selected_paper.get("summary", "")
    current_id = selected_paper.get("arxiv_id", "")

    keywords = get_keywords(title, abstract)

    seen_ids = {current_id}
    recommendations = []
    client = arxiv.Client()

    for kw in keywords:
        search = arxiv.Search(
            query=f"all:{kw}",
            max_results=3,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        for p in client.results(search):
            pid = p.entry_id.split("/")[-1].split("v")[0]
            if pid in seen_ids:
                continue
            seen_ids.add(pid)
            recommendations.append({
                "title": p.title,
                "arxiv_id": pid,
                "authors": [a.name for a in p.authors[:3]],
                "summary": p.summary[:200],
                "published": p.published.strftime("%Y-%m-%d"),
                "relevance_keyword": kw,
            })
            if len(recommendations) >= 5:
                break
        if len(recommendations) >= 5:
            break

    return {"recommendations": recommendations}
