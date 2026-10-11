"""Node functions for P3 Code Review & Test Generation graph.

All three chains stay on the "medium" tier (see ADR-0014): this is P3's core deliverable
quality (review findings, generated/fixed tests), with no live-verified opensource-tier
baseline to fall back to.
"""

from typing import cast

from langgraph.types import interrupt

from agentlab.models import llm_model
from agentlab.prompts.nodes.code_review_prompt import (
    REVIEW_PROMPT,
    TEST_FIX_PROMPT,
    TEST_GEN_PROMPT,
)
from agentlab.schemas.output.code_review_output_schema import CodeReview, TestSuite
from agentlab.schemas.state.code_review_state import CodeReviewState
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.sandbox_util import run_tests_in_sandbox


def _format_review_summary(review: CodeReview | None) -> str:
    """Helper to convert structured CodeReview into readable text for the test prompt."""
    if not review:
        return "No prior review findings available."

    lines = [
        f"Overall Quality Score: {review.score}/10",
        f"Summary: {review.summary}",
    ]

    if review.issues:
        lines.append("\nIdentified Issues:")
        for issue in review.issues:
            loc = f"Line {issue.line_number}: " if issue.line_number is not None else ""
            lines.append(
                f"- [{issue.severity.upper()}] ({issue.category}) {loc}{issue.description}",
            )
            lines.append(f"  Suggestion: {issue.suggestion}")

    if review.refactored_code:
        lines.append(f"\nRefactored Code Version:\n```\n{review.refactored_code}\n```")

    return "\n".join(lines)


def review_code_node(state: CodeReviewState) -> dict:
    """Analyze source code and produce structured review findings."""
    try:
        chain = REVIEW_PROMPT | llm_model.chain(
            "medium",
            structured=CodeReview,
            cascade=True,
        )
        result = chain.invoke(
            {
                "language": state.get("language", "python"),
                "file_path": state.get("file_path") or "<inline_code>",
                "code": state["code"],
            },
        )
        return {"review": cast(CodeReview, result), "error": None}
    except Exception as e:
        if failure_kind(e) is None:
            raise
        return {"error": f"Review node failed: {failure_reason(e)}"}


def generate_tests_node(state: CodeReviewState) -> dict:
    """Generate executable test suite covering code and regression for identified issues."""
    try:
        review_summary = _format_review_summary(state.get("review"))
        language = state.get("language", "python")
        framework = "pytest" if language.lower() == "python" else "standard test runner"

        chain = TEST_GEN_PROMPT | llm_model.chain(
            "medium",
            structured=TestSuite,
            cascade=True,
        )
        result = chain.invoke(
            {
                "framework": framework,
                "language": language,
                "file_path": state.get("file_path") or "<inline_code>",
                "code": state["code"],
                "review_summary": review_summary,
            },
        )
        return {"tests": cast(TestSuite, result), "error": None}
    except Exception as e:
        if failure_kind(e) is None:
            raise
        return {"error": f"Test generation node failed: {failure_reason(e)}"}


def _target_code(state: CodeReviewState) -> str:
    """The code the test suite exercises: the refactored version when the review proposed one."""
    review = state.get("review")
    if review and review.refactored_code:
        return review.refactored_code
    return state["code"]


def execute_tests_node(state: CodeReviewState) -> dict:
    """Execute generated test suite in an isolated sandbox environment."""
    tests = state.get("tests")
    if not tests or not tests.test_code:
        return {"test_run": None}

    result = run_tests_in_sandbox(
        code=_target_code(state),
        test_code=tests.test_code,
    )
    return {"test_run": result}


def fix_tests_node(state: CodeReviewState) -> dict:
    """Analyze pytest execution failure and generate corrected test suite."""
    try:
        language = state.get("language", "python")
        framework = "pytest" if language.lower() == "python" else "standard test runner"
        tests = state.get("tests")
        test_run = state.get("test_run")
        failing_test_code = tests.test_code if tests else ""
        error_output = test_run.output if test_run else "Unknown execution failure."

        chain = TEST_FIX_PROMPT | llm_model.chain(
            "medium",
            structured=TestSuite,
            cascade=True,
        )
        result = chain.invoke(
            {
                "framework": framework,
                "language": language,
                "code": _target_code(state),
                "failing_test_code": failing_test_code,
                "error_output": error_output,
            },
        )
        test_retries = state.get("test_retries", 0) + 1

        return {
            "tests": cast(TestSuite, result),
            "test_retries": test_retries,
            "error": None,
        }

    except Exception as e:
        if failure_kind(e) is None:
            raise
        return {"error": f"Test fix node failed: {failure_reason(e)}"}


def approved_refactor_node(state: CodeReviewState) -> dict:
    """Pause graph execution via interrupt() to ask human developer for refactor approval."""
    review = state.get("review")
    if not review or not review.refactored_code:
        return {"refactor_decision": "skip"}

    human_response = interrupt(
        {
            "action_required": "Refactor Approval",
            "summary": review.summary,
            "refactored_code": review.refactored_code,
        },
    )

    decision = str(human_response).lower().strip()
    return {"refactor_decision": decision}


def apply_refactor_node(state: CodeReviewState) -> dict:
    """Apply the approved refactored code as the final output."""
    review = state.get("review")
    if not review or not review.refactored_code:
        return {"applied_code": state["code"]}

    return {"applied_code": review.refactored_code}
