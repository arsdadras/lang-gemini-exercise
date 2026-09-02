"""Unit tests for P3 Phase A reference components."""
import sys
from pathlib import Path

ref_path = str(Path(__file__).resolve().parents[1] / "reference")
if ref_path not in sys.path:
    sys.path.append(ref_path)

from output_schemas import CodeIssue, ReviewResult, TestCase, TestSuite
from graph import route_after_review

def test_p3_schema_creation():
    issue = CodeIssue(severity="warning", category="style", description="missing type hints", suggestion="add types")
    review = ReviewResult(summary="looks ok", score=7, issues=[issue])
    assert review.score == 7
    assert len(review.issues) == 1

def test_p3_route_after_review():
    assert route_after_review({"error": "some exception"}) == "__end__"
    assert route_after_review({"error": None}) == "generate_tests"
