"""Node functions for P3 Code Review and Test Generation graph."""

from op_schema import TestExecutionResult
from models.registry import llm_model
from typing import cast

from .model import gemini_flashlite
from .op_schema import ReviewResult, TestSuite
from .prompt import REVIEW_PROMPT, TEST_GEN_PROMPT
from .state import CodeReviewState

import subprocess
import sys
import tempfile
from pathlib import Path


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


def execute_tests(state: CodeReviewState) -> dict:
    if not state["tests"] or not state["tests"].test_code:
        return {
            "test_execution": TestExecutionResult(
                status="error",
                passed=False,
                exit_code=-1,
                output="no test code available to execute",
            )
        }

    tests = state["tests"]
    test_code = state["tests"].test_code

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Zakhireye code-e asli ba name standard baraye import dar test
    src_file = tmp_path / "tested_module.py"
    src_file.write_text(code, encoding="utf-8")

    # Zakhireye test code
    test_file = tmp_path / "test_module.py"
    test_file.write_text(test_code, encoding="utf-8")

    # 2. Ejraye pytest dar yek process-e joda ba timeout
    try:
        res = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", str(test_file)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=15,  # Jologiri az infinite loop dar code-haye kharab
        )

        is_passed = res.returncode == 0
        status = "passed" if is_passed else "failed"
        full_output = res.stdout + ("\n" + res.stderr if res.stderr else "")

        return {
            "test_execution": TestExecutionResult(
                status=status,
                passed=is_passed,
                exit_code=res.returncode,
                output=full_output,
            )
        }

    except subprocess.TimeoutExpired:
        return {
            "test_execution": TestExecutionResult(
                status="timed_out",
                passed=False,
                exit_code=-1,
                output="Test execution timed out after 15 seconds.",
            )
        }

    except Exception as e:
        return {
            "test_execution": TestExecutionResult(
                status="error",
                passed=False,
                exit_code=-1,
                output=f"Execution environment failure: {e}",
            )
        }
