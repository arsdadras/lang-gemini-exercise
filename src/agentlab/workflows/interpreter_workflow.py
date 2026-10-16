"""P4 domain workflow & specialist: ``InterpreterWorkflow``, ``run_interpreter``, and ``INTERPRETER_SPECIALIST``."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.interpreter_agent import InterpreterAgent
from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.graphs.interpreter_graph import (
    DEFAULT_INTERPRETER_DESCRIPTION,
    INTERPRETER_SPEC,
    InterpreterGraph,
    build_interpreter_graph,
)
from agentlab.schemas.input.interpreter_input_schema import InterpreterInput
from agentlab.schemas.output.interpreter_output_schema import InterpreterReport
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.workflows.specialist_workflow import Workflow

__all__ = [
    "DEFAULT_INTERPRETER_DESCRIPTION",
    "INTERPRETER_SPECIALIST",
    "InterpreterWorkflow",
    "build_interpreter_graph",
    "make_interpreter_specialist",
    "render_interpreter_report",
    "run_interpreter",
]


def render_interpreter_report(report: InterpreterReport) -> str:
    """Render an ``InterpreterReport`` as its answer text for ``SpecialistResult.to_text``."""
    return report.answer


class InterpreterWorkflow(Workflow[InterpreterInput, InterpreterReport]):
    """Active Rung-2 Interpreter domain workflow wrapping ``InterpreterGraph`` as a Runnable facade."""

    spec = INTERPRETER_SPEC

    def __init__(
        self,
        graph: InterpreterGraph | CompiledStateGraph | Any | None = None,
        *,
        agent: InterpreterAgent | CompiledStateGraph | Any = None,
        sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    ) -> None:
        super().__init__(graph)
        self._agent = agent
        self.sandbox_dir = sandbox_dir

    def build_default_graph(self) -> CompiledStateGraph:
        return build_interpreter_graph(agent=self._agent, sandbox_dir=self.sandbox_dir)

    @classmethod
    def from_graph(
        cls,
        graph: InterpreterGraph | CompiledStateGraph | Any,
        *,
        sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    ) -> InterpreterWorkflow:
        return cls(graph=graph, sandbox_dir=sandbox_dir)

    @classmethod
    def from_agent(
        cls,
        agent: InterpreterAgent | CompiledStateGraph | Any,
        *,
        sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    ) -> InterpreterWorkflow:
        return cls(
            graph=build_interpreter_graph(agent=agent, sandbox_dir=sandbox_dir),
            agent=agent,
            sandbox_dir=sandbox_dir,
        )

    def render(self, report: InterpreterReport) -> str:
        return render_interpreter_report(report)


def run_interpreter(
    graph: InterpreterGraph | CompiledStateGraph | Any,
    task: str,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[InterpreterReport]:
    """Run ``task`` through the pre-composed interpreter graph and return the specialist envelope."""
    return InterpreterWorkflow(graph=graph, sandbox_dir=sandbox_dir).invoke(task)[
        "result"
    ]


def make_interpreter_specialist(
    graph: InterpreterGraph | CompiledStateGraph | Any = None,
    *,
    agent: InterpreterAgent | CompiledStateGraph | Any = None,
    sandbox_dir: Path | None = None,
) -> InterpreterWorkflow:
    """Create an Interpreter Workflow bound to a graph, agent, or lazy default."""
    target_sandbox = sandbox_dir if sandbox_dir is not None else DEFAULT_SANDBOX_DIR
    if graph is not None:
        return InterpreterWorkflow.from_graph(graph, sandbox_dir=target_sandbox)
    if agent is not None:
        return InterpreterWorkflow.from_agent(agent, sandbox_dir=target_sandbox)
    return InterpreterWorkflow(sandbox_dir=target_sandbox)


INTERPRETER_SPECIALIST = make_interpreter_specialist()
