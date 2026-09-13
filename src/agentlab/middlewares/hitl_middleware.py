"""Human-in-the-loop approval middleware factory.

Interrupts pause the graph and resume from persisted state, so any agent using
this middleware needs a checkpointer.
"""

from collections.abc import Sequence

from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain.agents.middleware.human_in_the_loop import DecisionType


def hitl_for(
    tool_names: str | Sequence[str],
    *,
    allowed_decisions: Sequence[DecisionType] = ("approve", "edit", "reject"),
    description_prefix: str | None = None,
) -> HumanInTheLoopMiddleware:
    """Require human approval before the given tool(s) run."""
    names = [tool_names] if isinstance(tool_names, str) else list(tool_names)
    interrupt_on: dict[str, bool | InterruptOnConfig] = {
        name: InterruptOnConfig(allowed_decisions=list(allowed_decisions)) for name in names
    }
    return HumanInTheLoopMiddleware(
        interrupt_on=interrupt_on,
        description_prefix=description_prefix or f"{', '.join(names)} pending approval",
    )
