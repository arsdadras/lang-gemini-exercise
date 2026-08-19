"""Human-in-the-loop approval middleware.

Requires a checkpointer on the agent (see app.py) since interrupts
pause the graph and must resume from persisted state.
"""

<<<<<<< HEAD
"""Agent middleware."""

=======
>>>>>>> ac268283fa2050850887180009b388e00afa28e8
from langchain.agents.middleware import HumanInTheLoopMiddleware

search_approval = HumanInTheLoopMiddleware(
    interrupt_on={
        "web_search": {
            "allowed_decisions": ["approve", "edit", "reject"],
<<<<<<< HEAD
        }
    },
    description_prefix="web_search pending approaval...",
=======
        },
    },
    description_prefix="web_search pending approval",
>>>>>>> ac268283fa2050850887180009b388e00afa28e8
)
