"""Structured output schema for the P5 personal context workflow (`run_personal_context`)."""

from pydantic import BaseModel, Field


class PersonalContextReport(BaseModel):
    """Structured snapshot of a user's long-term memory and active skills."""

    profile_summary: str = Field(
        default="",
        description="Redacted summary of the user's profile and stored memory.",
    )
    relevant_facts: list[str] = Field(
        default_factory=list,
        description="Fact and bullet items extracted from the user's memory files.",
    )
    active_preferences: dict[str, str] = Field(
        default_factory=dict,
        description="Active preferences and constraints extracted from the user's memory.",
    )
    active_skills: list[str] = Field(
        default_factory=list,
        description="Names of available procedural skills in the store.",
    )
    files: dict[str, str] = Field(
        default_factory=dict,
        description="Redacted memory file contents keyed by virtual path (`/memories/...`).",
    )
