"""Structured output schema for the research agent."""

from pydantic import BaseModel, Field


class Source(BaseModel):
    """A single cited source."""

    title: str = Field(description="Title of the source page")
    url: str = Field(description="URL the claim came from")


class ResearchReport(BaseModel):
    """Structured, cited research report."""

    topic: str = Field(description="The topic that was researched")
    summary: str = Field(description="2-3 sentence executive summary")
    key_findings: list[str] = Field(description="Bullet-point findings")
    sources: list[Source] = Field(description="Sources cited across findings")
    confidence: float = Field(
        ge=0,
        le=1,
        description="0 to 1, based on how much sources agree",
    )
