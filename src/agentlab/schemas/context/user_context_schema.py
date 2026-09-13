"""Runtime context schemas: per-invocation identity passed with ``context=``.

Context is not graph state (it isn't checkpointed or updated by nodes) and not
``config["configurable"]`` (the LangGraph ``Runtime`` handed to backends, tools,
and middleware doesn't expose config). Pass it on every call, e.g.
``agent.invoke(inputs, config, context=UserContext(user_id="alice"))``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserContext:
    """Identity the current run acts for; scopes per-user long-term memory."""

    user_id: str
