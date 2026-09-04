"""Node functions for P3 Code Review & Test Generation graph."""

from typing import cast

from langgraph.types import interrupt
from models import llm_model
from output_schemas.code_review_output_schema import ReviewResult, TestSuite
from prompts.nodes.code_review_prompt import (
    REVIEW_PROMPT,
    TEST_FIX_PROMPT,
    TEST_GEN_PROMPT,
)
from state.code_review_state import CodeReviewState
from utils.sandbox import run_tests_in_sandbox


def _format_review_summary(review: ReviewResult | None) -> str:
    """Helper to convert structured ReviewResult into readable text for the test prompt."""
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
                f"- [{issue.severity.upper()}] ({issue.category}) {loc}{issue.description}"
            )
            lines.append(f"  Suggestion: {issue.suggestion}")

    if review.refactored_code:
        lines.append(f"\nRefactored Code Version:\n```\n{review.refactored_code}\n```")

    return "\n".join(lines)


def review_code_node(state: CodeReviewState) -> dict:
    """Analyze source code and produce structured review findings."""
    try:
        chain = REVIEW_PROMPT | llm_model.chain("medium", structured=ReviewResult, cascade=True)
        result = chain.invoke(
            {
                "language": state.get("language", "python"),
                "file_path": state.get("file_path") or "<inline_code>",
                "code": state["code"],
            }
        )
        return {"review": cast(ReviewResult, result), "error": None}
    except Exception as e:  # noqa: BLE001
        return {"error": f"Review node failed: {e}"}


def generate_tests_node(state: CodeReviewState) -> dict:
    """Generate executable test suite covering code and regression for identified issues."""
    try:
        review_summary = _format_review_summary(state.get("review"))
        language = state.get("language", "python")
        framework = "pytest" if language.lower() == "python" else "standard test runner"

        chain = TEST_GEN_PROMPT | llm_model.chain("medium", structured=TestSuite, cascade=True)
        result = chain.invoke(
            {
                "framework": framework,
                "language": language,
                "file_path": state.get("file_path") or "<inline_code>",
                "code": state["code"],
                "review_summary": review_summary,
            }
        )
        return {"tests": cast(TestSuite, result), "error": None}
    except Exception as e:  # noqa: BLE001
        return {"error": f"Test generation node failed: {e}"}


def execute_tests_node(state: CodeReviewState) -> dict:
    """Execute generated test suite in an isolated sandbox environment."""
    if not state.get("tests") or not state["tests"].test_code:
        return {"test_execution": None}

    result = run_tests_in_sandbox(
        code=state["code"],
        test_code=state["tests"].test_code,
    )
    return {"test_execution": result}


def fix_tests_node(state: CodeReviewState) -> dict:
    """Analyze pytest execution failure and generate corrected test suite."""
    try:
        language = state.get("language", "python")
        framework = "pytest" if language.lower() == "python" else "standard test runner"
        failing_test_code = state.get("tests").test_code if state.get("tests") else ""
        error_output = (
            state.get("test_execution").output
            if state.get("test_execution")
            else "Unknown execution failure."
        )

        chain = TEST_FIX_PROMPT | llm_model.chain("medium", structured=TestSuite, cascade=True)
        result = chain.invoke(
            {
                "framework": framework,
                "language": language,
                "code": state["code"],
                "failing_test_code": failing_test_code,
                "error_output": error_output,
            }
        )
        test_retries = state.get("test_retries", 0) + 1

        return {
            "tests": cast(TestSuite, result),
            "test_retries": test_retries,
            "error": None,
        }

    except Exception as e:  # noqa: BLE001
        return {"error": f"Test fix node failed: {e}"}


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
        }
    )

    decision = str(human_response).lower().strip()
    return {"refactor_decision": decision}


def apply_refactor_node(state: CodeReviewState) -> dict:
    """Apply the approved refactored code as the final output."""
    review = state.get("review")
    if not review or not review.refactored_code:
        return {"applied_code": state["code"]}

    return {"applied_code": review.refactored_code}
