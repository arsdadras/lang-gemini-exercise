"""The specialist contract: one result envelope every specialist returns to its callers.

The envelope keeps what a caller needs to decide (did it work, where did the answer come
from, what changed) apart from the answer itself, whose type differs per specialist.
"""

from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, Field


class Provenance(BaseModel):
    kind: Literal["web", "corpus", "memory", "sandbox"]
    ref: str = Field(description="A URL, or a path in the corpus, memory, or sandbox.")
    title: str = Field(description="The title of the source document.", default="")


class SideEffect(BaseModel):
    """Side effects are the changes made to the environment by the specialist outside its own run."""

    action: Literal["created", "updated", "deleted"]
    target: str = Field(description="The path of the target file or directory.")
    description: str = Field(
        description="A brief description of the change.",
        default="",
    )


class SpecialistResult[T](BaseModel):
    """What a Specialist returns: how its work ended, the answer, its sources, and its changes.
    ``status`` is decideded by code from facts in the specialist's final state, never by the model's opinion of its own work.
    - ``success``: the job is done.
    - ``partial``: the job is done, but there are some issues.
    - ``failure``: the job is not done, and there are some issues.
    - ``timeout``: the job is not done, and there are some issues.
    - ``error``: the job is not done, and there are some issues.
    """

    specialist: str = Field(
        description="The name of the specialist that returned the result.",
    )
    status: Literal["success", "partial", "failure", "timeout", "error"]
    reason: str = Field(description="The reason for the status.", default="")
    output: T | None = Field(
        description="The output of the specialist, if any.",
        default=None,
    )
    provenance: list[Provenance] = Field(
        description="The sources of the answer.",
        default_factory=list,
    )
    side_effects: list[SideEffect] = Field(
        description="The side effects of the work.",
        default_factory=list,
    )

    def to_text(self, render: Callable[[T], str]) -> str:
        """The envelope as text for a model caller: Status and Sources first, then the Answer."""

        status = self.status + (f" ({self.reason})" if self.reason else "")
        lines = [f"[{self.specialist}] status: {status}"]
        if self.provenance:
            sources = [f"{p.kind}: {p.title or p.ref}" for p in self.provenance]
            lines.append("Sources: " + "; ".join(sources))
        if self.side_effects:
            side_effects = [f"{e.action} {e.target}" for e in self.side_effects]
            lines.append("Changed: " + "; ".join(side_effects))
        if self.output is not None:
            if render is not None:
                body = render(self.output)
            elif isinstance(self.output, BaseModel):
                body = self.output.model_dump_json(indent=2)
            else:
                body = str(self.output)
            lines.extend(["", body])
        return "\n".join(lines)
