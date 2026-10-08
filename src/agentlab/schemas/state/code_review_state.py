"""Graph state for the P3 code review and test generation pipeline."""

from typing import NotRequired, TypedDict

from agentlab.schemas.output.code_review_output_schema import (
    CodeReview,
    TestRun,
    TestSuite,
)


class CodeReviewState(TypedDict):
    """State shared by the parent pipeline and its three subgraphs.

    Only ``code`` is required on input; every node returns a partial update.
    ``error`` is the fail-fast channel the routers check before continuing.
    """

    code: str
    language: NotRequired[str]
    file_path: NotRequired[str | None]
    review: NotRequired[CodeReview | None]
    tests: NotRequired[TestSuite | None]
    test_run: NotRequired[TestRun | None]
    test_retries: NotRequired[int]
    refactor_decision: NotRequired[str | None]
    applied_code: NotRequired[str | None]
    error: NotRequired[str | None]
