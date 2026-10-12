"""Structured output schemas for the P2 RAG graph and workflow."""

from typing import Literal

from pydantic import BaseModel, Field

RagRetrievalMode = Literal["corpus", "web", "none"]
RagGroundingVerdict = Literal["grounded", "unverified", "none"]


class GradeChunk(BaseModel):
    """Binary relevance grade for one retrieved chunk."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the chunk is relevant to the question, else 'no'.",
    )


class GradeHallucination(BaseModel):
    """Binary hallucination grade for a generated answer."""

    binary_score: Literal["yes", "no"] = Field(
        description="'yes' if the answer is fully grounded in the provided context, else 'no'.",
    )


class RagReport(BaseModel):
    """Structured report returned by the P2 RAG workflow (`run_rag`)."""

    answer: str = Field(
        description="The grounded answer produced from the retrieved chunks."
    )
    citations: list[str] = Field(
        default_factory=list,
        description="Unique corpus paths or web URLs of the chunks backing the answer.",
    )
    retrieval_mode: RagRetrievalMode = Field(
        default="corpus",
        description="Where the chunks came from: the local corpus, the web fallback, or none.",
    )
    grounding_verdict: RagGroundingVerdict = Field(
        default="grounded",
        description="Whether the answer passed the grounding check against its chunks.",
    )
