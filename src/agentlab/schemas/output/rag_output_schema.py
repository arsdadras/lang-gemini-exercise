"""Structured output schemas for the P2 RAG graph's grading nodes."""

from typing import Literal

from pydantic import BaseModel, Field


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
