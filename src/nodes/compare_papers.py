"""Node 8: Paper Comparison - compare two papers side by side."""

import arxiv
from src.state import AgentState
from src.utils.llm_client import invoke_llm


COMPARE_SYSTEM = """You are a research paper analyst. Compare these two papers.
Output a JSON object with:
{
  "similarities": ["similarity 1", "similarity 2"],
  "differences": ["difference 1", "difference 2"],
  "paper_a_strengths": ["strength 1", "strength 2"],
  "paper_b_strengths": ["strength 1", "strength 2"],
  "recommendation": "which paper to read first and why"
}
Return ONLY valid JSON."""

COMPARE_USER = """Paper A: {title_a}
Abstract A: {abstract_a}

Paper B: {title_b}
Abstract B: {abstract_b}"""


def compare_papers_node(state: AgentState) -> dict:
    compare_ids = state.get("compare_ids", [])
    if len(compare_ids) < 2:
        return {"error": "Need two paper IDs to compare."}

    papers = []
    client = arxiv.Client()
    for pid in compare_ids[:2]:
        search = arxiv.Search(id_list=[pid])
        results = list(client.results(search))
        if results:
            p = results[0]
            papers.append({
                "title": p.title,
                "arxiv_id": pid,
                "authors": [a.name for a in p.authors],
                "summary": p.summary,
                "published": p.published.strftime("%Y-%m-%d"),
            })

    if len(papers) < 2:
        return {"error": "Could not fetch both papers."}

    try:
        response = invoke_llm(
            COMPARE_SYSTEM,
            COMPARE_USER.format(
                title_a=papers[0]["title"],
                abstract_a=papers[0]["summary"][:2000],
                title_b=papers[1]["title"],
                abstract_b=papers[1]["summary"][:2000],
            ),
        )
        import json, re
        cleaned = response.strip()
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            comparison = json.loads(match.group(0))
        else:
            comparison = {}
    except Exception:
        comparison = {}

    return {
        "comparison_papers": papers,
        "comparison_result": comparison,
    }
