"""Graph assembly for the P4 interpreter workflow: interpret -> pack_result -> END."""

from pathlib import Path
from typing import Any, NewType

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

InterpreterGraph = NewType("InterpreterGraph", CompiledStateGraph)

from agentlab.agents.interpreter_agent import (
    InterpreterAgent,
    make_interpreter_agent,
)
from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.schemas.input.interpreter_input_schema import InterpreterInput
from agentlab.schemas.output.interpreter_output_schema import InterpreterReport
from agentlab.schemas.output.specialist_output_schema import SideEffect
from agentlab.schemas.state.interpreter_state import InterpreterState
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.get_text_util import get_text
from agentlab.utils.sandbox_util import (
    diff_sandbox_deliverables,
    snapshot_sandbox_deliverables,
)
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals
from agentlab.workflows.specialist_workflow import ResultNode, SpecialistSpec

DEFAULT_INTERPRETER_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in deliverables/ and self-corrects on errors."
)

INTERPRETER_SPEC = SpecialistSpec[InterpreterInput, InterpreterReport](
    name="interpreter",
    description=DEFAULT_INTERPRETER_DESCRIPTION,
    input_schema=InterpreterInput,
    report_schema=InterpreterReport,
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


def build_interpreter_graph(
    agent: InterpreterAgent | CompiledStateGraph | Any = None,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
    checkpointer: BaseCheckpointSaver | None = None,
) -> InterpreterGraph:
    """Build and compile the unified Interpreter graph ending in ``pack_result``."""
    resolved_agent = agent if agent is not None else _default_interpreter_agent()

    def _interpret_step(state: InterpreterState) -> dict[str, Any]:
        before = snapshot_sandbox_deliverables(sandbox_dir)
        failure: Exception | None = None
        try:
            sub_state = resolved_agent.invoke(
                {"messages": [HumanMessage(content=state["task"])]},
                config=new_delegation_config(),
            )
        except Exception as error:
            if failure_kind(error) is None:
                raise
            sub_state, failure = {}, error

        changes = diff_sandbox_deliverables(before, sandbox_dir)
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

    graph = StateGraph(InterpreterState)
    graph.add_node("interpret", _interpret_step)
    graph.add_node("pack_result", ResultNode(INTERPRETER_SPEC))
    graph.add_edge(START, "interpret")
    graph.add_edge("interpret", "pack_result")
    graph.add_edge("pack_result", END)

    compiled = graph.compile(checkpointer=checkpointer)
    return InterpreterGraph(compiled)
