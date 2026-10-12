"""Structured schemas for P4 sandbox deliverables."""

from typing import Literal

from pydantic import BaseModel, Field

DeliverableType = Literal["csv", "json", "chart", "markdown", "text", "binary", "other"]


class Deliverable(BaseModel):
    """Metadata describing one deliverable file under the sandbox's ``deliverables/``."""

    name: str = Field(description="File name of the deliverable (e.g. sales_trend.png)")
    path: str = Field(
        description="Path relative to the sandbox root (e.g. deliverables/sales_trend.png)",
    )
    deliverable_type: DeliverableType = Field(
        default="other",
        description="Type of the deliverable: csv, json, chart, markdown, text, binary, other",
    )
    description: str = Field(
        default="",
        description="Short description of what this deliverable contains",
    )
    size_bytes: int | None = Field(
        default=None,
        description="File size in bytes, if known",
    )
    modified_at: float | None = Field(
        default=None,
        description="Last modification time (epoch seconds), if known",
    )


class InterpreterReport(BaseModel):
    """Structured report returned by the P4 interpreter workflow (`run_interpreter`)."""

    answer: str = Field(description="Final text response from the interpreter run.")
    executed_commands: list[str] = Field(
        default_factory=list,
        description="Shell commands executed in the sandbox during the run.",
    )
    deliverables: list[str] = Field(
        default_factory=list,
        description="Relative sandbox paths of deliverables created or modified during the run.",
    )
