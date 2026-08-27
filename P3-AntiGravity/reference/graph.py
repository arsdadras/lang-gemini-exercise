"""Reference graph for P3 Code Review."""
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from .nodes import generate_tests, review_code
from .state import CodeReviewState

def route_after_review(state: CodeReviewState) -> str:
    if state.get("error"):
        return END
    return "generate_tests"

def build_code_review_graph(checkpointer: BaseCheckpointSaver | None = None):
    workflow = StateGraph(CodeReviewState)
    workflow.add_node("review_code", review_code)
    workflow.add_node("generate_tests", generate_tests)
    workflow.add_edge(START, "review_code")
    workflow.add_conditional_edges(
        "review_code",
        route_after_review,
        {"generate_tests": "generate_tests", END: END},
    )
    workflow.add_edge("generate_tests", END)
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    return workflow.compile(checkpointer=saver)
