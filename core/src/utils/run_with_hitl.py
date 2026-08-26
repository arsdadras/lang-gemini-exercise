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
    prompt: str = "Approve this action? [y/n]: ",
) -> dict:
    """Invoke `agent`, resolving any HITL interrupts via CLI y/n prompts.

    Loops until the agent produces a result with no pending interrupt.
    """
    result = agent.invoke(initial_input, config)

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        for request in interrupt.value["action_requests"]:
            print(f"\n{request['description']}")
            print(f"Tool: {request['name']}")
            print(f"Args: {request['args']}")

        decision = input(prompt).strip().lower()
        resume = {"decisions": [{"type": "approve" if decision == "y" else "reject"}]}
        result = agent.invoke(Command(resume=resume), config)

    return result
