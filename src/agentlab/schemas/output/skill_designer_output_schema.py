"""Structured output of the P5 skill designer."""

from pydantic import BaseModel, Field


class SkillDraft(BaseModel):
    """A procedural skill for the shared library, in the Agent Skills format."""

    name: str = Field(
        pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$",
        max_length=64,
        description="Lowercase words joined by hyphens, e.g. 'weekly-review'.",
    )
    description: str = Field(
        max_length=1024,
        description="When to use the skill and what it does, in one or two sentences.",
    )
    instructions: str = Field(
        description="The skill body in Markdown: a '## When to Use' section, then numbered steps.",
    )

    def to_markdown(self) -> str:
        return f"---\nname: {self.name}\ndescription: {self.description}\n---\n\n{self.instructions.strip()}\n"
