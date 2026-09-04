"""Refactor Subgraph: standalone compiled graph for HITL approval and applying
refactored code."""

from langgraph.graph import END, START, StateGraph
from nodes.code_review_node import apply_refactor_node, approved_refactor_node
from state.code_review_state import CodeReviewState


def route_after_approval(state: CodeReviewState) -> str:
    """Conditional edge: apply refactor if approved by human, else finish."""
    decision = state.get("refactor_decision", "")
    if decision in ["yes", "approve", "apply"]:
        return "apply_refactor"
    return "__end__"


def build_refactor_subgraph():
    """Build and compile the standalone Refactor Gate Subgraph."""
    workflow = StateGraph(CodeReviewState)  # type: ignore[call-arg]

    # 1. Register nodes
    workflow.add_node("approved_refactor", approved_refactor_node)
    workflow.add_node("apply_refactor", apply_refactor_node)

    # 2. Add edges and routing
    workflow.add_edge(START, "approved_refactor")
    workflow.add_conditional_edges(
        "approved_refactor",
        route_after_approval,
        {
            "apply_refactor": "apply_refactor",
            "__end__": END,
        },
    )
    workflow.add_edge("apply_refactor", END)

    return workflow.compile()