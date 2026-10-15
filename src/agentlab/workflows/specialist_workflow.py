"""Rung-2 workflow framework: ``SpecialistSpec``, ``ResultNode``, and graph-native ``Workflow`` (ADR-0033)."""

from __future__ import annotations

import operator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    NotRequired,
    Protocol,
    TypedDict,
    TypeVar,
    runtime_checkable,
)

from deepagents import CompiledSubAgent
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel

from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SideEffect,
    SpecialistName,
    SpecialistResult,
    SpecialistStatus,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.subagent_util import (
    new_delegation_config,
    pending_approvals,
    specialist_subagent,
)

TInput = TypeVar("TInput", bound=BaseModel)
TReport = TypeVar("TReport", bound=BaseModel)


@runtime_checkable
class WorkflowRunner(Protocol):
    """Structural protocol for any domain workflow runner function (ADR-0033)."""

    def __call__(self, *args: Any, **kwargs: Any) -> Any: ...


class WorkflowOutputState[TReport: BaseModel](TypedDict):
    """Strict OutputState schema for every Rung-2 workflow graph."""

    result: SpecialistResult[TReport]


class WorkflowOverallState[TReport: BaseModel](TypedDict):
    """Standardized channels read by ``ResultNode`` at the end of a Rung-2 workflow graph."""

    report: NotRequired[TReport | dict[str, Any] | None]
    problems: NotRequired[Annotated[list[str], operator.add]]
    provenance: NotRequired[Annotated[list[Provenance], operator.add]]
    side_effects: NotRequired[Annotated[list[SideEffect], operator.add]]
    result: NotRequired[SpecialistResult[TReport]]


@dataclass(frozen=True)
class SpecialistSpec[TInput: BaseModel, TReport: BaseModel]:
    """Declarative I/O specification (ID card) of a Rung-2 specialist.

    Exposes only external input/output contracts—never internal engines or graphs.
    """

    name: SpecialistName
    description: str
    input_schema: type[TInput]
    report_schema: type[TReport]


class ResultNode[TInput: BaseModel, TReport: BaseModel]:
    """Reusable terminal graph node (like LangGraph's ``ToolNode``) that packs ``SpecialistResult``.

    Reads ``report``, ``problems``, ``provenance``, and ``side_effects`` from
    ``WorkflowOverallState`` and writes ``{"result": SpecialistResult[TReport]}``.
    """

    def __init__(
        self,
        spec: SpecialistSpec[TInput, TReport],
        *,
        empty_reason: str | None = None,
    ) -> None:
        self.spec = spec
        self.empty_reason = empty_reason or f"No {spec.name} report was produced."

    def __call__(
        self,
        state: Any,
    ) -> WorkflowOutputState[TReport]:
        raw_report = state.get("report")
        raw_problems = state.get("problems") or []
        problems = [str(p).strip() for p in raw_problems if str(p).strip()]
        reason = " ".join(dict.fromkeys(problems))
        side_effects = list(state.get("side_effects") or [])
        waiting = pending_approvals(state) if isinstance(state, dict) else ""

        if raw_report is None:
            is_waiting = bool(waiting) or "waiting for approval" in reason
            status: SpecialistStatus = "partial" if is_waiting else "failed"
            return {
                "result": SpecialistResult[TReport](
                    specialist=self.spec.name,
                    status=status,
                    reason=reason or self.empty_reason,
                    output=None,
                    provenance=[],
                    side_effects=side_effects,
                )
            }

        report: TReport = (
            raw_report
            if isinstance(raw_report, self.spec.report_schema)
            else self.spec.report_schema.model_validate(raw_report)
        )
        ok_status: SpecialistStatus = "partial" if problems else "ok"
        return {
            "result": SpecialistResult[TReport](
                specialist=self.spec.name,
                status=ok_status,
                reason=reason,
                output=report,
                provenance=list(state.get("provenance") or []),
                side_effects=side_effects,
            )
        }


class Workflow[TInput: BaseModel, TReport: BaseModel](ABC):
    """Active Rung-2 domain workflow that compiles a StateGraph ending in ``ResultNode``."""

    spec: SpecialistSpec[TInput, TReport]
    _compiled_graph: CompiledStateGraph | None = None

    @property
    def name(self) -> SpecialistName:
        return self.spec.name

    @property
    def description(self) -> str:
        return self.spec.description

    @property
    def input_schema(self) -> type[TInput]:
        return self.spec.input_schema

    @property
    def report_schema(self) -> type[TReport]:
        return self.spec.report_schema

    @property
    def pack_node(self) -> ResultNode[TInput, TReport]:
        """Terminal ``ResultNode`` bound to this workflow's ``SpecialistSpec``."""
        return ResultNode(self.spec)

    @abstractmethod
    def build_graph(self) -> CompiledStateGraph:
        """Assemble and compile the workflow's StateGraph ending in ``self.pack_node``."""

    @property
    def graph(self) -> CompiledStateGraph:
        """Lazy compiled StateGraph (nothing is built at import time)."""
        if self._compiled_graph is None:
            self._compiled_graph = self.build_graph()
        return self._compiled_graph

    def coerce_input(self, inputs: TInput | dict[str, Any] | str | None) -> TInput:
        """Normalize a raw task string, dict, or ``TInput`` model into ``TInput``."""
        if inputs is None:
            return self.spec.input_schema.model_validate({})
        if isinstance(inputs, self.spec.input_schema):
            return inputs
        if isinstance(inputs, dict):
            return self.spec.input_schema.model_validate(inputs)
        first_field = next(iter(self.spec.input_schema.model_fields))
        return self.spec.input_schema.model_validate({first_field: str(inputs)})

    def invoke(
        self,
        inputs: TInput | dict[str, Any] | str | None = None,
        config: RunnableConfig | None = None,
    ) -> WorkflowOutputState[TReport]:
        """Validate input, invoke the workflow StateGraph, and guarantee ``{'result': ...}``."""
        validated = self.coerce_input(inputs)
        payload = {k: getattr(validated, k) for k in type(validated).model_fields}
        has_saver = getattr(self.graph, "checkpointer", None) is not None
        invoke_config = config or (new_delegation_config() if has_saver else None)
        try:
            state: dict[str, Any] = (
                self.graph.invoke(payload, config=invoke_config)
                if invoke_config is not None
                else self.graph.invoke(payload)
            )
        except Exception as error:
            if failure_kind(error) is None:
                raise
            return {
                "result": SpecialistResult[TReport](
                    specialist=self.spec.name,
                    status="failed",
                    reason=failure_reason(error),
                )
            }

        if isinstance(state, dict) and state.get("result") is not None:
            return {"result": state["result"]}

        waiting = pending_approvals(state) if isinstance(state, dict) else ""
        return {
            "result": SpecialistResult[TReport](
                specialist=self.spec.name,
                status="partial" if waiting else "failed",
                reason=(
                    f"Stopped before finishing: waiting for approval of {waiting}."
                    if waiting
                    else f"No {self.spec.name} report was produced."
                ),
            )
        }

    def run(self, *args: Any, **kwargs: Any) -> SpecialistResult[TReport]:
        """Run the workflow and return the ``SpecialistResult[TReport]`` envelope."""
        if len(args) == 1 and not kwargs:
            return self.invoke(args[0])["result"]
        if args:
            field_names = list(self.spec.input_schema.model_fields)
            merged = {**dict(zip(field_names, args, strict=False)), **kwargs}
            return self.invoke(merged)["result"]
        return self.invoke(kwargs)["result"]

    def render(self, report: TReport) -> str:
        """Render ``TReport`` as text for a coordinator or tool caller."""
        return report.model_dump_json(indent=2)

    def as_subagent(
        self,
        *,
        name: str | None = None,
        description: str | None = None,
    ) -> CompiledSubAgent:
        """Expose this bound workflow as a ``CompiledSubAgent`` (no engine parameter needed)."""
        return specialist_subagent(
            name or self.spec.name,
            description or self.spec.description,
            lambda task: self.invoke(task)["result"],
            render=self.render,
        )

    def as_tool(self) -> BaseTool:
        """Expose this bound workflow as a typed ``BaseTool`` (no engine parameter needed)."""

        def invoke_tool(**tool_args: Any) -> str:
            return self.invoke(tool_args)["result"].to_text(render=self.render)

        return StructuredTool.from_function(
            func=invoke_tool,
            name=self.spec.name,
            description=self.spec.description,
            args_schema=self.spec.input_schema,
        )


# Alias so existing references to `Specialist` in docs/tests resolve cleanly to `Workflow`
Specialist = Workflow

__all__ = [
    "ResultNode",
    "Specialist",
    "SpecialistSpec",
    "Workflow",
    "WorkflowOutputState",
    "WorkflowOverallState",
    "WorkflowRunner",
]
