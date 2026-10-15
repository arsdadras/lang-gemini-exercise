"""P4 domain workflow & specialist: ``InterpreterWorkflow``, ``run_interpreter``, and ``INTERPRETER_SPECIALIST``."""

from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.interpreter_agent import (
    InterpreterAgent,
    make_interpreter_agent,
)
from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.schemas.input.interpreter_input_schema import InterpreterInput
from agentlab.schemas.output.interpreter_output_schema import InterpreterReport
from agentlab.schemas.output.specialist_output_schema import (
    SideEffect,
    SpecialistResult,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.get_text_util import get_text
from agentlab.utils.sandbox_util import (
    diff_sandbox_deliverables,
    snapshot_sandbox_deliverables,
)
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals
from agentlab.workflows.specialist_workflow import (
    SpecialistSpec,
    Workflow,
    WorkflowOverallState,
)

DEFAULT_INTERPRETER_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in deliverables/ and self-corrects on errors."
)


def _default_interpreter_agent() -> CompiledStateGraph:
    return make_interpreter_agent(
        get_sqlite_checkpointer(checkpoint_db_path(DELEGATIONS_APP)),
        interrupt_tools=(),
        worker=True,
    )


def _extract_executed_commands(messages: list[Any]) -> list[str]:
    commands: list[str] = []
    for msg in messages:
        for tc in getattr(msg, "tool_calls", None) or []:
            if (
                isinstance(tc, dict)
                and tc.get("name") == "execute"
                and isinstance(tc.get("args"), dict)
                and tc["args"].get("command")
            ):
                commands.append(str(tc["args"]["command"]))
    return commands


def render_interpreter_report(report: InterpreterReport) -> str:
    """Render an ``InterpreterReport`` as its answer text for ``SpecialistResult.to_text``."""
    return report.answer


class InterpreterWorkflowState(WorkflowOverallState[InterpreterReport]):
    """Overall state for the Interpreter workflow graph."""

    task: str


class InterpreterWorkflow(Workflow[InterpreterInput, InterpreterReport]):
    """Active Rung-2 Interpreter domain workflow wrapping ``InterpreterAgent``."""

    spec = SpecialistSpec(
        name="interpreter",
        description=DEFAULT_INTERPRETER_DESCRIPTION,
        input_schema=InterpreterInput,
        report_schema=InterpreterReport,
    )

    def __init__(
        self,
        agent: InterpreterAgent | CompiledStateGraph | Any = None,
        *,
        sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    ) -> None:
        self._agent = agent
        self.sandbox_dir = sandbox_dir

    @property
    def agent(self) -> CompiledStateGraph:
        if self._agent is None:
            self._agent = _default_interpreter_agent()
        return self._agent

    def render(self, report: InterpreterReport) -> str:
        return render_interpreter_report(report)

    def build_graph(self) -> CompiledStateGraph:
        def _interpret_step(state: InterpreterWorkflowState) -> dict[str, Any]:
            before = snapshot_sandbox_deliverables(self.sandbox_dir)
            failure: Exception | None = None
            try:
                sub_state = self.agent.invoke(
                    {"messages": [HumanMessage(content=state["task"])]},
                    config=new_delegation_config(),
                )
            except Exception as error:
                if failure_kind(error) is None:
                    raise
                sub_state, failure = {}, error

            changes = diff_sandbox_deliverables(before, self.sandbox_dir)
            side_effects = [
                SideEffect(
                    action="created" if change == "new" else "modified",
                    target=deliverable.path,
                    description=deliverable.description or deliverable.deliverable_type,
                )
                for change, deliverable in changes
            ]

            if failure is not None:
                return {
                    "report": None,
                    "problems": [failure_reason(failure)],
                    "side_effects": side_effects,
                }

            messages = sub_state.get("messages", [])
            answer = get_text(messages[-1]) if messages else ""
            waiting = pending_approvals(sub_state)
            report = InterpreterReport(
                answer=answer,
                executed_commands=_extract_executed_commands(messages),
                deliverables=[deliverable for _, deliverable in changes],
            )
            problems = (
                [f"Stopped before finishing: waiting for approval of {waiting}."]
                if waiting
                else []
            )
            return {
                "report": report,
                "problems": problems,
                "side_effects": side_effects,
            }

        graph = StateGraph(InterpreterWorkflowState)
        graph.add_node("interpret_step", _interpret_step)
        graph.add_node("pack_result", self.pack_node)
        graph.add_edge(START, "interpret_step")
        graph.add_edge("interpret_step", "pack_result")
        graph.add_edge("pack_result", END)
        return graph.compile()


def run_interpreter(
    agent: InterpreterAgent | CompiledStateGraph | Any,
    task: str,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[InterpreterReport]:
    """Run ``task`` with a P4 interpreter agent on a fresh thread; files it wrote become side effects."""
    return InterpreterWorkflow(agent, sandbox_dir=sandbox_dir).run(task=task)


def make_interpreter_specialist(
    engine: InterpreterAgent | CompiledStateGraph | Any = None,
    *,
    sandbox_dir: Path | None = None,
) -> InterpreterWorkflow:
    """Create an Interpreter Workflow bound to an engine or lazy default."""
    target_sandbox = sandbox_dir if sandbox_dir is not None else DEFAULT_SANDBOX_DIR
    return InterpreterWorkflow(engine, sandbox_dir=target_sandbox)


INTERPRETER_SPECIALIST = InterpreterWorkflow()
interpreter_workflow = INTERPRETER_SPECIALIST
