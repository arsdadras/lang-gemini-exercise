"""Interpreter Subagent — wraps the compiled P4 Sandbox/Interpreter agent for delegation from DeepAgents multi-agent coordinators."""

import uuid
from typing import Any

from deepagents import CompiledSubAgent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda
from utils.get_text_util import get_text
from utils.sandbox_util import list_sandbox_artifacts

_interpreter_agent: Any | None = None


def _get_interpreter_agent() -> Any:
    """Lazy initialization of the compiled interpreter agent to prevent circular import layer inversion."""
    global _interpreter_agent
    if _interpreter_agent is None:
        from agents.interpreter_agent import make_interpreter_agent

        _interpreter_agent = make_interpreter_agent(hitl=False)
    return _interpreter_agent


def _run_interpreter_subagent(state: dict[str, Any]) -> dict[str, Any]:
    """Adapter function: converts incoming coordinator state to an interpreter agent call and returns a formatted AIMessage."""
    task_text = get_text(state["messages"][-1])
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    prev_artifacts = {a.path for a in list_sandbox_artifacts()}

    agent = _get_interpreter_agent()
    result = agent.invoke(
        {"messages": [HumanMessage(content=task_text)]},
        config=config,
    )

    output_text = get_text(result["messages"][-1])

    # Data Model Cohesion: detect any new artifacts generated during this delegation turn
    current_artifacts = list_sandbox_artifacts()
    new_artifacts = [a for a in current_artifacts if a.path not in prev_artifacts]

    parts = [output_text]
    if new_artifacts:
        parts.append("\n\n### Generated Deliverables:")
        for artifact in new_artifacts:
            size_kb = f" ({artifact.size_bytes / 1024:.1f} KB)" if artifact.size_bytes else ""
            desc = f" - {artifact.description}" if artifact.description else ""
            parts.append(f"- `{artifact.path}`{size_kb} [{artifact.artifact_type}]{desc}")

    return {
        "messages": [AIMessage(content="\n".join(parts))],
        "thread_id": thread_id,
    }


interpreter_subagent: CompiledSubAgent = {
    "name": "interpreter_subagent",
    "description": (
        "Executes Python scripts, computational tasks, data processing, and shell commands "
        "in an isolated sandbox workspace. Generates deliverable files (CSVs, charts, "
        "markdown reports) in artifacts/ and self-corrects on errors."
    ),
    "runnable": RunnableLambda(_run_interpreter_subagent),
}
