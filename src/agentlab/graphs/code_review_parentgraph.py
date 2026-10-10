"""Parent Graph Assembly for P3 Code Review & Test Generation using Pure Subgraphs."""

from typing import NewType

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.graphs.refactor_subgraph import build_refactor_subgraph
from agentlab.graphs.reviewer_subgraph import build_reviewer_subgraph
from agentlab.graphs.test_gen_subgraph import build_test_gen_subgraph
from agentlab.schemas.state.code_review_state import CodeReviewState

CodeReviewGraph = NewType("CodeReviewGraph", CompiledStateGraph)
"""A graph ``build_code_review_graph`` compiled: its state carries ``review``, ``tests``,
``test_run``, ``applied_code``, and ``error``, and it pauses at the refactor gate. A static
guarantee only: a type checker rejects any other graph; at run time it is the compiled graph."""


def route_after_reviewer(state: CodeReviewState) -> str:
    """Conditional edge after Reviewer: proceed to test generation if no fatal error."""
    if state.get("error"):
        return "__end__"
    return "test_generator"


def route_after_test_gen(state: CodeReviewState) -> str:
    """Conditional edge after TestGen: proceed to refactor gate if refactored code
    exists."""
    if state.get("error"):
        return "__end__"

    review = state.get("review")
    if review and review.refactored_code:
        return "refactor_gate"

    return "__end__"


def build_code_review_graph(
    checkpointer: BaseCheckpointSaver | None = None,
) -> CodeReviewGraph:
    """Build and compile the top-level Code Review pipeline by composing 3 subgraphs."""
    workflow = StateGraph(CodeReviewState)

    # 1. Register 3 Pure Subgraphs
    workflow.add_node("reviewer", build_reviewer_subgraph())
    workflow.add_node("test_generator", build_test_gen_subgraph())
    workflow.add_node("refactor_gate", build_refactor_subgraph())

    # 2. Add edges between Subgraphs
    workflow.add_edge(START, "reviewer")
    workflow.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {
            "test_generator": "test_generator",
            "__end__": END,
        },
    )
    workflow.add_conditional_edges(
        "test_generator",
        route_after_test_gen,
        {
            "refactor_gate": "refactor_gate",
            "__end__": END,
        },
    )
    workflow.add_edge("refactor_gate", END)

    # 3. Compile with checkpointer
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    return CodeReviewGraph(workflow.compile(checkpointer=saver))
