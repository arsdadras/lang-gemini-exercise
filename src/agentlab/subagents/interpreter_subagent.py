"""P4's boundary: ``run_interpreter`` returns the specialist envelope; the adapter serves coordinators."""

from pathlib import Path

from deepagents import CompiledSubAgent
from langchain_core.messages import HumanMessage
from langchain_core.runnables import Runnable

from agentlab.configs.interpreter_config import DEFAULT_SANDBOX_DIR
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
from agentlab.utils.subagent_util import (
    new_delegation_config,
    pending_approvals,
    specialist_subagent,
)

INTERPRETER_SPECIALIST = "interpreter"
DEFAULT_SUBAGENT_NAME = "code_interpreter"
DEFAULT_SUBAGENT_DESCRIPTION = (
    "Executes Python scripts, computational tasks, data processing, and shell commands "
    "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
    "markdown reports) in deliverables/ and self-corrects on errors."
)


def run_interpreter(
    agent: Runnable,
    task: str,
    *,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> SpecialistResult[str]:
    """Run ``task`` with an injected P4 agent on a fresh thread; files it wrote become side effects.

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
    side_effects = [
        SideEffect(
            action="created" if change == "new" else "modified",
            target=deliverable.path,
            description=deliverable.description or deliverable.deliverable_type,
        )
        for change, deliverable in diff_sandbox_deliverables(before, sandbox_dir)
    ]
    if failure is not None:
        return SpecialistResult[str](
            specialist=INTERPRETER_SPECIALIST,
            status="failed",
            reason=failure_reason(failure),
            side_effects=side_effects,
        )
    answer = get_text(state["messages"][-1]) if state.get("messages") else None
    waiting = pending_approvals(state)
    return SpecialistResult[str](
        specialist=INTERPRETER_SPECIALIST,
        status="partial" if waiting else "ok",
        reason=f"Stopped before finishing: waiting for approval of {waiting}."
        if waiting
        else "",
        output=answer,
        side_effects=side_effects,
    )


def make_interpreter_subagent(
    agent: Runnable,
    *,
    name: str = DEFAULT_SUBAGENT_NAME,
    description: str = DEFAULT_SUBAGENT_DESCRIPTION,
    sandbox_dir: Path = DEFAULT_SANDBOX_DIR,
) -> CompiledSubAgent:
    """Wrap an interpreter agent as a ``CompiledSubAgent``; the envelope comes back as text.

    The agent is injected (built by the caller, e.g. ``make_interpreter_agent``), so this
    module never depends on ``agents/``.
    """

    return specialist_subagent(
        name,
        description,
        lambda task: run_interpreter(agent, task, sandbox_dir=sandbox_dir),
    )
