"""Structured output schemas for P3 Code Review & Test Generation."""

from typing import Literal

from pydantic import BaseModel, Field


class CodeIssue(BaseModel):
    """A specific issue or suggestion found in the code."""

    line_number: int | None = Field(
        default=None,
        description="Approximate line number where the issue was found, if applicable.",
    )
    severity: Literal["critical", "warning", "info"] = Field(
        description="Severity level of the issue.",
    )
    category: Literal["bug", "security", "performance", "style", "maintainability"] = (
        Field(
            description="Category classification of the issue.",
        )
    )
    description: str = Field(
        description="Detailed explanation of the issue or concern.",
    )
    suggestion: str = Field(
        description="Actionable suggestion or recommendation to fix/improve it.",
    )


class ReviewResult(BaseModel):
    """Overall structured review findings for a given code file or snippet."""

    summary: str = Field(
        description="High-level overview of code quality, strengths, and primary concerns.",
    )
    score: int = Field(
        description="Overall quality score from 1 (poor) to 10 (exemplary).",
        ge=1,
        le=10,
    )
    issues: list[CodeIssue] = Field(
        default_factory=list,
        description="List of detected code issues or improvement points.",
    )
    refactored_code: str | None = Field(
        default=None,
        description="Optional full refactored version of the code incorporating fixes, if appropriate.",
    )


class TestCase(BaseModel):
    """An individual test case specification."""

    name: str = Field(
        description="Identifier name of the test function (e.g. 'test_valid_login').",
    )
    description: str = Field(
        description="Description of what this test case verifies (e.g. edge cases, happy path).",
    )
    target_function: str = Field(
        description="Name of the specific function or class being tested.",
    )


class TestSuite(BaseModel):
    """Generated test suite containing complete runnable tests."""

    framework: str = Field(
        default="pytest",
        description="Testing framework used (e.g. 'pytest', 'unittest').",
    )
    test_code: str = Field(
        description="Complete, valid, ready-to-run Python test file contents.",
    )
    test_cases: list[TestCase] = Field(
        default_factory=list,
        description="List of test cases included in the suite.",
    )


class TestExecutionResult(BaseModel):
    """Execution results from running the test suite in the sandbox."""

    status: Literal["passed", "failed", "error", "timed_out"] = Field(
        description="Outcome status of sandbox execution.",
    )
    passed: bool = Field(
        description="True if all tests passed successfully with return code 0.",
    )
    exit_code: int = Field(
        description="Process exit code from pytest execution.",
    )
    output: str = Field(
        description="Full captured stdout and stderr from the test run.",
    )


class CodeReviewOutcome(BaseModel):
    """Everything the P3 pipeline produced for one piece of code."""

    review: ReviewResult
    tests: TestSuite | None = None
    test_execution: TestExecutionResult | None = None
    applied_code: str | None = None
