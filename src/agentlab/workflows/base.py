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

_ENGINE_KW_KEYS = ("engine", "target", "graph", "store", "agent")


class WorkflowRunner[TReport: BaseModel](Protocol):
    """Structural protocol for any domain workflow runner function.

    Guarantees that every runner accepts ``engine`` as its first positional parameter.
    """

    def __call__(
        self,
        engine: Any,
        /,
        *args: Any,
        **kwargs: Any,
    ) -> SpecialistResult[TReport]: ...


@dataclass(frozen=True)
class Specialist[TInput: BaseModel, TReport: BaseModel]:
    """The Particle face of a Rung-2 domain capability (ADR-0033).

    Pairs a typed input_schema and report_schema with the domain workflow's run
    function and thin as_subagent / as_tool adapters.
    """

    name: SpecialistName
    description: str
    input_schema: type[TInput]
    report_schema: type[TReport]
    run: WorkflowRunner[TReport]
    render: Callable[[TReport], str] | None = None
    default_engine: Callable[[], Any] | None = None
    default_target: Callable[[], Any] | None = None

    def _resolve_engine(
        self,
        engine: Any = None,
        kwargs: dict[str, Any] | None = None,
    ) -> tuple[Any, dict[str, Any]]:
        """Resolve the execution engine without runtime reflection hacks."""
        remaining = dict(kwargs or {})
        if engine is not None:
            return engine, remaining
        for key in _ENGINE_KW_KEYS:
            if key in remaining:
                return remaining.pop(key), remaining
        if self.default_engine is not None:
            return self.default_engine(), remaining
        if self.default_target is not None:
            return self.default_target(), remaining
        msg = f"Specialist '{self.name}' requires an engine or default_engine."
        raise ValueError(msg)

    def as_subagent(
        self,
        engine: Any = None,
        *,
        target: Any = None,
        name: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> CompiledSubAgent:
        """Adapt this specialist as a CompiledSubAgent for a Rung-3 coordinator."""
        resolved_engine, run_kwargs = self._resolve_engine(
            engine if engine is not None else target, kwargs
        )
        return specialist_subagent(
            name or self.name,
            description or self.description,
            lambda task: self.run(resolved_engine, task, **run_kwargs),
            render=self.render,
        )

    def as_tool(
        self,
        engine: Any = None,
        *,
        target: Any = None,
        **kwargs: Any,
    ) -> BaseTool:
        """Adapt this specialist as a typed BaseTool for an agent or coordinator."""
        resolved_engine, run_kwargs = self._resolve_engine(
            engine if engine is not None else target, kwargs
        )

        def invoke_tool(**tool_args: Any) -> str:
            result = self.run(resolved_engine, **tool_args, **run_kwargs)
            return result.to_text(render=self.render)

        return StructuredTool.from_function(
            func=invoke_tool,
            name=self.name,
            description=self.description,
            args_schema=self.input_schema,
        )
