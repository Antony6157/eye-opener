from typing import Literal, Optional, TypedDict


RetrievalMethod = Literal["rag", "live_search", "hybrid"]


class AgentState(TypedDict):
    raw_input: str
    cleaned_text: str
    claims: list[str]
    research_logs: list[dict]
    critiques: list[str]
    verdicts: list[dict]
    truth_score: int
    active_agent: str
    retrieval_method: RetrievalMethod
    error: Optional[str]


def initial_state(raw_input: str) -> AgentState:
    return {
        "raw_input": raw_input,
        "cleaned_text": "",
        "claims": [],
        "research_logs": [],
        "critiques": [],
        "verdicts": [],
        "truth_score": 0,
        "active_agent": "architect",
        "retrieval_method": "live_search",
        "error": None,
    }