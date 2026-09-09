"""LangGraph state schema for the Code Review agent workflow."""

from typing import TypedDict

from output_schemas.code_review_output_schema import (
    ReviewResult,
    TestExecutionResult,
    TestSuite,
)


class CodeReviewState(TypedDict):
    """LangGraph state schema for the Code Review agent workflow."""

    code: str
    language: str
    file_path: str | None
    review: ReviewResult | None
    tests: TestSuite | None
    test_execution: TestExecutionResult | None
    test_retries: int
    refactor_decision: str | None
    applied_code: str | None
    error: str | None
