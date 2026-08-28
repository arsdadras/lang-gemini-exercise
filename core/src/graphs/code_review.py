"""LangGraph StateGraph assembly for P3 Code Review & Test Generation."""

from typing import cast

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from nodes.code_review import execute_tests, generate_tests, review_code
from state.code_review import CodeReviewState


def route_after_review(state: CodeReviewState) -> str:
    """Determine next step after code review: proceed to test generation or fail-fast to END."""
    if state.get("error"):
        return END
    return "generate_tests"


def route_after_test_gen(state: CodeReviewState) -> str:
    """Determine next step after test generation: proceed to sandbox execution or END."""
    if state.get("error") or not state.get("tests"):
        return END
    return "execute_tests"


def build_code_review_graph(
    checkpointer: BaseCheckpointSaver | None = None,
):
    """Build and compile the Code Review and Test Generation StateGraph."""
    workflow = StateGraph(CodeReviewState)  # type: ignore[call-arg]

    # 1. Register nodes
    workflow.add_node("review_code", review_code)
    workflow.add_node("generate_tests", generate_tests)
    workflow.add_node("execute_tests", execute_tests)

    # 2. Add edges and conditional routing
    workflow.add_edge(START, "review_code")
    workflow.add_conditional_edges(
        "review_code",
        route_after_review,
        {
            "generate_tests": "generate_tests",
            END: END,
        },
    )
    workflow.add_conditional_edges(
        "generate_tests",
        route_after_test_gen,
        {
            "execute_tests": "execute_tests",
            END: END,
        },
    )
    workflow.add_edge("execute_tests", END)

    # 3. Compile with checkpointer
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    return workflow.compile(checkpointer=saver)
