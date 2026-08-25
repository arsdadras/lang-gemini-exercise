from pydantic import BaseModel, Field
from typing import Literal


class GradeDocument(BaseModel):
    """Binary relevance grade for one retrieved document."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the document is relevant to the question, else 'no'."
    )


class GradeHallucination(BaseModel):
    """Binary hallucination grade for a generated answer."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the answer is fully grounded in the provided context, else 'no'."
    )


class _GroundednessVerdict(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the answer is fully grounded in the tool context, else 'no'."
    )
