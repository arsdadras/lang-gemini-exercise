"""Generic human-in-the-loop resume loop for DeepAgents interrupts.

Any agent using an HITL middleware (e.g. `middlewares.hitl_for(...)`) pauses
via a LangGraph interrupt instead of running unattended. This drives that
interrupt/resume cycle over the CLI so callers don't each reimplement it.
"""

from typing import Any

from langgraph.types import Command


def _get_messages_count(agent: Any, config: dict) -> int:
    try:
        state = agent.get_state(config)
        return len(state.values.get("messages", []))
    except Exception:  # noqa: BLE001
        return 0


def _print_new_tool_outputs(agent: Any, config: dict, prev_count: int) -> int:
    try:
        state = agent.get_state(config)
        messages = state.values.get("messages", [])
        for m in messages[prev_count:]:
            m_type = getattr(m, "type", "") or type(m).__name__.lower()
            if "tool" in m_type:
                name = getattr(m, "name", "tool")
                content = str(getattr(m, "content", "")).strip()
                if content:
                    print(f"\n[Tool Execution Output — {name}]:\n{content}\n")
        return len(messages)
    except Exception:  # noqa: BLE001
        return prev_count


def run_with_hitl(
    agent: Any,
    initial_input: Any,
    config: dict,
    *,
    assistant_prompt: str = "Approve this action? [y/n]: ",
) -> dict:
    """Invoke `agent`, resolving any HITL interrupts via CLI y/n prompts.

    Loops until the agent produces a result with no pending interrupt.
    When an action is rejected, prompts for an optional reason and forwards
    it to the agent as actionable feedback for self-correction.
    """
    seen_msg_count = _get_messages_count(agent, config)

    if initial_input is None:
        state = agent.get_state(config)
        pending = [i for t in state.tasks for i in t.interrupts] if state.tasks else []
        if not pending:
            return state.values
        interrupt = pending[0]
        decisions: list[dict[str, Any]] = []
        for request in interrupt.value.get("action_requests", []):
            if request.get("description"):
                print(f"\n{request['description']}")
            else:
                print(f"\nTool: {request['name']}")
                print(f"Args: {request['args']}")

            decision = input(assistant_prompt).strip().lower()
            if decision in ("y", "yes"):
                print(f"✓ Approved. Executing {request.get('name', 'tool')}...")
                decisions.append({"type": "approve"})
            else:
                reason = input("Reason for rejection (optional, press Enter to skip): ").strip()
                print("✗ Action rejected. Returning feedback to agent...")
                reject_payload: dict[str, Any] = {"type": "reject"}
                if reason:
                    reject_payload["message"] = reason
                decisions.append(reject_payload)

        resume = {"decisions": decisions}
        result = agent.invoke(Command(resume=resume), config)
    else:
        result = agent.invoke(initial_input, config)

    seen_msg_count = _print_new_tool_outputs(agent, config, seen_msg_count)

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        decisions = []

        print("\n[Notice] Agent requested tool execution requiring approval:")
        for request in interrupt.value.get("action_requests", []):
            if request.get("description"):
                print(f"\n{request['description']}")
            else:
                print(f"\nTool: {request['name']}")
                print(f"Args: {request['args']}")

            decision = input(assistant_prompt).strip().lower()
            if decision in ("y", "yes"):
                print(f"✓ Approved. Executing {request.get('name', 'tool')}...")
                decisions.append({"type": "approve"})
            else:
                reason = input("Reason for rejection (optional, press Enter to skip): ").strip()
                print("✗ Action rejected. Returning feedback to agent...")
                reject_payload = {"type": "reject"}
                if reason:
                    reject_payload["message"] = reason
                decisions.append(reject_payload)

        resume = {"decisions": decisions}
        result = agent.invoke(Command(resume=resume), config)
        seen_msg_count = _print_new_tool_outputs(agent, config, seen_msg_count)

    return result

