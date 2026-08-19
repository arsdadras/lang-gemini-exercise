"""Structured output schema for the research agent."""

from pydantic import BaseModel, Field


class Source(BaseModel):
    """a single cited source"""

    title: str = Field(description="Title of the source page")
    url: str = Field(description="URL of the claimed source")


class ResearchReport(BaseModel):
    topic: str = Field(description="The topic being researched")
    summary: str = Field(description="A comprehensive summary of the research")
    sources: list[Source] = Field(description="A list of cited sources across findings")
    key_findings: list[str] = Field(
        description="Bullet-point findings from the research"
    )
    confidence: float = Field(le=1, ge=0, description="Confidence score of the report")
