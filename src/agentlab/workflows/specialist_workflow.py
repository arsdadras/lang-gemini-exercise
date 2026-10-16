"""Rung-2 workflow framework: ``SpecialistSpec``, ``ResultNode``, and graph-native ``Workflow`` (ADR-0033)."""

from __future__ import annotations

import operator
from collections.abc import AsyncIterator, Iterator
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
from langchain_core.runnables import Runnable, RunnableConfig
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
    """Declarative I/O specification (Particle ID card) of a Rung-2 specialist.

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
        raw_report = state.get("report") if isinstance(state, dict) else None
        raw_problems = state.get("problems") if isinstance(state, dict) else []
        problems = [str(p).strip() for p in (raw_problems or []) if str(p).strip()]
        reason = " ".join(dict.fromkeys(problems))
        side_effects = (
            list(state.get("side_effects") or []) if isinstance(state, dict) else []
        )
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
                provenance=list(state.get("provenance") or [])
                if isinstance(state, dict)
                else [],
                side_effects=side_effects,
            )
        }


class Workflow[TInput: BaseModel, TReport: BaseModel](
    Runnable[TInput, WorkflowOutputState[TReport]]
):
    """Rung-2 domain workflow: typed Runnable facade over a compiled domain StateGraph (ADR-0033)."""

    spec: SpecialistSpec[TInput, TReport]

    def __init__(
        self,
        graph: CompiledStateGraph | Any | None = None,
    ) -> None:
        super().__init__()
        self._graph = graph

    @property
    def graph(self) -> CompiledStateGraph:
        """The compiled domain StateGraph wrapped by this workflow."""
        if self._graph is None:
            self._graph = self.build_default_graph()
        return self._graph

    def build_default_graph(self) -> CompiledStateGraph:
        """Build the default domain StateGraph when none was injected."""
        raise NotImplementedError(
            f"{type(self).__name__} must inject a graph or implement build_default_graph."
        )

    @property
    def name(self) -> SpecialistName:  # type: ignore[override]
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

    def prepare_payload(self, inputs: TInput) -> dict[str, Any]:
        """Convert validated input model to the dictionary passed to graph.invoke/stream."""
        return {k: getattr(inputs, k) for k in type(inputs).model_fields}

    def invoke(
        self,
        input: TInput | dict[str, Any] | str | None = None,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> WorkflowOutputState[TReport]:
        """Validate input, invoke the domain StateGraph, and guarantee ``{'result': ...}``."""
        validated = self.coerce_input(input)
        payload = self.prepare_payload(validated)
        has_saver = getattr(self.graph, "checkpointer", None) is not None
        invoke_config = config or (new_delegation_config() if has_saver else None)
        try:
            state: dict[str, Any] = (
                self.graph.invoke(payload, config=invoke_config, **kwargs)
                if invoke_config is not None
                else self.graph.invoke(payload, **kwargs)
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

    async def ainvoke(
        self,
        input: TInput | dict[str, Any] | str | None = None,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> WorkflowOutputState[TReport]:
        """Validate input, asynchronously invoke the domain StateGraph, and guarantee ``{'result': ...}``."""
        validated = self.coerce_input(input)
        payload = self.prepare_payload(validated)
        has_saver = getattr(self.graph, "checkpointer", None) is not None
        invoke_config = config or (new_delegation_config() if has_saver else None)
        try:
            state: dict[str, Any] = (
                await self.graph.ainvoke(payload, config=invoke_config, **kwargs)
                if invoke_config is not None
                else await self.graph.ainvoke(payload, **kwargs)
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

    def stream(  # type: ignore[override]
        self,
        input: TInput | dict[str, Any] | str | None = None,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> Iterator[dict[str, Any]]:
        """Stream steps from the underlying domain StateGraph."""
        validated = self.coerce_input(input)
        payload = self.prepare_payload(validated)
        has_saver = getattr(self.graph, "checkpointer", None) is not None
        invoke_config = config or (new_delegation_config() if has_saver else None)
        if invoke_config is not None:
            yield from self.graph.stream(payload, config=invoke_config, **kwargs)
        else:
            yield from self.graph.stream(payload, **kwargs)

    async def astream(  # type: ignore[override]
        self,
        input: TInput | dict[str, Any] | str | None = None,
        config: RunnableConfig | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[dict[str, Any]]:
        """Asynchronously stream steps from the underlying domain StateGraph."""
        validated = self.coerce_input(input)
        payload = self.prepare_payload(validated)
        has_saver = getattr(self.graph, "checkpointer", None) is not None
        invoke_config = config or (new_delegation_config() if has_saver else None)
        if invoke_config is not None:
            async for chunk in self.graph.astream(
                payload, config=invoke_config, **kwargs
            ):
                yield chunk
        else:
            async for chunk in self.graph.astream(payload, **kwargs):
                yield chunk

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

    def as_tool(
        self,
        args_schema: type[BaseModel] | None = None,
        *,
        name: str | None = None,
        description: str | None = None,
        arg_types: dict[str, type] | None = None,
    ) -> BaseTool:
        """Expose this bound workflow as a typed ``BaseTool`` (no engine parameter needed)."""

        def invoke_tool(**tool_args: Any) -> str:
            return self.invoke(tool_args)["result"].to_text(render=self.render)

        target_schema = args_schema or self.spec.input_schema
        target_name = name or self.spec.name
        target_desc = description or self.spec.description

        return StructuredTool.from_function(
            func=invoke_tool,
            name=target_name,
            description=target_desc,
            args_schema=target_schema,
        )


__all__ = [
    "ResultNode",
    "SpecialistSpec",
    "Workflow",
    "WorkflowOutputState",
    "WorkflowOverallState",
    "WorkflowRunner",
]
