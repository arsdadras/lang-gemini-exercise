"""Typed inputs a caller passes to a specialist."""

from agentlab.schemas.input.code_review_input_schema import CodeReviewInput
from agentlab.schemas.input.interpreter_input_schema import InterpreterInput
from agentlab.schemas.input.personal_context_input_schema import PersonalContextInput
from agentlab.schemas.input.rag_input_schema import RagInput
from agentlab.schemas.input.research_input_schema import (
    Depth,
    ResearchInput,
    ResearchOptions,
)

__all__ = [
    "CodeReviewInput",
    "Depth",
    "InterpreterInput",
    "PersonalContextInput",
    "RagInput",
    "ResearchInput",
    "ResearchOptions",
]
