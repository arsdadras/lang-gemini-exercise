"""Structured output schemas for P4 Sandbox / Interpreter Agent artifacts and execution manifests."""

from typing import Literal

from pydantic import BaseModel, Field

ArtifactType = Literal["csv", "json", "chart", "markdown", "text", "binary", "other"]


class ArtifactMetadata(BaseModel):
    """Metadata describing a generated deliverable artifact."""

    name: str = Field(description="Name or filename of the artifact (e.g. sales_trend.png)")
    path: str = Field(
        description="Relative path to the artifact within the sandbox (e.g. artifacts/sales_trend.png)"
    )
    artifact_type: ArtifactType = Field(
        default="other",
        description="Type of the artifact: csv, json, chart, markdown, text, binary, other",
    )
    description: str = Field(
        default="",
        description="Short description of what this artifact contains or represents",
    )
    size_bytes: int | None = Field(
        default=None,
        description="File size in bytes if known",
    )


class ExecutionManifest(BaseModel):
    """Structured execution manifest summarizing computation results and generated artifacts."""

    summary: str = Field(
        description="Executive summary of the computation, analysis, or transformation performed"
    )
    artifacts: list[ArtifactMetadata] = Field(
        default_factory=list,
        description="List of all deliverable artifacts generated and saved into the artifacts directory",
    )
    success: bool = Field(
        default=True,
        description="Whether the requested computational task succeeded without unhandled errors",
    )
