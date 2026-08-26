"""Human-in-the-loop approval middleware.

Requires a checkpointer on the agent since interrupts pause the graph and
must resume from persisted state.
"""

from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain.agents.middleware.human_in_the_loop import DecisionType


def hitl_for(
    tool_names: str | list[str],
    *,
    allowed_decisions: tuple[DecisionType, ...] = ("approve", "edit", "reject"),
    description_prefix: str | None = None,
) -> HumanInTheLoopMiddleware:
    """Build a `HumanInTheLoopMiddleware` requiring approval before the given tool(s) run."""
    if isinstance(tool_names, str):
        tool_names = [tool_names]
    interrupt_on: dict[str, bool | InterruptOnConfig] = {
        name: InterruptOnConfig(allowed_decisions=list(allowed_decisions))
        for name in tool_names
    }
    return HumanInTheLoopMiddleware(
        interrupt_on=interrupt_on,
        description_prefix=description_prefix or f"{', '.join(tool_names)} pending approval",
    )


search_approval = hitl_for("web_search")
