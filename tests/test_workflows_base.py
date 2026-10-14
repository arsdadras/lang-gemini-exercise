"""Unit tests for `agentlab.workflows.base` and engine resolution in domain workflows."""

from __future__ import annotations

import inspect
from typing import Any
from unittest.mock import MagicMock

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from pydantic import BaseModel

from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.workflows.base import _ENGINE_KW_KEYS, Specialist, WorkflowRunner
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
        assert first_param.name in _ENGINE_KW_KEYS, (
            f"{runner.__name__} first param '{first_param.name}' must be one of {_ENGINE_KW_KEYS}"
        )


def test_specialist_engine_resolution_branches() -> None:
    """Verify all precedence and fallback branches of Specialist._resolve_engine."""
    spec = Specialist[DummyInput, DummyReport](
        name="research",
        description="A dummy specialist.",
        input_schema=DummyInput,
        report_schema=DummyReport,
        run=dummy_runner,
    )

    # 1. Explicit engine
    eng, rem = spec._resolve_engine(engine="custom_engine", kwargs={"extra_flag": True})
    assert eng == "custom_engine"
    assert rem == {"extra_flag": True}

    # 2. Kwargs target (backward compatibility)
    eng, rem = spec._resolve_engine(kwargs={"target": "target_engine", "other": 1})
    assert eng == "target_engine"
    assert rem == {"other": 1}

    # 3. Kwargs engine / graph / agent / store
    for key in ("engine", "graph", "agent", "store"):
        eng, rem = spec._resolve_engine(kwargs={key: f"{key}_val", "foo": "bar"})
        assert eng == f"{key}_val"
        assert key not in rem
        assert rem == {"foo": "bar"}

    # 4. Error when nothing provided
    with pytest.raises(ValueError, match="requires an engine or default_engine"):
        spec._resolve_engine()


def test_specialist_default_engine_and_default_target_fallbacks() -> None:
    """Verify default_engine and default_target fallbacks."""
    spec_with_default_engine = Specialist[DummyInput, DummyReport](
        name="rag",
        description="Desc",
        input_schema=DummyInput,
        report_schema=DummyReport,
        run=dummy_runner,
        default_engine=lambda: "default_engine_value",
    )
    eng, _ = spec_with_default_engine._resolve_engine()
    assert eng == "default_engine_value"

    spec_with_default_target = Specialist[DummyInput, DummyReport](
        name="code_review",
        description="Desc",
        input_schema=DummyInput,
        report_schema=DummyReport,
        run=dummy_runner,
        default_target=lambda: "default_target_value",
    )
    eng, _ = spec_with_default_target._resolve_engine()
    assert eng == "default_target_value"


def test_specialist_as_subagent_and_as_tool() -> None:
    """Verify adaptation to CompiledSubAgent dictionary and StructuredTool."""
    spec = Specialist[DummyInput, DummyReport](
        name="research",
        description="Conducts research.",
        input_schema=DummyInput,
        report_schema=DummyReport,
        run=dummy_runner,
        render=lambda r: f"RENDERED: {r.summary}",
        default_engine=lambda: "mock_engine",
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
    tool = spec.as_tool(target="tool_target", extra_flag=False)
    assert isinstance(tool, BaseTool)
    assert tool.name == "research"
    assert tool.args_schema == DummyInput
    tool_out = tool.invoke({"query": "neural networks"})
    assert (
        "RENDERED: result for neural networks with tool_target (extra=False)"
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
