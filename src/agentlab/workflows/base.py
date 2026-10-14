"""Foundational contracts and descriptors for the Rung-2 domain workflows (ADR-0033)."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from deepagents import CompiledSubAgent
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel

from agentlab.schemas.output.specialist_output_schema import (
    SpecialistName,
    SpecialistResult,
)
from agentlab.utils.subagent_util import specialist_subagent


class WorkflowRunner[TEngine, TReport: BaseModel](Protocol):
    """Structural protocol for any domain workflow runner function (ADR-0033).

    Guarantees that every domain runner (``run_*``) accepts ``engine`` as its first
    positional parameter.
    """

    def __call__(
        self,
        engine: TEngine,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> SpecialistResult[TReport]: ...


@dataclass(frozen=True)
class Specialist[TInput: BaseModel, TReport: BaseModel]:
    """The Particle face of a Rung-2 domain capability (ADR-0033).

    A Specialist is pre-bound to its execution engine (or a lazy factory).
    It exposes a clean task-level interface to coordinators and tools without
    leaking internal engine types or requiring runtime keyword reflection.
    """

    name: SpecialistName
    description: str
    input_schema: type[TInput]
    report_schema: type[TReport]
    run: Callable[..., SpecialistResult[TReport]]
    render: Callable[[TReport], str] | None = None

    def as_subagent(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> CompiledSubAgent:
        """Adapt this specialist as a CompiledSubAgent for a Rung-3 coordinator."""
        return specialist_subagent(
            name or self.name,
            description or self.description,
            lambda task: self.run(task, **kwargs),
            render=self.render,
        )

    def as_tool(self, **kwargs: Any) -> BaseTool:
        """Adapt this specialist as a typed BaseTool for an agent or coordinator."""

        def invoke_tool(**tool_args: Any) -> str:
            result = self.run(**tool_args, **kwargs)
            return result.to_text(render=self.render)

        return StructuredTool.from_function(
            func=invoke_tool,
            name=self.name,
            description=self.description,
            args_schema=self.input_schema,
        )
