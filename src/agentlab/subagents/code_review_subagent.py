"""P3's boundary: ``run_code_review`` returns the specialist envelope; the adapter serves coordinators."""

from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.runnables import Runnable, RunnableLambda

from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.graphs.code_review_parentgraph import build_code_review_graph
from agentlab.schemas.output.code_review_output_schema import CodeReviewOutcome
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import (
    new_delegation_config,
    pending_approvals,
    task_text_from_state,
    to_subagent_reply,
)

CODE_REVIEW_SPECIALIST = "code_review"
DEFAULT_CODE_REVIEW_NAME = "code_review_subagent"
DEFAULT_CODE_REVIEW_DESCRIPTION = (
    "Analyzes and reviews source code, identifies bugs, security vulnerabilities, "
    "and performance flaws, generates and executes pytest test suites in an isolated "
    "sandbox, and outputs refactored code."
)


def run_code_review(
    graph: Runnable,
    code: str,
    *,
    language: str = "python",
) -> SpecialistResult[CodeReviewOutcome]:
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
        return SpecialistResult[CodeReviewOutcome](
            specialist=CODE_REVIEW_SPECIALIST,
            status="failed",
            reason=failure_reason(error),
        )
    review = state.get("review")
    if review is None:
        return SpecialistResult[CodeReviewOutcome](
            specialist=CODE_REVIEW_SPECIALIST,
            status="failed",
            reason=state.get("error") or "No review was produced.",
        )
    outcome = CodeReviewOutcome(
        review=review,
        tests=state.get("tests"),
        test_execution=state.get("test_execution"),
        applied_code=state.get("applied_code"),
    )
    execution = outcome.test_execution
    if waiting := pending_approvals(state):
        status, reason = (
            "partial",
            f"The suggested refactor waits for approval ({waiting}); it wasn't applied.",
        )
    elif execution is None or execution.status in ("error", "timed_out"):
        status, reason = "partial", "The generated tests didn't run to completion."
    else:
        status, reason = "ok", ""
    return SpecialistResult[CodeReviewOutcome](
        specialist=CODE_REVIEW_SPECIALIST,
        status=status,
        reason=reason,
        output=outcome,
    )


def render_outcome(outcome: CodeReviewOutcome) -> str:
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
        execution = outcome.test_execution
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


def make_code_review_subagent(
    graph: Runnable | None = None,
    *,
    name: str = DEFAULT_CODE_REVIEW_NAME,
    description: str = DEFAULT_CODE_REVIEW_DESCRIPTION,
) -> CompiledSubAgent:
    """Wrap the compiled review pipeline as a ``CompiledSubAgent``.

    Defaults to ``build_code_review_graph`` on the shared SQLite checkpointer. The last
    coordinator message is reviewed as Python source; the envelope comes back as text.
    """
    review_graph = (
        graph
        if graph is not None
        else build_code_review_graph(checkpointer=get_sqlite_checkpointer())
    )

    def run(state: dict[str, Any]) -> dict[str, Any]:
        result = run_code_review(review_graph, task_text_from_state(state))
        return to_subagent_reply(result.to_text(render=render_outcome))

    return {"name": name, "description": description, "runnable": RunnableLambda(run)}
