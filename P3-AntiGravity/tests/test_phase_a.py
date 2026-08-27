"""Unit tests for P3 Phase A reference components."""
from P3_AntiGravity.reference.output_schemas import CodeIssue, ReviewResult, TestCase, TestSuite
from P3_AntiGravity.reference.graph import route_after_review

def test_p3_schema_creation():
    issue = CodeIssue(severity="warning", category="style", description="missing type hints", suggestion="add types")
    review = ReviewResult(summary="looks ok", score=7, issues=[issue])
    assert review.score == 7
    assert len(review.issues) == 1

def test_p3_route_after_review():
    assert route_after_review({"error": "some exception"}) == "__end__"
    assert route_after_review({"error": None}) == "generate_tests"
