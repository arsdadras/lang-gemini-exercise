"""Unit tests for P3 Code Review & Test Generation components."""

from output_schemas.code_review import (
    CodeIssue,
    ReviewResult,
    TestCase,
    TestSuite,
    TestExecutionResult,
)
from state.code_review import CodeReviewState
from graphs.code_review import route_after_review, route_after_test_gen, build_code_review_graph
from utils.sandbox import run_tests_in_sandbox


def test_code_review_schemas():
    """Verify instantiation and validation of P3 schemas."""
    issue = CodeIssue(
        line_number=5,
        severity="critical",
        category="bug",
        description="Index out of range",
        suggestion="Add bounds check",
    )
    assert issue.severity == "critical"

    review = ReviewResult(
        summary="Found 1 critical bug",
        score=4,
        issues=[issue],
        refactored_code="def safe(): pass",
    )
    assert review.score == 4
    assert len(review.issues) == 1

    tc = TestCase(
        name="test_bounds",
        description="Verify list bounds check",
        target_function="get_item",
    )
    suite = TestSuite(
        framework="pytest",
        test_code="def test_bounds(): assert True",
        test_cases=[tc],
    )
    assert suite.framework == "pytest"


def test_graph_routing():
    """Verify conditional edges logic in the code review graph."""
    # Review routing
    assert route_after_review({"error": "Failed API"}) == "__end__"
    assert route_after_review({"error": None}) == "generate_tests"

    # Test generation routing
    assert route_after_test_gen({"error": "Failed test gen", "tests": None}) == "__end__"
    assert route_after_test_gen({"error": None, "tests": None}) == "__end__"
    assert route_after_test_gen({"error": None, "tests": TestSuite(test_code="pass", test_cases=[])}) == "execute_tests"


def test_sandbox_execution():
    """Verify local subprocess sandbox execution for passing and failing test code."""
    source_code = "def is_even(n: int) -> bool:\n    return n % 2 == 0\n"

    # 1. Passing test
    pass_test = "from tested_module import is_even\ndef test_even():\n    assert is_even(4) is True\n"
    res_pass = run_tests_in_sandbox(code=source_code, test_code=pass_test)
    assert res_pass.passed is True
    assert res_pass.status == "passed"
    assert res_pass.exit_code == 0

    # 2. Failing test
    fail_test = "from tested_module import is_even\ndef test_even():\n    assert is_even(3) is True\n"
    res_fail = run_tests_in_sandbox(code=source_code, test_code=fail_test)
    assert res_fail.passed is False
    assert res_fail.status == "failed"
    assert res_fail.exit_code != 0
