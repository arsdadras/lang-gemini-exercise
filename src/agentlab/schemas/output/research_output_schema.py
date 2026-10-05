"""Structured output schemas for the research agent and its checked report.

The agent writes a ``ResearchDraft``: claims, each with the page passages it rests on. Code
checks every claim against the pages the agent actually read and builds the ``ResearchReport``,
so a claim's ``status`` and the report's ``confidence`` are never the model's own opinion
(ADR-0026: code decides status).
"""

from typing import Literal

from pydantic import BaseModel, Field


class Source(BaseModel):
    """A single cited source."""

    title: str = Field(description="Title of the source page")
    url: str = Field(description="URL the claim came from")


class Evidence(BaseModel):
    """A page passage a claim rests on."""

    url: str = Field(description="URL of a page you read with read_page")
    passage: str = Field(description="The passage of that page that supports the claim")


class DraftClaim(BaseModel):
    """One factual claim of the report, with the evidence the agent cites for it."""

    text: str = Field(description="One factual claim, stated so a reader can verify it")
    evidence: list[Evidence] = Field(
        description="Passages of pages you read that support this claim; at least one"
    )


class ResearchDraft(BaseModel):
    """What the research agent returns: claims with cited evidence, before any check."""

    topic: str = Field(description="The topic that was researched")
    summary: str = Field(description="2-3 sentence executive summary")
    claims: list[DraftClaim] = Field(description="The findings, one claim each")
    sources: list[Source] = Field(description="Sources cited across claims")


ClaimStatus = Literal["supported", "contradicted", "unsupported"]


class Claim(BaseModel):
    """A claim after the check: ``status`` is set by code from what the cited pages say."""

    text: str
    evidence: list[Evidence]
    status: ClaimStatus
    supporting_urls: list[str] = Field(default_factory=list)


class ResearchReport(BaseModel):
    """The checked report. ``confidence`` is derived from the claims, never written by a model."""

    topic: str
    summary: str
    claims: list[Claim]
    sources: list[Source]
    confidence: float = Field(
        ge=0,
        le=1,
        description="From the claim table: how many claims their pages support, and how many "
        "independent pages agree",
    )


class ClaimVerdict(BaseModel):
    """The LLM's verdict on one claim and one source, when the decider isn't sure."""

    verdict: Literal["supports", "contradicts", "none"] = Field(
        description="supports: the source states the claim. contradicts: it states the opposite. "
        "none: it doesn't address the claim, or only mentions the same subject."
    )


class ResearchFindings(BaseModel):
    """Structured findings returned by the researcher subagent."""

    sub_question: str = Field(description="The specific sub-question researched")
    answer: str = Field(description="Concise answer to the sub-question")
    sources: list[Source] = Field(description="Sources backing the answer")
