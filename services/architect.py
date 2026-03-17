import logging

from langgraph.graph import END, StateGraph

from services.agents import diver, scorer, skeptic, surgeon
from services.preprocessor import preprocess
from services.state import AgentState


LOGGER = logging.getLogger(__name__)


def error_handler(state: AgentState) -> AgentState:
    state["active_agent"] = "error_handler"
    LOGGER.error("Pipeline entered error handler: %s", state.get("error"))
    state["truth_score"] = 0
    return state


def _route_after_node(state: AgentState) -> str:
    if state["error"]:
        return "error_handler"
    return "continue"


builder = StateGraph(AgentState)

builder.add_node("preprocessor", preprocess)
builder.add_node("surgeon", surgeon)
builder.add_node("diver", diver)
builder.add_node("skeptic", skeptic)
builder.add_node("scorer", scorer)
builder.add_node("error_handler", error_handler)

builder.set_entry_point("preprocessor")

builder.add_conditional_edges(
    "preprocessor",
    _route_after_node,
    {"error_handler": "error_handler", "continue": "surgeon"},
)
builder.add_conditional_edges(
    "surgeon",
    _route_after_node,
    {"error_handler": "error_handler", "continue": "diver"},
)
builder.add_conditional_edges(
    "diver",
    _route_after_node,
    {"error_handler": "error_handler", "continue": "skeptic"},
)
builder.add_conditional_edges(
    "skeptic",
    _route_after_node,
    {"error_handler": "error_handler", "continue": "scorer"},
)
builder.add_conditional_edges(
    "scorer",
    _route_after_node,
    {"error_handler": "error_handler", "continue": END},
)
builder.add_edge("error_handler", END)

graph = builder.compile()