"""P4 domain workflow & specialist: ``InterpreterWorkflow``, ``run_interpreter``, and ``INTERPRETER_SPECIALIST``."""

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
    "interpreter_workflow",
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

    def render(self, report: InterpreterReport) -> str:
        return render_interpreter_report(report)


def run_interpreter(
    agent: InterpreterAgent | CompiledStateGraph | Any,
    task: str,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[InterpreterReport]:
    """Run ``task`` with a P4 interpreter agent on a fresh thread; files it wrote become side effects."""
    if getattr(agent, "_is_interpreter_graph", False):
        workflow = InterpreterWorkflow(graph=agent, sandbox_dir=sandbox_dir)
    else:
        workflow = InterpreterWorkflow(agent=agent, sandbox_dir=sandbox_dir)
    return workflow.invoke(task)["result"]


def make_interpreter_specialist(
    engine: InterpreterAgent | CompiledStateGraph | Any = None,
    *,
    sandbox_dir: Path | None = None,
) -> InterpreterWorkflow:
    """Create an Interpreter Workflow bound to an engine or lazy default."""
    target_sandbox = sandbox_dir if sandbox_dir is not None else DEFAULT_SANDBOX_DIR
    if getattr(engine, "_is_interpreter_graph", False):
        return InterpreterWorkflow(graph=engine, sandbox_dir=target_sandbox)
    return InterpreterWorkflow(agent=engine, sandbox_dir=target_sandbox)


INTERPRETER_SPECIALIST = InterpreterWorkflow()
interpreter_workflow = INTERPRETER_SPECIALIST
