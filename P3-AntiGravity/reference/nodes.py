"""Reference nodes for P3 Code Review."""
from typing import cast
from models import llm_model
try:
    from .output_schemas import ReviewResult, TestSuite, TestExecutionResult
    from .prompts import REVIEW_PROMPT, TEST_GEN_PROMPT
    from .state import CodeReviewState
except ImportError:
    from output_schemas import ReviewResult, TestSuite, TestExecutionResult
    from prompts import REVIEW_PROMPT, TEST_GEN_PROMPT
    from state import CodeReviewState


def _format_review_summary(review: ReviewResult | None) -> str:
    if not review:
        return "No prior review findings available."
    lines = [f"Overall Quality Score: {review.score}/10", f"Summary: {review.summary}"]
    if review.issues:
        lines.append("\nIdentified Issues:")
        for issue in review.issues:
            loc = f"Line {issue.line_number}: " if issue.line_number is not None else ""
            lines.append(f"- [{issue.severity.upper()}] ({issue.category}) {loc}{issue.description}")
            lines.append(f"  Suggestion: {issue.suggestion}")
    if review.refactored_code:
        lines.append(f"\nRefactored Code Version:\n```\n{review.refactored_code}\n```")
    return "\n".join(lines)

def review_code(state: CodeReviewState) -> dict:
    try:
        chain = REVIEW_PROMPT | llm_model.chain("medium", structured=ReviewResult)
        result = chain.invoke({
            "language": state.get("language", "python"),
            "file_path": state.get("file_path") or "<inline_code>",
            "code": state["code"],
        })
        return {"review": cast(ReviewResult, result), "error": None}
    except Exception as e:
        return {"error": f"Review node failed: {e}"}

def generate_tests(state: CodeReviewState) -> dict:
    try:
        review_summary = _format_review_summary(state.get("review"))
        language = state.get("language", "python")
        framework = "pytest" if language.lower() == "python" else "standard test runner"
        chain = TEST_GEN_PROMPT | llm_model.chain("medium", structured=TestSuite)
        result = chain.invoke({
            "framework": framework,
            "language": language,
            "file_path": state.get("file_path") or "<inline_code>",
            "code": state["code"],
            "review_summary": review_summary,
        })
        return {"tests": cast(TestSuite, result), "error": None}
    except Exception as e:
        return {"error": f"Test generation node failed: {e}"}

def execute_tests(state: CodeReviewState) -> dict:
    """Execute generated test suite against the target code in an isolated sandbox."""
    if not state.get("tests"):
        return {
            "test_execution": TestExecutionResult(
                status="error",
                passed=False,
                exit_code=-1,
                output="No tests to execute.",
            )
        }

    import sys
    import tempfile
    import subprocess
    from pathlib import Path


    code = state["code"]
    test_code = state["tests"].test_code

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        src_file = tmp_path / "tested_module.py"
        src_file.write_text(code, encoding="utf-8")

        test_file = tmp_path / "test_module.py"
        test_file.write_text(test_code, encoding="utf-8")

        try:
            res = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", str(test_file)],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=15,
            )
            is_passed = (res.returncode == 0)
            status = "passed" if is_passed else "failed"
            output = res.stdout + ("\n" + res.stderr if res.stderr else "")
            return {
                "test_execution": TestExecutionResult(
                    status=status,
                    passed=is_passed,
                    exit_code=res.returncode,
                    output=output,
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

