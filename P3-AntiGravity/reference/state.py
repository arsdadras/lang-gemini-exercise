"""Reference state for P3 Code Review."""
from typing import TypedDict
try:
    from .output_schemas import ReviewResult, TestSuite, TestExecutionResult
except ImportError:
    from output_schemas import ReviewResult, TestSuite, TestExecutionResult


class CodeReviewState(TypedDict):
    code: str
    language: str
    file_path: str | None
    review: ReviewResult | None
    tests: TestSuite | None
    test_execution: TestExecutionResult | None
    error: str | None

