"""Structured output of the P5 memory consolidator: line-level edits, not rewritten files."""

from typing import Literal

from pydantic import BaseModel, Field


class MemoryEdit(BaseModel):
    """One change to one memory file. Code decides how it lands in the file."""

    kind: Literal["add", "replace", "remove"]
    path: str = Field(description="Full path under /memories/, e.g. /memories/user_profile.md.")
    section: str = Field(
        default="",
        description="add: the heading to add under, e.g. '## Preferences'. Empty for a new file.",
    )
    old: str = Field(default="", description="replace/remove: one existing line, copied exactly.")
    new: str = Field(
        default="",
        description="add/replace: the new line. For add to a file that doesn't exist, its full content.",
    )
    reason: str = Field(description="What the user said that shows this change.")

    def describe(self) -> str:
        if self.kind == "add":
            return f"{self.path}: + {self.new}"
        if self.kind == "replace":
            return f"{self.path}: {self.old} -> {self.new}"
        return f"{self.path}: - {self.old}"


class MemoryEdits(BaseModel):
    """The edits a finished conversation makes to memory; empty when nothing changes."""

    edits: list[MemoryEdit] = Field(default_factory=list)
