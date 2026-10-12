"""The Particle face of a Rung-2 domain capability: ``Specialist[TInput, TReport]`` (ADR-0033)."""

import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel

from agentlab.schemas.output.specialist_output_schema import (
    SpecialistName,
    SpecialistResult,
)
from agentlab.utils.subagent_util import specialist_subagent


@dataclass(frozen=True)
class Specialist[TInput: BaseModel, TReport: BaseModel]:
    """The Particle face of a Rung-2 domain capability (ADR-0033).

    Pairs a typed ``input_schema`` and ``report_schema`` with the domain workflow's ``run``
    function and thin ``as_subagent`` / ``as_tool`` adapters, without wrapping Rung-1
    ``CompiledStateGraph`` objects in a custom OOP base class.
    """

    name: SpecialistName
    description: str
    input_schema: type[TInput]
    report_schema: type[TReport]
    run: Callable[..., SpecialistResult[TReport]]
    render: Callable[[TReport], str] | None = None
    default_target: Callable[[], Any] | None = None

    def _resolve_target(
        self,
        target: Any,
        kwargs: dict[str, Any],
    ) -> tuple[Any, dict[str, Any]]:
        remaining = dict(kwargs)
        if target is not None:
            return target, remaining
        first_param = next(iter(inspect.signature(self.run).parameters), None)
        if first_param is not None and first_param in remaining:
            return remaining.pop(first_param), remaining
        if self.default_target is not None:
            return self.default_target(), remaining
        msg = f"Specialist '{self.name}' requires a target or default_target."
        raise ValueError(msg)

    def as_subagent(
        self,
        target: Any = None,
        *,
        name: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> CompiledSubAgent:
        """Adapt this specialist as a ``CompiledSubAgent`` for a Rung-3 coordinator."""
        resolved_target, run_kwargs = self._resolve_target(target, kwargs)
        return specialist_subagent(
            name or self.name,
            description or self.description,
            lambda task: self.run(resolved_target, task, **run_kwargs),
            render=self.render,
        )

    def as_tool(self, target: Any = None, **kwargs: Any) -> BaseTool:
        """Adapt this specialist as a typed ``BaseTool`` for an agent or coordinator."""
        resolved_target, run_kwargs = self._resolve_target(target, kwargs)

        def invoke_tool(**tool_args: Any) -> str:
            result = self.run(resolved_target, **tool_args, **run_kwargs)
            return result.to_text(render=self.render)

        return StructuredTool.from_function(
            func=invoke_tool,
            name=self.name,
            description=self.description,
            args_schema=self.input_schema,
        )
