"""LangGraph state graph: wire all nodes into the pipeline."""

from langgraph.graph import StateGraph, END

from src.state import AgentState
from src.nodes.query_understanding import query_understanding_node
from src.nodes.arxiv_retrieval import arxiv_retrieval_node
from src.nodes.selection_ranking import selection_ranking_node
from src.nodes.fetch_parse_pdf import fetch_parse_pdf_node
from src.nodes.chunk_embed import chunk_embed_node
from src.nodes.summarize import summarize_node
from src.nodes.qa_loop import qa_node
from src.nodes.compare_papers import compare_papers_node
from src.nodes.author_tracking import author_tracking_node
from src.nodes.recommendations import recommend_papers_node
from src.nodes.synthesis import synthesize_papers_node


def _route_after_query(state: AgentState) -> str:
    if state.get("error"):
        return "end"
    qt = state.get("query_type", "")
    if qt == "compare":
        return "compare"
    if qt == "synthesize":
        return "synthesize"
    return "retrieve"


def _route_after_retrieval(state: AgentState) -> str:
    if state.get("error"):
        return "end"
    query_type = state.get("query_type", "")
    if query_type == "arxiv_id":
        return "fetch_pdf"
    return "select"


def _route_after_selection(state: AgentState) -> str:
    if state.get("error"):
        return "end"
    return "fetch_pdf"


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("query_understanding", query_understanding_node)
    graph.add_node("arxiv_retrieval", arxiv_retrieval_node)
    graph.add_node("selection_ranking", selection_ranking_node)
    graph.add_node("fetch_parse_pdf", fetch_parse_pdf_node)
    graph.add_node("chunk_embed", chunk_embed_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("qa_loop", qa_node)
    graph.add_node("compare_papers", compare_papers_node)
    graph.add_node("author_tracking", author_tracking_node)
    graph.add_node("recommendations", recommend_papers_node)
    graph.add_node("synthesize_papers", synthesize_papers_node)

    graph.set_entry_point("query_understanding")

    graph.add_conditional_edges(
        "query_understanding",
        _route_after_query,
        {
            "retrieve": "arxiv_retrieval",
            "compare": "compare_papers",
            "synthesize": "synthesize_papers",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "arxiv_retrieval",
        _route_after_retrieval,
        {
            "select": "selection_ranking",
            "fetch_pdf": "fetch_parse_pdf",
            "end": END,
        },
    )

    graph.add_conditional_edges(
        "selection_ranking",
        _route_after_selection,
        {
            "fetch_pdf": "fetch_parse_pdf",
            "end": END,
        },
    )

    graph.add_edge("fetch_parse_pdf", "chunk_embed")
    graph.add_edge("chunk_embed", "summarize")
    graph.add_edge("summarize", "author_tracking")
    graph.add_edge("author_tracking", "recommendations")
    graph.add_edge("recommendations", "qa_loop")
    graph.add_edge("compare_papers", END)
    graph.add_edge("synthesize_papers", END)

    graph.add_edge("qa_loop", END)

    return graph.compile()
