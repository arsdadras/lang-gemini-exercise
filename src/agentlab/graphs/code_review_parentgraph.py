"""Parent Graph Assembly for P3 Code Review & Test Generation using Pure Subgraphs."""

from typing import Any, NewType

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

CodeReviewGraph = NewType("CodeReviewGraph", CompiledStateGraph)

from agentlab.graphs.refactor_subgraph import build_refactor_subgraph
from agentlab.graphs.reviewer_subgraph import build_reviewer_subgraph
from agentlab.graphs.test_gen_subgraph import build_test_gen_subgraph
from agentlab.schemas.input.code_review_input_schema import CodeReviewInput
from agentlab.schemas.output.code_review_output_schema import CodeReviewReport
from agentlab.schemas.state.code_review_state import CodeReviewState
from agentlab.utils.subagent_util import pending_approvals
from agentlab.workflows.specialist_workflow import ResultNode, SpecialistSpec

DEFAULT_CODE_REVIEW_DESCRIPTION = (
    "Analyzes and reviews source code, identifies bugs, security vulnerabilities, "
    "and performance flaws, generates and executes pytest test suites in an isolated "
    "sandbox, and outputs refactored code."
)

CODE_REVIEW_SPEC = SpecialistSpec[CodeReviewInput, CodeReviewReport](
    name="code_review",
    description=DEFAULT_CODE_REVIEW_DESCRIPTION,
    input_schema=CodeReviewInput,
    report_schema=CodeReviewReport,
)


def route_after_reviewer(state: CodeReviewState) -> str:
    """Conditional edge after Reviewer: proceed to test generation if no fatal error."""
    if state.get("error"):
        return "__end__"
    return "test_generator"


def route_after_test_gen(state: CodeReviewState) -> str:
    """Conditional edge after TestGen: proceed to refactor gate if refactored code exists."""
    if state.get("error"):
        return "__end__"

    review = state.get("review")
    if review and review.refactored_code:
        return "refactor_gate"

    return "__end__"


def format_code_review_report_node(state: CodeReviewState) -> dict[str, Any]:
    """Format review, tests, and refactor state into ``CodeReviewReport`` and problems."""
    review = state.get("review")
    if review is None:
        err = state.get("error") or "No review was produced."
        return {"report": None, "problems": [err]}

    outcome = CodeReviewReport(
        review=review,
        tests=state.get("tests"),
        test_run=state.get("test_run"),
        applied_code=state.get("applied_code"),
    )
    problems = []
    if waiting := pending_approvals(state):
        problems.append(
            f"The suggested refactor waits for approval ({waiting}); it wasn't applied."
        )
    elif outcome.test_run is None or outcome.test_run.status in (
        "error",
        "timed_out",
    ):
        problems.append("The generated tests didn't run to completion.")
    return {"report": outcome, "problems": problems}


def build_code_review_graph(
    checkpointer: BaseCheckpointSaver | None = None,
) -> CodeReviewGraph:
    """Build and compile the top-level Code Review pipeline ending in ``format_report -> pack_result``."""
    workflow = StateGraph(CodeReviewState)

    # 1. Register 3 Pure Subgraphs + format_report + pack_result
    workflow.add_node("reviewer", build_reviewer_subgraph())
    workflow.add_node("test_generator", build_test_gen_subgraph())
    workflow.add_node("refactor_gate", build_refactor_subgraph())
    workflow.add_node("format_report", format_code_review_report_node)
    workflow.add_node("pack_result", ResultNode(CODE_REVIEW_SPEC))

    # 2. Add edges between Subgraphs and terminal nodes
    workflow.add_edge(START, "reviewer")
    workflow.add_conditional_edges(
        "reviewer",
        route_after_reviewer,
        {
            "test_generator": "test_generator",
            "__end__": "format_report",
        },
    )
    workflow.add_conditional_edges(
        "test_generator",
        route_after_test_gen,
        {
            "refactor_gate": "refactor_gate",
            "__end__": "format_report",
        },
    )
    workflow.add_edge("refactor_gate", "format_report")
    workflow.add_edge("format_report", "pack_result")
    workflow.add_edge("pack_result", END)

    # 3. Compile with checkpointer
    saver = checkpointer if checkpointer is not None else InMemorySaver()
    compiled = workflow.compile(checkpointer=saver)
    setattr(compiled, "_is_code_review_graph", True)  # noqa: B010
    return CodeReviewGraph(compiled)
