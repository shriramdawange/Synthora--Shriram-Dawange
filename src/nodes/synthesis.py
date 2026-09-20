"""Node 11: Multi-Paper Synthesis - synthesize findings across papers."""

import arxiv
from src.state import AgentState
from src.utils.llm_client import invoke_llm


SYNTHESIS_SYSTEM = """You are a research analyst synthesizing multiple papers.
Given the summaries and key findings from several papers, produce:

{
  "topic": "research topic",
  "papers_count": 3,
  "common_themes": ["theme 1", "theme 2"],
  "evolution": "how the field has evolved",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "open_questions": ["question 1", "question 2"],
  "future_directions": ["direction 1", "direction 2"]
}

Return ONLY valid JSON."""

SYNTHESIS_USER = """Research topic: {topic}

Papers analyzed:
{papers_text}"""


def synthesize_papers_node(state: AgentState) -> dict:
    topic = state.get("user_input", "").strip()
    search_results = state.get("search_results", [])

    if not search_results and topic:
        client = arxiv.Client()
        search = arxiv.Search(
            query=topic,
            max_results=5,
            sort_by=arxiv.SortCriterion.Relevance,
        )
        results = list(client.results(search))
        search_results = [
            {
                "title": p.title,
                "arxiv_id": p.entry_id.split("/")[-1].split("v")[0],
                "summary": p.summary,
            }
            for p in results
        ]

    if not search_results:
        return {"synthesis": None, "error": "No papers found to synthesize."}

    papers_text = ""
    client = arxiv.Client()

    for i, paper in enumerate(search_results[:3], 1):
        pid = paper.get("arxiv_id", "")
        try:
            search = arxiv.Search(id_list=[pid])
            results = list(client.results(search))
            if results:
                p = results[0]
                papers_text += f"\n--- Paper {i}: {p.title} ---\n"
                papers_text += f"Authors: {', '.join(a.name for a in p.authors[:3])}\n"
                papers_text += f"Abstract: {p.summary[:1500]}\n"
        except Exception:
            continue

    if not papers_text:
        return {"synthesis": None, "error": "Could not fetch paper details."}

    try:
        response = invoke_llm(
            SYNTHESIS_SYSTEM,
            SYNTHESIS_USER.format(topic=topic, papers_text=papers_text),
        )
        import json, re
        cleaned = response.strip()
        match = re.search(r'\{[\s\S]*\}', cleaned)
        if match:
            synthesis = json.loads(match.group(0))
        else:
            synthesis = {"topic": topic, "papers_count": len(search_results[:3])}
    except Exception:
        synthesis = {"topic": topic, "papers_count": len(search_results[:3])}

    return {"synthesis": synthesis}
