"""What a caller asks of the P3 code-review specialist: ``CodeReviewInput``."""

from pydantic import BaseModel, Field


class CodeReviewInput(BaseModel):
    """Typed input for the P3 code-review specialist."""

    code: str = Field(description="Source code to review and test.")
    language: str = Field(
        default="python",
        description="Programming language of the source code (defaults to 'python').",
    )
