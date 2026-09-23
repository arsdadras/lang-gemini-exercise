"""Test Generator Subgraph: standalone compiled graph for test generation, sandbox
execution, and self-correction."""

from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from agentlab.configs.code_review_config import MAX_TEST_RETRIES
from agentlab.nodes.code_review_node import (
    execute_tests_node,
    fix_tests_node,
    generate_tests_node,
)
from agentlab.schemas.state.code_review_state import CodeReviewState


def route_after_test_gen(state: CodeReviewState) -> str:
    """Determine next step after test generation: proceed to sandbox or fail-fast."""
    if state.get("error") or not state.get("tests"):
        return "__end__"
    return "execute_tests"


def route_after_execution(
    state: CodeReviewState,
    config: RunnableConfig | None = None,
) -> str:
    """Determine next step after sandbox execution: finish if passed or retries
    exhausted, else fix."""
    execution = state.get("test_execution")
    if not execution or execution.passed:
        return "__end__"

    configurable = config.get("configurable", {}) if config else {}
    max_retries = configurable.get("max_test_retries", MAX_TEST_RETRIES)

    current_retries = state.get("test_retries", 0)
    if current_retries < max_retries:
        return "fix_tests"

    return "__end__"


def build_test_gen_subgraph():
    """Build and compile the standalone Test Generator Subgraph."""
    workflow = StateGraph(CodeReviewState)

    # 1. Register nodes
    workflow.add_node("generate_tests", generate_tests_node)
    workflow.add_node("execute_tests", execute_tests_node)
    workflow.add_node("fix_tests", fix_tests_node)

    # 2. Add edges and conditional routing
    workflow.add_edge(START, "generate_tests")
    workflow.add_conditional_edges(
        "generate_tests",
        route_after_test_gen,
        {
            "execute_tests": "execute_tests",
            "__end__": END,
        },
    )
    # Self-Correction Loop:
    workflow.add_conditional_edges(
        "execute_tests",
        route_after_execution,
        {
            "fix_tests": "fix_tests",
            "__end__": END,
        },
    )
    workflow.add_edge("fix_tests", "execute_tests")

    return workflow.compile()
