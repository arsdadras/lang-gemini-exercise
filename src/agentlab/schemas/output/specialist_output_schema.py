"""The specialist contract: one result envelope every specialist returns to its callers.

The envelope keeps what a caller needs to decide (did it work, where did the answer come
from, what changed) apart from the answer itself, whose type differs per specialist.
"""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Literal

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from langchain_core.tools import BaseTool, StructuredTool
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


@dataclass(frozen=True)
class Specialist[TInput: BaseModel, TReport: BaseModel]:
    """The Particle face of a Rung-2 domain capability (ADR-0033).

    Pairs a typed ``input_schema`` and ``report_schema`` with the domain workflow's ``run``
    function and thin ``as_subagent`` / ``as_tool`` adapters, without wrapping Rung-1
    ``CompiledStateGraph`` objects in a custom OOP base class.
    """

    name: str
    description: str
    input_schema: type[TInput]
    report_schema: type[TReport]
    run: Callable[..., SpecialistResult[TReport]]
    render: Callable[[TReport], str] | None = None
    subagent_factory: Callable[..., CompiledSubAgent] | None = None

    def as_subagent(self, **kwargs: Any) -> CompiledSubAgent:
        """Adapt this specialist as a ``CompiledSubAgent`` for a Rung-3 coordinator."""
        if self.subagent_factory is not None:
            return self.subagent_factory(**kwargs)

        def delegate(state: dict[str, Any]) -> dict[str, Any]:
            last = state["messages"][-1]
            content = getattr(last, "content", last)
            task = content if isinstance(content, str) else str(content)
            result = self.run(task, **kwargs)
            return {"messages": [AIMessage(content=result.to_text(render=self.render))]}

        return {
            "name": self.name,
            "description": self.description,
            "runnable": RunnableLambda(delegate),
        }

    def as_tool(self, **kwargs: Any) -> BaseTool:
        """Adapt this specialist as a typed ``BaseTool`` for an agent or coordinator."""

        def invoke_tool(**tool_args: Any) -> str:
            result = self.run(**tool_args, **kwargs)
            return result.to_text(render=self.render)

        return StructuredTool.from_function(
            func=invoke_tool,
            name=self.name,
            description=self.description,
            args_schema=self.input_schema,
        )
