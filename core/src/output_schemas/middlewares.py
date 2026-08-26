from pydantic import BaseModel, Field
from typing import Literal


class _GroundednessVerdict(BaseModel):
    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the answer is fully grounded in the tool context, else 'no'."
    )
