"""P3 domain workflow & specialist: ``run_code_review`` and ``CODE_REVIEW_SPECIALIST``."""

from langgraph.graph.state import CompiledStateGraph

from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import build_code_review_graph
from agentlab.schemas.input.code_review_input_schema import CodeReviewInput
from agentlab.schemas.output.code_review_output_schema import CodeReviewReport
from agentlab.schemas.output.specialist_output_schema import (
    SpecialistResult,
    SpecialistStatus,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals
from agentlab.workflows.specialist_workflow import Specialist

DEFAULT_CODE_REVIEW_DESCRIPTION = (
    "Analyzes and reviews source code, identifies bugs, security vulnerabilities, "
    "and performance flaws, generates and executes pytest test suites in an isolated "
    "sandbox, and outputs refactored code."
)


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


def run_code_review(
    graph: CompiledStateGraph,
    code: str,
    *,
    language: str = "python",
) -> SpecialistResult[CodeReviewReport]:
    """Review ``code`` with the P3 pipeline on a fresh thread, as a specialist envelope.

    Failing tests are findings, not a failed review: ``ok`` means the review, the tests, and
    their run all happened. A refactor waiting at the approval gate makes it ``partial``.
    """
    try:
        state = graph.invoke(
            {"code": code, "language": language, "file_path": None},
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return SpecialistResult[CodeReviewReport](
            specialist="code_review",
            status="failed",
            reason=failure_reason(error),
        )
    review = state.get("review")
    if review is None:
        return SpecialistResult[CodeReviewReport](
            specialist="code_review",
            status="failed",
            reason=state.get("error") or "No review was produced.",
        )
    outcome = CodeReviewReport(
        review=review,
        tests=state.get("tests"),
        test_run=state.get("test_run"),
        applied_code=state.get("applied_code"),
    )
    execution = outcome.test_run
    status: SpecialistStatus
    if waiting := pending_approvals(state):
        status, reason = (
            "partial",
            f"The suggested refactor waits for approval ({waiting}); it wasn't applied.",
        )
    elif execution is None or execution.status in ("error", "timed_out"):
        status, reason = "partial", "The generated tests didn't run to completion."
    else:
        status, reason = "ok", ""
    return SpecialistResult[CodeReviewReport](
        specialist="code_review",
        status=status,
        reason=reason,
        output=outcome,
    )


CODE_REVIEW_SPECIALIST = Specialist[CodeReviewInput, CodeReviewReport](
    name="code_review",
    description=DEFAULT_CODE_REVIEW_DESCRIPTION,
    input_schema=CodeReviewInput,
    report_schema=CodeReviewReport,
    run=run_code_review,
    render=render_outcome,
    default_target=_default_code_review_graph,
)
