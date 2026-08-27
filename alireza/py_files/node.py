"""Node functions for P3 Code Review and Test Generation graph."""

from models.registry import llm_model
from typing import cast

from .model import gemini_flashlite
from .op_schema import ReviewResult, TestSuite
from .prompt import REVIEW_PROMPT, TEST_GEN_PROMPT
from .state import CodeReviewState


def _format_review_summary(review: ReviewResult | None) -> str:
    """Helper to convert structured ReviewResult into formatted text for
    the test prompt."""
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
        lines.append(
            f"\nRefactored Code Version:\n```\n{review.
refactored_code}\n```"
        )

    return "\n".join(lines)


def review_code(state: CodeReviewState) -> dict:
    """Analyze the code and produce structured review findings."""
    try:
        chain = REVIEW_PROMPT | llm_model.chain("medium", structured=ReviewResult)
        result = chain.invoke(
            {
                "language": state.get("language", "python"),
                "file_path": state.get("file_path") or "<inline_code>",
                "code": state["code"],
            }
        )
        return {"review": cast(ReviewResult, result), "error": None}
    except Exception as e:
        return {"error": f"Review node failed: {e}"}


def generate_tests(state: CodeReviewState) -> dict:
    """Generate executable test suite covering the code and regression
    for identified issues."""
    try:
        review_summary = _format_review_summary(state.get("review"))
        language = state.get("language", "python")
        framework = "pytest" if language.lower() == "python" else "standard test runner"

        chain = TEST_GEN_PROMPT | llm_model.chain("medium", structured=TestSuite)
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

    except Exception as e:
        return {"error": f"Test generation node failed: {e}"}
