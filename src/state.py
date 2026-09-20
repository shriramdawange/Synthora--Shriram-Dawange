"""AgentState: TypedDict defining data flow between all nodes."""

from typing import TypedDict, Optional, Literal
from pydantic import BaseModel


class PaperBriefing(BaseModel):
    title: str = ""
    authors: list[str] = []
    arxiv_id: str = ""
    published: str = ""
    summary: str = ""
    problem_statement: list[str] = []
    method: list[str] = []
    key_results: list[str] = []
    limitations: list[str] = []
    suggested_questions: list[str] = []


class QAExchange(BaseModel):
    turn: int
    user_question: str
    grounded_answer: str
    sources: list[str] = []


class AgentState(TypedDict):
    user_input: str
    query_type: Literal["arxiv_id", "topic_search", "compare", "synthesize", "invalid"]
    arxiv_id: Optional[str]
    compare_ids: list[str]
    search_results: list[dict]
    selected_paper: Optional[dict]
    raw_pdf_text: str
    sections: dict[str, str]
    chunks: list[dict]
    vector_store_path: Optional[str]
    briefing: Optional[PaperBriefing]
    conversation_history: list[QAExchange]
    author_info: list[dict]
    recommendations: list[dict]
    comparison_papers: list[dict]
    comparison_result: Optional[dict]
    synthesis: Optional[dict]
    error: Optional[str]
