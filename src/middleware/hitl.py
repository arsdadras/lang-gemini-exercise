"""Human-in-the-loop approval middleware.

Requires a checkpointer on the agent (see app.py) since interrupts
pause the graph and must resume from persisted state.
"""

"""Agent middleware."""

from langchain.agents.middleware import HumanInTheLoopMiddleware

search_approval = HumanInTheLoopMiddleware(
    interrupt_on={
        "web_search": {
            "allowed_decisions": ["approve", "edit", "reject"],
        }
    },
    description_prefix="web_search pending approaval...",
)
