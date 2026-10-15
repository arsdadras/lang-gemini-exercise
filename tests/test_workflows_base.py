"""Unit tests for ``agentlab.workflows.specialist_workflow`` and graph-native ``Workflow`` (ADR-0033)."""

from __future__ import annotations

import dataclasses
import inspect
from typing import Any

import pytest
from langchain_core.messages import HumanMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SideEffect,
)
from agentlab.workflows.code_review_workflow import (
    CodeReviewWorkflow,
    run_code_review,
)
from agentlab.workflows.interpreter_workflow import (
    InterpreterWorkflow,
    run_interpreter,
)
from agentlab.workflows.personal_brief_workflow import run_personal_brief
from agentlab.workflows.personal_context_workflow import (
    PersonalContextWorkflow,
    run_personal_context,
)
from agentlab.workflows.rag_workflow import RagWorkflow, run_rag
from agentlab.workflows.research_workflow import (
    ResearchWorkflow,
    run_research,
)
from agentlab.workflows.specialist_workflow import (
    ResultNode,
    SpecialistSpec,
    Workflow,
    WorkflowOverallState,
    WorkflowRunner,
)


class DummyInput(BaseModel):
    query: str


class DummyReport(BaseModel):
    summary: str


class DummyWorkflowState(WorkflowOverallState[DummyReport]):
    query: str


class DummyWorkflow(Workflow[DummyInput, DummyReport]):
    spec = SpecialistSpec(
        name="research",
        description="A dummy research specialist.",
        input_schema=DummyInput,
        report_schema=DummyReport,
    )

    def __init__(self, engine_tag: str = "mock_engine") -> None:
        self.engine_tag = engine_tag

        def step(state: DummyWorkflowState) -> dict[str, Any]:
            report = DummyReport(
                summary=f"result for {state['query']} with {self.engine_tag}"
            )
            return {
                "report": report,
                "problems": [],
                "provenance": [
                    Provenance(kind="web", ref="https://example.com/source")
                ],
            }

        graph = StateGraph(DummyWorkflowState)
        graph.add_node("step", step)
        graph.add_node("pack_result", ResultNode(self.spec))
        graph.add_edge(START, "step")
        graph.add_edge("step", "pack_result")
        graph.add_edge("pack_result", END)
        super().__init__(graph.compile())

    def render(self, report: DummyReport) -> str:
        return f"RENDERED: {report.summary}"


def test_specialist_spec_declarative_metadata_and_immutability() -> None:
    """Verify that SpecialistSpec holds metadata only, without engine/target, and is frozen."""
    spec = SpecialistSpec[DummyInput, DummyReport](
        name="research",
        description="Conducts research.",
        input_schema=DummyInput,
        report_schema=DummyReport,
    )
    assert spec.name == "research"
    assert spec.description == "Conducts research."
    assert spec.input_schema is DummyInput
    assert spec.report_schema is DummyReport

    # Must NOT have engine or target attributes
    assert not hasattr(spec, "engine")
    assert not hasattr(spec, "target")
    assert not hasattr(spec, "graph")
    assert not hasattr(spec, "agent")
    assert not hasattr(spec, "store")

    # Must be frozen
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.name = "rag"  # type: ignore[misc]


def test_result_node_packing_across_outcomes() -> None:
    """Verify ResultNode packs ok, partial, and failed envelopes correctly."""
    spec = SpecialistSpec[DummyInput, DummyReport](
        name="research",
        description="Conducts research.",
        input_schema=DummyInput,
        report_schema=DummyReport,
    )
    packer = ResultNode(spec)

    # 1. OK outcome: report present, no problems
    ok_res = packer(
        {
            "report": DummyReport(summary="All good."),
            "problems": [],
            "provenance": [Provenance(kind="web", ref="https://a.example")],
            "side_effects": [SideEffect(action="created", target="out.txt")],
        }
    )["result"]
    assert ok_res.status == "ok"
    assert ok_res.reason == ""
    assert ok_res.output == DummyReport(summary="All good.")
    assert len(ok_res.provenance) == 1
    assert len(ok_res.side_effects) == 1

    # 2. Partial outcome: report present, problems non-empty
    partial_res = packer(
        {
            "report": DummyReport(summary="Partial good."),
            "problems": ["Missing one citation", "Low confidence"],
        }
    )["result"]
    assert partial_res.status == "partial"
    assert "Missing one citation Low confidence" in partial_res.reason
    assert partial_res.output == DummyReport(summary="Partial good.")

    # 3. Failed outcome: report is None, problems non-empty
    failed_res = packer(
        {
            "report": None,
            "problems": ["Search failed", "Timeout"],
        }
    )["result"]
    assert failed_res.status == "failed"
    assert "Search failed Timeout" in failed_res.reason
    assert failed_res.output is None
    assert failed_res.provenance == []

    # 4. Failed outcome with fallback reason: report is None, problems empty
    fallback_res = packer(
        {
            "report": None,
            "problems": [],
        }
    )["result"]
    assert fallback_res.status == "failed"
    assert fallback_res.reason == "No research report was produced."


def test_workflow_invoke_stream_run_and_subagent_adaptation() -> None:
    """Verify that Workflow.invoke, .stream, .run, .as_subagent, and .as_tool work cleanly."""
    wf = DummyWorkflow(engine_tag="engine_999")

    # 1. invoke() with string input
    state = wf.invoke("quantum computing")
    assert "result" in state
    assert state["result"].status == "ok"
    assert (
        state["result"].output.summary == "result for quantum computing with engine_999"
    )

    # 2. stream() yields steps from underlying StateGraph
    chunks = list(wf.stream("quantum computing"))
    assert len(chunks) >= 1
    # Last chunk should contain either pack_result or step updates
    assert any("pack_result" in c or "step" in c for c in chunks)

    # 3. run() with schema
    res = wf.run(DummyInput(query="distributed systems"))
    assert res.status == "ok"
    assert res.output.summary == "result for distributed systems with engine_999"

    # 4. as_subagent()
    subagent = wf.as_subagent(name="custom_subagent", description="Custom desc")
    assert subagent["name"] == "custom_subagent"
    assert subagent["description"] == "Custom desc"
    reply = subagent["runnable"].invoke(
        {"messages": [HumanMessage(content="superconductors")]}
    )
    assert (
        "RENDERED: result for superconductors with engine_999"
        in reply["messages"][0].content
    )

    # 5. as_tool() invoked with keyword arguments (regression test for TypeError: multiple values for argument)
    tool = wf.as_tool()
    assert isinstance(tool, BaseTool)
    assert tool.name == "research"
    assert tool.args_schema == DummyInput
    tool_out = tool.invoke({"query": "neural networks"})
    assert "RENDERED: result for neural networks with engine_999" in tool_out


def test_workflow_runner_protocol_conformance() -> None:
    """Verify that domain workflow runners conform to WorkflowRunner protocol."""
    runners = [
        run_research,
        run_rag,
        run_code_review,
        run_interpreter,
        run_personal_context,
        run_personal_brief,
    ]
    for runner in runners:
        assert isinstance(runner, WorkflowRunner), (
            f"{runner} should conform to WorkflowRunner"
        )
        sig = inspect.signature(runner)
        first_param = next(iter(sig.parameters.values()))
        assert first_param.name in (
            "engine",
            "graph",
            "agent",
            "store",
        ), (
            f"{runner.__name__} first param '{first_param.name}' must be an engine/graph/agent/store parameter"
        )


def test_domain_workflow_classes_subclass_workflow() -> None:
    """Verify that all domain workflow classes inherit from Workflow."""
    workflow_classes = [
        ResearchWorkflow,
        RagWorkflow,
        CodeReviewWorkflow,
        InterpreterWorkflow,
        PersonalContextWorkflow,
    ]
    for cls in workflow_classes:
        assert issubclass(cls, Workflow), f"{cls} must subclass Workflow"
        assert isinstance(cls.spec, SpecialistSpec), (
            f"{cls}.spec must be SpecialistSpec"
        )
