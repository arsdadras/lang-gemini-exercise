"""Agent-level model fallback on top of LangChain's ``ModelFallbackMiddleware``.

An agent's model must be a plain ``BaseChatModel`` (DeepAgents calls
``bind_tools`` on it), so agents can't use ``llm_model.chain()``'s
``with_fallbacks`` wrapper. Instead the agent gets ``llm_model.get(tier, primary)``
and this middleware retries a failed model call on the same catalog's fallbacks.
The built-in middleware also re-raises ``GraphBubbleUp`` (interrupts) untouched
instead of treating them as model failures.
"""

from typing import Any

from langchain.agents.middleware import AgentMiddleware, ModelFallbackMiddleware

from agentlab.models import llm_model


def make_model_fallback(
    tier: str | None = None,
    *,
    primary: str | None = None,
    cascade: bool = False,
) -> list[AgentMiddleware[Any, Any, Any]]:
    """Fallback middleware for an agent whose model is ``llm_model.get(tier, primary)``.

    A list, spread into the agent's middleware: empty in test mode when the test tier has a single
    provider (there is nothing to fall back to, by design), so test mode can build every agent.
    Outside test mode a tier without a fallback is a catalog error and raises (ADR-0007).
    """
    fallbacks = llm_model.fallback_models(tier, primary=primary, cascade=cascade)
    if fallbacks:
        return [ModelFallbackMiddleware(*fallbacks)]
    if llm_model.in_test_mode():
        return []
    msg = f"Tier {llm_model.resolve_tier(tier)!r} has no fallback provider configured"
    raise ValueError(msg)
