"""Structured output schema for the P4 Interpreter and Analysis Agent."""

from pydantic import BaseModel, Field


class AnalysisReport(BaseModel):
    """Structured final report produced by the data analysis agent."""

    title: str = Field(description="Concise, descriptive title of the analytical task")
    executive_summary: str = Field(
        description="2-3 sentence executive summary of key analytical findings"
    )
    metrics: dict[str, float | int | str] = Field(
        default_factory=dict,
        description="Key computed quantitative metrics (e.g. {'average_salary': 87500.0})",
    )
    insights: list[str] = Field(
        default_factory=list,
        description="Key observations, trends, or insights discovered in data",
    )
    artifacts_created: list[str] = Field(
        default_factory=list,
        description="Relative paths to files/artifacts created in the sandbox (e.g. ['data.csv'])",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Actionable recommendations or next steps based on analysis",
    )
