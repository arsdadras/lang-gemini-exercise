"""Generic human-in-the-loop resume loop for DeepAgents interrupts.

Any agent using an HITL middleware (e.g. `middlewares.hitl_for(...)`) pauses
via a LangGraph interrupt instead of running unattended. This drives that
interrupt/resume cycle over the CLI so callers don't each reimplement it.
"""

from typing import Any

from langgraph.types import Command


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
                decisions.append({"type": "approve"})
            else:
                reason = input("Reason for rejection (optional, press Enter to skip): ").strip()
                reject_payload: dict[str, Any] = {"type": "reject"}
                if reason:
                    reject_payload["message"] = reason
                decisions.append(reject_payload)

        resume = {"decisions": decisions}
        result = agent.invoke(Command(resume=resume), config)
    else:
        result = agent.invoke(initial_input, config)

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        decisions: list[dict[str, Any]] = []

        for request in interrupt.value["action_requests"]:
            if request.get("description"):
                print(f"\n{request['description']}")
            else:
                print(f"\nTool: {request['name']}")
                print(f"Args: {request['args']}")

            decision = input(assistant_prompt).strip().lower()
            if decision in ("y", "yes"):
                decisions.append({"type": "approve"})
            else:
                reason = input("Reason for rejection (optional, press Enter to skip): ").strip()
                reject_payload: dict[str, Any] = {"type": "reject"}
                if reason:
                    reject_payload["message"] = reason
                decisions.append(reject_payload)

        resume = {"decisions": decisions}
        result = agent.invoke(Command(resume=resume), config)

    return result
