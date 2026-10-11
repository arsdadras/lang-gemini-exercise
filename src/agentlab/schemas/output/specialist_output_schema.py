"""The specialist contract: one result envelope every specialist returns to its callers.

The envelope keeps what a caller needs to decide (did it work, where did the answer come
from, what changed) apart from the answer itself, whose type differs per specialist.
"""

from collections.abc import Callable
from typing import Literal

from pydantic import BaseModel, Field

from agentlab.schemas.output.research_output_schema import SourceKind


class Provenance(BaseModel):
    """Where part of an answer came from."""

    kind: SourceKind | Literal["memory", "sandbox"]
    ref: str = Field(description="A URL, or a path in the corpus, memory, or sandbox.")
    title: str = ""


class SideEffect(BaseModel):
    """Something the specialist changed outside its own run."""

    action: Literal["created", "modified", "deleted"]
    target: str
    description: str = ""


SpecialistStatus = Literal["ok", "partial", "failed"]


class SpecialistResult[T](BaseModel):
    """What a specialist returns: how its work ended, the answer, its sources, and its changes.

    ``status`` is decided by code from facts in the specialist's final state, never by the
    model's opinion of its own work.

    - ``ok``: the job is done.
    - ``partial``: the job isn't fully done, and ``reason`` says what's missing: the answer came
      from a fallback, or the run stopped at an approval. ``output`` holds whatever is usable.
    - ``failed``: no usable answer; ``reason`` says why.
    """

    specialist: str
    status: SpecialistStatus
    reason: str = ""
    output: T | None = None
    provenance: list[Provenance] = Field(default_factory=list)
    side_effects: list[SideEffect] = Field(default_factory=list)

    def to_text(self, render: Callable[[T], str] | None = None) -> str:
        """The envelope as text for a model caller: status and sources first, then the answer."""
        status = self.status + (f" ({self.reason})" if self.reason else "")
        lines = [f"[{self.specialist}] status: {status}"]
        if self.provenance:
            lines.append(
                "Sources: "
                + "; ".join(f"{p.kind}: {p.title or p.ref}" for p in self.provenance)
            )
        if self.side_effects:
            lines.append(
                "Changed: "
                + "; ".join(f"{e.action} {e.target}" for e in self.side_effects)
            )
        if self.output is not None:
            if render is not None:
                body = render(self.output)
            elif isinstance(self.output, BaseModel):
                body = self.output.model_dump_json(indent=2)
            else:
                body = str(self.output)
            lines.extend(["", body])
        return "\n".join(lines)
