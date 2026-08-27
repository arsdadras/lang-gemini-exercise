"""State definition for P3 Code Review & Test Generation."""

from typing import TypedDict
from output_schemas.code_review import (
    ReviewResult,
    TestSuite,
    TestExecutionResult,
)


class CodeReviewState(TypedDict):
    """LangGraph state schema for the Code Review agent workflow."""

    code: str
    language: str
    file_path: str | None
    review: ReviewResult | None
    tests: TestSuite | None
    test_execution: TestExecutionResult | None
    error: str | None
