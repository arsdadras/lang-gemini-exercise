"""P4 domain workflow & specialist: ``run_interpreter`` and ``INTERPRETER_SPECIALIST``."""

from pathlib import Path
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from agentlab.agents.interpreter_agent import make_interpreter_agent
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
from agentlab.workflows.base import Specialist

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


def run_interpreter(
    agent: CompiledStateGraph,
    task: str,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[InterpreterReport]:
    """Run ``task`` with a P4 interpreter agent on a fresh thread; files it wrote become side effects.

    The deliverable diff compares ``deliverables/`` before and after the run, so the caller learns
    exactly which deliverables were created or changed, even when the run failed midway.
    """
    before = snapshot_sandbox_deliverables(sandbox_dir)
    failure: Exception | None = None
    try:
        state = agent.invoke(
            {"messages": [HumanMessage(content=task)]},
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        state, failure = {}, error
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
        return SpecialistResult[InterpreterReport](
            specialist="interpreter",
            status="failed",
            reason=failure_reason(failure),
            side_effects=side_effects,
        )
    messages = state.get("messages", [])
    answer = get_text(messages[-1]) if messages else ""
    waiting = pending_approvals(state)
    report = InterpreterReport(
        answer=answer,
        executed_commands=_extract_executed_commands(messages),
        deliverables=[deliverable for _, deliverable in changes],
    )
    return SpecialistResult[InterpreterReport](
        specialist="interpreter",
        status="partial" if waiting else "ok",
        reason=f"Stopped before finishing: waiting for approval of {waiting}."
        if waiting
        else "",
        output=report,
        side_effects=side_effects,
    )


def make_interpreter_specialist(
    engine: CompiledStateGraph | None = None,
    *,
    sandbox_dir: Path | None = None,
) -> Specialist[InterpreterInput, InterpreterReport]:
    """Create an Interpreter Specialist pre-bound to an engine or lazy default."""

    target_sandbox = sandbox_dir if sandbox_dir is not None else DEFAULT_SANDBOX_DIR

    def run_bound(
        task: InterpreterInput | str | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SpecialistResult[InterpreterReport]:
        resolved_engine = engine if engine is not None else _default_interpreter_agent()
        data = task if task is not None else kwargs
        if isinstance(data, InterpreterInput):
            prompt = data.task
        elif isinstance(data, dict):
            prompt = str(data["task"])
        else:
            prompt = str(data)
        return run_interpreter(resolved_engine, prompt, sandbox_dir=target_sandbox)

    return Specialist[InterpreterInput, InterpreterReport](
        name="interpreter",
        description=DEFAULT_INTERPRETER_DESCRIPTION,
        input_schema=InterpreterInput,
        report_schema=InterpreterReport,
        run=run_bound,
        render=render_interpreter_report,
    )


INTERPRETER_SPECIALIST = make_interpreter_specialist()
