"""P3 domain workflow & specialist: ``CodeReviewWorkflow``, ``run_code_review``, and ``CODE_REVIEW_SPECIALIST``."""

from typing import Any

from langgraph.graph.state import CompiledStateGraph

from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import (
    CODE_REVIEW_SPEC,
    DEFAULT_CODE_REVIEW_DESCRIPTION,
    CodeReviewGraph,
    build_code_review_graph,
    format_code_review_report_node,
)
from agentlab.schemas.input.code_review_input_schema import CodeReviewInput
from agentlab.schemas.output.code_review_output_schema import CodeReviewReport
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.workflows.specialist_workflow import Workflow

__all__ = [
    "CODE_REVIEW_SPECIALIST",
    "DEFAULT_CODE_REVIEW_DESCRIPTION",
    "CodeReviewWorkflow",
    "build_code_review_graph",
    "code_review_workflow",
    "make_code_review_specialist",
    "render_outcome",
    "run_code_review",
]


def _default_code_review_graph() -> CompiledStateGraph:
    return build_code_review_graph(
        checkpointer=get_sqlite_checkpointer(checkpoint_db_path(DELEGATIONS_APP))
    )


def render_outcome(outcome: CodeReviewReport) -> str:
    """The pipeline's findings as a short report for a model caller."""
    review = outcome.review
    parts = [f"### Code Review Summary (Score: {review.score}/10)", review.summary]
    if review.issues:
        parts.append("\n**Key Issues Found:**")
        for issue in review.issues:
            location = (
                f"Line {issue.line_number}: " if issue.line_number is not None else ""
            )
            parts.append(f"- [{issue.severity.upper()}] {location}{issue.description}")
    if outcome.tests:
        execution = outcome.test_run
        result = (
            "PASSED"
            if execution and execution.passed
            else (execution.status.upper() if execution else "NOT RUN")
        )
        parts.append(
            f"\n### Tests: {result} ({len(outcome.tests.test_cases)} test cases)",
        )
    refactored = outcome.applied_code or review.refactored_code
    if refactored:
        label = "Applied" if outcome.applied_code else "Suggested (not applied)"
        parts.append(f"\n### {label} Refactored Code:\n```python\n{refactored}\n```")
    return "\n".join(parts)


class CodeReviewWorkflow(Workflow[CodeReviewInput, CodeReviewReport]):
    """Active Rung-2 Code Review domain workflow wrapping ``CodeReviewGraph`` as a Runnable facade."""

    spec = CODE_REVIEW_SPEC

    def __init__(
        self,
        graph: CodeReviewGraph | CompiledStateGraph | Any | None = None,
    ) -> None:
        super().__init__(graph)

    def build_default_graph(self) -> CompiledStateGraph:
        return _default_code_review_graph()

    def render(self, report: CodeReviewReport) -> str:
        return render_outcome(report)

    def format_state(self, state: dict[str, Any]) -> dict[str, Any]:
        """Format raw code review state if returned by an external runner/mock without format_report node."""
        if state.get("report") is None and state.get("result") is None:
            return {**state, **format_code_review_report_node(state)}  # type: ignore[arg-type]
        return state


def run_code_review(
    graph: CodeReviewGraph | CompiledStateGraph | Any,
    code: str,
    *,
    language: str = "python",
) -> SpecialistResult[CodeReviewReport]:
    """Review ``code`` with the P3 pipeline on a fresh thread, as a specialist envelope."""
    return CodeReviewWorkflow(graph).invoke({"code": code, "language": language})[
        "result"
    ]


def make_code_review_specialist(
    engine: CodeReviewGraph | CompiledStateGraph | Any = None,
) -> CodeReviewWorkflow:
    """Create a Code Review Workflow bound to an engine or lazy default."""
    return CodeReviewWorkflow(engine)


CODE_REVIEW_SPECIALIST = CodeReviewWorkflow()
code_review_workflow = CODE_REVIEW_SPECIALIST
