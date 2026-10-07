"""``create_deep_agent`` without DeepAgents' default general-purpose subagent.

DeepAgents adds a ``general-purpose`` subagent to every deep agent unless told otherwise. It gets
the parent's tools but none of the parent's middleware, so through the ``task`` tool it skips the
parent's approval gates, tool budgets, security guards, and redaction, and whatever it reads or
does never reaches the parent's messages. No agent here needs it: those that delegate name their
own subagents. Every deep agent is built through this module.

The switch is DeepAgents' harness profile (``GeneralPurposeSubagentProfile(enabled=False)``),
registered per provider, which merges with the provider's built-in profile. The registry is
global, so registration happens once, on the first build, never at import time. An agent with
no subagents of its own then has no ``task`` tool at all.
"""

from functools import cache
from typing import Any

import deepagents
from deepagents import (
    GeneralPurposeSubagentProfile,
    HarnessProfile,
    register_harness_profile,
)

# The providers our catalog's chat models report (``configs/models_config.py``).
CHAT_PROVIDERS = ("openai", "google_genai", "anthropic", "ollama")


@cache
def disable_general_purpose_subagent() -> None:
    """Register, once per process, the profile that drops the default subagent."""
    for provider in CHAT_PROVIDERS:
        register_harness_profile(
            provider,
            HarnessProfile(
                general_purpose_subagent=GeneralPurposeSubagentProfile(enabled=False)
            ),
        )


def create_deep_agent(*args: Any, **kwargs: Any) -> Any:
    """``deepagents.create_deep_agent``, never with the default general-purpose subagent."""
    disable_general_purpose_subagent()
    return deepagents.create_deep_agent(*args, **kwargs)
