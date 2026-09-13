"""Structured output schemas used by agent middlewares."""

from typing import Literal

from pydantic import BaseModel, Field


class GroundednessVerdict(BaseModel):
    """Binary verdict on whether a final answer is supported by tool outputs."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the answer is fully grounded in the tool context, else 'no'."
    )
