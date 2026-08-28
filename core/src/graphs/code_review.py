"""LangGraph StateGraph assembly for P3 Code Review & Test Generation."""

from langchain_core.runnables import RunnableConfig
from nodes.code_review import fix_tests_node
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from configs import MAX_TEST_RETRIES
from nodes.code_review import execute_tests_node, generate_tests_node, review_code_node
from state.code_review import CodeReviewState


def route_after_review(state: CodeReviewState) -> str:
    """Determine next step after code review: proceed to test generation or fail-fast to END."""
    if state.get("error"):
        return "__end__"
    return "generate_tests"


def route_after_test_gen(state: CodeReviewState) -> str:
    """Determine next step after test generation: proceed to sandbox execution or END."""
    if state.get("error") or not state.get("tests"):
        return "__end__"
    return "execute_tests"


def route_after_execution(state: CodeReviewState, config: RunnableConfig | None = None) -> str:
    """Determine next step after sandbox run: finish if passed or retries exhausted, else fix tests."""
    execution = state.get("test_execution")
    if not execution or execution.passed:
        return "__end__"

    configurable = config.get("configurable", {}) if config else {}
    max_retries = configurable.get("max_test_retries", MAX_TEST_RETRIES)

    current_retries = state.get("test_retries", 0)
    if current_retries < max_retries:
        return "fix_tests"

    return "__end__"



def build_code_review_graph(
    checkpointer: BaseCheckpointSaver | None = None,
):
    """Build and compile the Code Review and Test Generation StateGraph."""
    workflow = StateGraph(CodeReviewState)  # type: ignore[call-arg]

    # 1. Register nodes
    workflow.add_node("review_code", review_code_node)
    workflow.add_node("generate_tests", generate_tests_node)
    workflow.add_node("execute_tests", execute_tests_node)
    workflow.add_node("fix_tests", fix_tests_node)

    # 2. Add edges and conditional routing
    workflow.add_edge(START, "review_code")
    workflow.add_conditional_edges(
        "review_code",
        route_after_review,
        {
            "generate_tests": "generate_tests",
            "__end__": END,
        },
    )
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

    # After fixing, go back to execute tests
    workflow.add_edge("fix_tests", "execute_tests")

    # 3. Compile with checkpointer
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    return workflow.compile(checkpointer=saver)
