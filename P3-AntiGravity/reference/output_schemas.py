"""Reference schemas for P3 Code Review."""
from typing import Literal
from pydantic import BaseModel, Field

class CodeIssue(BaseModel):
    line_number: int | None = Field(default=None, description="Line number")
    severity: Literal["critical", "warning", "info"] = Field(description="Severity")
    category: Literal["bug", "security", "performance", "style", "maintainability"] = Field(description="Category")
    description: str = Field(description="Description")
    suggestion: str = Field(description="Suggestion")

class ReviewResult(BaseModel):
    summary: str = Field(description="Summary")
    score: int = Field(ge=1, le=10, description="Score")
    issues: list[CodeIssue] = Field(default_factory=list, description="Issues")
    refactored_code: str | None = Field(default=None, description="Refactored code")

class TestCase(BaseModel):
    name: str = Field(description="Test name")
    description: str = Field(description="Test description")
    target_function: str = Field(description="Target function")

class TestSuite(BaseModel):
    framework: str = Field(default="pytest", description="Framework")
    test_code: str = Field(description="Test code")
    test_cases: list[TestCase] = Field(default_factory=list, description="Test cases")

class TestExecutionResult(BaseModel):
    status: Literal["passed", "failed", "error", "timed_out"]
    passed: bool
    exit_code: int
    output: str

