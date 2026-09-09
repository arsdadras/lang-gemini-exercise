"""Reviewer Subgraph: standalone compiled graph for code analysis and review generation."""

from langgraph.graph import END, START, StateGraph

from nodes.code_review_node import review_code_node
from state.code_review_state import CodeReviewState


def build_reviewer_subgraph():
    """Build and compile the standalone Reviewer Subgraph."""
    workflow = StateGraph(CodeReviewState)  # type: ignore[call-arg]

    workflow.add_node("review_code", review_code_node)
    workflow.add_edge(START, "review_code")
    workflow.add_edge("review_code", END)

    return workflow.compile()
