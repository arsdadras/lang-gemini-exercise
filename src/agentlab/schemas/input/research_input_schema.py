"""What a caller asks of the P1 researcher: ``ResearchOptions`` (R1 topic 2)."""

from typing import Literal

from pydantic import BaseModel, Field

from agentlab.schemas.output.research_output_schema import SourceKind

Depth = Literal["quick", "standard", "deep"]


class ResearchOptions(BaseModel):
    """How to research a topic. Defaults reproduce a standard web research run."""

    depth: Depth = Field(
        default="standard",
        description="Sets the budget (configs/research_config.py DEPTH_BUDGETS): how many "
        "sub-questions, and searches, page reads, and claims each may spend",
    )
    recency: Literal["day", "week", "month", "year"] | None = Field(
        default=None, description="Only pages published within this window"
    )
    include_domains: list[str] = Field(
        default_factory=list, description="Search and read only these domains"
    )
    exclude_domains: list[str] = Field(
        default_factory=list, description="Never search or read these domains"
    )
    source_type: Literal["general", "news"] = Field(
        default="general",
        description="The kind of web source: general pages, or news",
    )
    sources: list[SourceKind] | None = Field(
        default=None,
        description="The sources this research may use; the router picks among them per "
        "sub-question (R1 topic 3). None: every source that is available",
    )
    corpus_files: list[str] = Field(
        default_factory=list,
        description="Paths of .txt or .md files to research as the corpus source; empty "
        "means this project's own docs and code",
    )
    language: str = Field(
        default="English", description="Language of the claims and the summary"
    )
    output: Literal["answer", "fact_pool"] = Field(
        default="answer",
        description="answer: claims that answer the topic and a short answer as the summary. "
        "fact_pool: as many distinct facts as the budget allows, for a caller such as P6",
    )
