"""Structured schemas for P4 sandbox deliverables."""

from typing import Literal

from pydantic import BaseModel, Field

ArtifactType = Literal["csv", "json", "chart", "markdown", "text", "binary", "other"]


class ArtifactMetadata(BaseModel):
    """Metadata describing one deliverable file under the sandbox's ``artifacts/``."""

    name: str = Field(description="File name of the artifact (e.g. sales_trend.png)")
    path: str = Field(
        description="Path relative to the sandbox root (e.g. artifacts/sales_trend.png)",
    )
    artifact_type: ArtifactType = Field(
        default="other",
        description="Type of the artifact: csv, json, chart, markdown, text, binary, other",
    )
    description: str = Field(
        default="",
        description="Short description of what this artifact contains",
    )
    size_bytes: int | None = Field(
        default=None,
        description="File size in bytes, if known",
    )
    modified_at: float | None = Field(
        default=None,
        description="Last modification time (epoch seconds), if known",
    )
