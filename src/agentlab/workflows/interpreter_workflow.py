"""P4 domain workflow & specialist: ``run_interpreter`` and ``INTERPRETER_SPECIALIST_SPEC``."""

from pathlib import Path
from typing import Any, overload

from langchain_core.messages import HumanMessage

from agentlab.agents.interpreter_agent import make_interpreter_agent
from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
from agentlab.configs.paths_config import DELEGATIONS_APP, checkpoint_db_path
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.schemas.input.interpreter_input_schema import InterpreterInput
from agentlab.schemas.output.interpreter_output_schema import InterpreterReport
from agentlab.schemas.output.specialist_output_schema import (
    SideEffect,
    Specialist,
    SpecialistResult,
)
from agentlab.utils.failure_util import failure_kind, failure_reason
from agentlab.utils.get_text_util import get_text
from agentlab.utils.sandbox_util import (
    diff_sandbox_deliverables,
    snapshot_sandbox_deliverables,
)
from agentlab.utils.subagent_util import new_delegation_config, pending_approvals

INTERPRETER_SPECIALIST = "interpreter"
DEFAULT_INTERPRETER_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in deliverables/ and self-corrects on errors."
)


def _default_interpreter_agent() -> Any:
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


@overload
def run_interpreter(
    task: str,
    *,
    agent: Any = None,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[InterpreterReport]: ...


@overload
def run_interpreter(
    agent: Any,
    task: str,
    /,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[InterpreterReport]: ...


def run_interpreter(*args: Any, **kwargs: Any) -> SpecialistResult[InterpreterReport]:
    """Run ``task`` with a P4 interpreter agent on a fresh thread; files it wrote become side effects.

    Supports both ``run_interpreter(agent, task)`` and ``run_interpreter(task, agent=...)``.
    The deliverable diff compares ``deliverables/`` before and after the run, so the caller learns
    exactly which deliverables were created or changed, even when the run failed midway.
    """
    agent_or_task = args[0] if len(args) >= 1 else None
    pos_task = args[1] if len(args) >= 2 else kwargs.get("task")
    kw_agent = kwargs.get("agent")
    sandbox_dir: Path = kwargs.get("sandbox_dir", DEFAULT_SANDBOX_DIR)

    if isinstance(agent_or_task, str):
        resolved_task = agent_or_task
        resolved_agent = (
            kw_agent if kw_agent is not None else _default_interpreter_agent()
        )
    elif agent_or_task is None and isinstance(pos_task, str):
        resolved_task = pos_task
        resolved_agent = (
            kw_agent if kw_agent is not None else _default_interpreter_agent()
        )
    else:
        if not isinstance(pos_task, str):
            msg = "run_interpreter requires a task string"
            raise TypeError(msg)
        resolved_agent = agent_or_task
        resolved_task = pos_task

    before = snapshot_sandbox_deliverables(sandbox_dir)
    failure: Exception | None = None
    try:
        state = resolved_agent.invoke(
            {"messages": [HumanMessage(content=resolved_task)]},
            config=new_delegation_config(),
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        state, failure = {}, error
    side_effects = [
        SideEffect(
            action="created" if change == "new" else "modified",
            target=deliverable.path,
            description=deliverable.description or deliverable.deliverable_type,
        )
        for change, deliverable in diff_sandbox_deliverables(before, sandbox_dir)
    ]
    if failure is not None:
        return SpecialistResult[InterpreterReport](
            specialist=INTERPRETER_SPECIALIST,
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
        deliverables=[effect.target for effect in side_effects],
    )
    return SpecialistResult[InterpreterReport](
        specialist=INTERPRETER_SPECIALIST,
        status="partial" if waiting else "ok",
        reason=f"Stopped before finishing: waiting for approval of {waiting}."
        if waiting
        else "",
        output=report,
        side_effects=side_effects,
    )


INTERPRETER_SPECIALIST_SPEC = Specialist[InterpreterInput, InterpreterReport](
    name=INTERPRETER_SPECIALIST,
    description=DEFAULT_INTERPRETER_DESCRIPTION,
    input_schema=InterpreterInput,
    report_schema=InterpreterReport,
    run=run_interpreter,
    render=render_interpreter_report,
)
