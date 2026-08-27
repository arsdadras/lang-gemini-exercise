from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.constants import END
from langgraph.constants import START
from py_files.node import generate_tests
from py_files.node import review_code
from langgraph.graph import StateGraph
from typing import cast, Type
from .state import CodeReviewState


def conditional_routing(state: CodeReviewState):
    """Determine next step after code review: proceed to test generation
    or fail-fast to END."""
    if state.get("errors"):
        return "end"
    return "generate_tests"


def build_code_review_graph():

    workflow = StateGraph(CodeReviewState)

    workflow.add_node("review_code", review_code)
    workflow.add_node("generate_tests", generate_tests)

    workflow.add_edge(START, "review_code")
    workflow.add_conditional_edges(
        "review_code",
        conditional_routing,
        {"end": END, "generate_tests": "generate_tests"},
    )
    workflow.add_edge("generate_tests", END)

    checkpointer: BaseCheckpointSaver | None = None
    saver = checkpointer if checkpointer is None else InMemorySaver()

    graph = workflow.compile(checkpointer=saver)
    return graph
