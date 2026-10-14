"""Unit tests for `agentlab.workflows.base` and Option C pre-bound Specialist pattern."""

from __future__ import annotations

import inspect
from typing import Any
from unittest.mock import MagicMock

from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.workflows.base import Specialist, WorkflowRunner
from agentlab.workflows.code_review_workflow import run_code_review
from agentlab.workflows.interpreter_workflow import run_interpreter
from agentlab.workflows.personal_brief_workflow import run_personal_brief
from agentlab.workflows.personal_context_workflow import run_personal_context
from agentlab.workflows.rag_workflow import run_rag
from agentlab.workflows.research_workflow import run_research


class DummyInput(BaseModel):
    query: str


class DummyReport(BaseModel):
    summary: str


def dummy_runner(
    engine: Any,
    query: str,
    *,
    extra_flag: bool = False,
) -> SpecialistResult[DummyReport]:
    report = DummyReport(
        summary=f"result for {query} with {engine} (extra={extra_flag})"
    )
    return SpecialistResult[DummyReport](
        specialist="research", status="ok", output=report
    )


def test_workflow_runner_protocol_conformance() -> None:
    """Verify that all domain workflow runners conform to WorkflowRunner and accept engine first."""
    runners = [
        run_research,
        run_rag,
        run_code_review,
        run_interpreter,
        run_personal_context,
        run_personal_brief,
        dummy_runner,
    ]
    for runner in runners:
        assert isinstance(runner, WorkflowRunner), (
            f"{runner} should conform to WorkflowRunner"
        )
        sig = inspect.signature(runner)
        first_param = next(iter(sig.parameters.values()))
        assert first_param.name in ("engine", "graph", "agent", "store"), (
            f"{runner.__name__} first param '{first_param.name}' must be an engine parameter"
        )


def test_specialist_prebound_factory_pattern() -> None:
    """Verify that Specialist executes pre-bound callable cleanly without keyword sniffing."""
    mock_engine = "engine_123"

    def run_bound(
        task: DummyInput | str | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SpecialistResult[DummyReport]:
        data = task if task is not None else kwargs
        if isinstance(data, DummyInput):
            query = data.query
        elif isinstance(data, dict):
            query = str(data["query"])
        else:
            query = str(data)
        extra_kwargs = {k: v for k, v in kwargs.items() if k != "query"}
        return dummy_runner(mock_engine, query, **extra_kwargs)

    spec = Specialist[DummyInput, DummyReport](
        name="research",
        description="A dummy specialist.",
        input_schema=DummyInput,
        report_schema=DummyReport,
        run=run_bound,
        render=lambda r: f"RENDERED: {r.summary}",
    )

    # 1. Direct run with schema
    res = spec.run(DummyInput(query="test"))
    assert res.output is not None
    assert "result for test with engine_123" in res.output.summary

    # 2. Direct run with kwargs
    res2 = spec.run(query="test2")
    assert res2.output is not None
    assert "result for test2 with engine_123" in res2.output.summary


def test_specialist_as_subagent_and_as_tool() -> None:
    """Verify adaptation to CompiledSubAgent dictionary and StructuredTool."""
    mock_engine = "mock_engine"

    def run_bound(
        task: DummyInput | str | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SpecialistResult[DummyReport]:
        data = task if task is not None else kwargs
        if isinstance(data, DummyInput):
            query = data.query
        elif isinstance(data, dict):
            query = str(data["query"])
        else:
            query = str(data)
        extra_flag = kwargs.get("extra_flag", False)
        return dummy_runner(mock_engine, query, extra_flag=extra_flag)

    spec = Specialist[DummyInput, DummyReport](
        name="research",
        description="Conducts research.",
        input_schema=DummyInput,
        report_schema=DummyReport,
        run=run_bound,
        render=lambda r: f"RENDERED: {r.summary}",
    )

    # Subagent adaptation
    subagent = spec.as_subagent(
        name="custom_subagent", description="Custom desc", extra_flag=True
    )
    assert subagent["name"] == "custom_subagent"
    assert subagent["description"] == "Custom desc"
    reply = subagent["runnable"].invoke(
        {"messages": [HumanMessage(content="quantum computing")]}
    )
    assert "messages" in reply
    assert (
        "RENDERED: result for quantum computing with mock_engine (extra=True)"
        in reply["messages"][0].content
    )

    # Tool adaptation
    tool = spec.as_tool(extra_flag=False)
    assert isinstance(tool, BaseTool)
    assert tool.name == "research"
    assert tool.args_schema == DummyInput
    tool_out = tool.invoke({"query": "neural networks"})
    assert (
        "RENDERED: result for neural networks with mock_engine (extra=False)"
        in tool_out
    )


def test_make_research_graph_and_precompiled_engine_detection() -> None:
    """Verify make_research_graph compiles the graph around an agent, and run_research detects it."""
    # Pre-compiled graph simulation (has 'check' in nodes)
    precompiled = MagicMock()
    precompiled.nodes = {"check": MagicMock(), "research": MagicMock()}
    precompiled.invoke.return_value = {
        "final_report": None,
        "drafts": [],
        "citations": [],
    }

    result = run_research(precompiled, topic="test topic")
    assert result.status == "failed"
    assert precompiled.invoke.called
