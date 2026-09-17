"""Structured output schemas used by agent middlewares."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GroundednessVerdict(BaseModel):
    """Binary verdict on whether a final answer is supported by tool outputs."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the answer is fully grounded in the tool context, else 'no'."
    )


class FinglishLines(BaseModel):
    """Lines rewritten into Finglish, one output line per input line."""

    lines: list[str] = Field(description="The rewritten lines, in the same number and order as the input.")


class GuardVerdict(BaseModel):
    """A security guard's decision on one action, judged against a policy."""

    model_config = ConfigDict(frozen=True)

    decision: Literal["allow", "ask", "block"] = Field(
        description=(
            "'allow' to proceed, 'ask' when the user must approve, "
            "'block' when the policy never allows it."
        )
    )
    category: str = Field(description="The policy category that applies, or 'none' when allowing.")
    reason: str = Field(description="One short sentence, addressed to the user, explaining the decision.")
