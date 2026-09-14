"""Generic human-in-the-loop resume loop for DeepAgents interrupts.

Any agent using an HITL middleware (e.g. `middlewares.hitl_for(...)`) pauses
via a LangGraph interrupt instead of running unattended. This drives that
interrupt/resume cycle over the CLI so callers don't each reimplement it, either
with a blocking ``invoke`` (``run_with_hitl``) or with live progress (``stream_with_hitl``).
"""

import json
from collections.abc import Callable
from typing import Any

from langgraph.types import Command

from agentlab.utils.secret_redaction_util import redact_secrets
from agentlab.utils.streaming_util import stream_agent_with_observability


def _get_messages_count(agent: Any, config: dict | None) -> int:
    if config is None:
        return 0
    try:
        state = agent.get_state(config)
        return len(state.values.get("messages", []))
    except Exception:  # noqa: BLE001
        return 0


def _print_new_tool_outputs(agent: Any, config: dict | None, prev_count: int) -> int:
    if config is None:
        return prev_count
    try:
        state = agent.get_state(config)
        messages = state.values.get("messages", [])
        for m in messages[prev_count:]:
            m_type = getattr(m, "type", "") or type(m).__name__.lower()
            if "tool" in m_type:
                name = getattr(m, "name", "tool")
                content = str(getattr(m, "content", "")).strip()
                if content:
                    print(f"\n[Tool Execution Output - {name}]:\n{content}\n")
        return len(messages)
    except Exception:  # noqa: BLE001
        return prev_count


def _format_prompt(
    assistant_prompt: str | Callable[[dict[str, Any]], str] | None,
    request: dict[str, Any],
) -> str:
    action_name = request.get("name", "action")
    if callable(assistant_prompt):
        return assistant_prompt(request)
    if isinstance(assistant_prompt, str):
        if "{name}" in assistant_prompt:
            return assistant_prompt.format(name=action_name)
        return assistant_prompt
    return f"\nApprove {action_name} action? [y/n]: "


def _handle_interrupt_decisions(
    interrupt: Any,
    assistant_prompt: str | Callable[[dict[str, Any]], str] | None = None,
) -> dict[str, Any]:
    decisions: list[dict[str, Any]] = []
    print("\n[Notice] Agent requested action requiring approval:")
    for request in interrupt.value.get("action_requests", []):
        action_name = request.get("name", "action")
        if request.get("description"):
            print(f"\n{request['description']}")
        else:
            print(f"\n[Action Review Request]: {action_name}")
            args = request.get("args", {})
            try:
                print(f"Arguments: {json.dumps(args, indent=2, default=str)}")
            except Exception:  # noqa: BLE001
                print(f"Arguments: {args}")

        prompt_text = _format_prompt(assistant_prompt, request)
        decision = input(prompt_text).strip().lower()
        if decision in ("y", "yes"):
            print(f"[Approved] Executing {action_name}...")
            decisions.append({"type": "approve"})
        else:
            reason = input(
                "Reason for rejection (optional, press Enter to skip): "
            ).strip()
            print(f"[Rejected] {action_name} rejected. Returning feedback to agent...")
            reject_payload: dict[str, Any] = {"type": "reject"}
            if reason:
                reject_payload["message"] = redact_secrets(reason)[0]
            decisions.append(reject_payload)

    return {"decisions": decisions}


def run_with_hitl(
    agent: Any,
    initial_input: Any,
    config: dict | None = None,
    *,
    assistant_prompt: str | Callable[[dict[str, Any]], str] | None = None,
) -> dict[str, Any]:
    """Invoke `agent`, resolving any HITL interrupts via CLI y/n prompts.

    Loops until the agent produces a result with no pending interrupt.
    When an action is rejected, prompts for an optional reason and forwards
    it to the agent as actionable feedback for self-correction.
    """
    seen_msg_count = _get_messages_count(agent, config)

    if initial_input is None:
        if config is None:
            msg = "Config must be provided when resuming from existing state (initial_input=None)"
            raise ValueError(msg)
        state = agent.get_state(config)
        pending = [i for t in state.tasks for i in t.interrupts] if state.tasks else []
        if not pending:
            return state.values
        interrupt = pending[0]
        resume = _handle_interrupt_decisions(interrupt, assistant_prompt)
        result = agent.invoke(Command(resume=resume), config)
    else:
        result = agent.invoke(initial_input, config)

    seen_msg_count = _print_new_tool_outputs(agent, config, seen_msg_count)

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        resume = _handle_interrupt_decisions(interrupt, assistant_prompt)
        result = agent.invoke(Command(resume=resume), config)
        seen_msg_count = _print_new_tool_outputs(agent, config, seen_msg_count)

    return result


def stream_with_hitl(
    agent: Any,
    input_data: dict[str, Any],
    config: dict[str, Any],
    *,
    context: Any | None = None,
    assistant_prompt: str | Callable[[dict[str, Any]], str] | None = None,
) -> dict[str, Any]:
    """Stream a run with live progress, resolving HITL interrupts via CLI y/n prompts.

    Returns the final ``stream_agent_with_observability`` result once nothing is
    pending. Decisions are keyed by interrupt id: LangGraph refuses an unkeyed resume
    while more than one interrupt is pending (e.g. two subagents paused in parallel).
    ``context`` is sent again on each resume: runtime context is per invocation and
    is not checkpointed.
    """
    result = stream_agent_with_observability(agent, input_data, config, context=context)
    while result["interrupts"]:
        resume = {
            interrupt.id: _handle_interrupt_decisions(interrupt, assistant_prompt)
            for interrupt in result["interrupts"]
        }
        result = stream_agent_with_observability(agent, Command(resume=resume), config, context=context)
    return result
