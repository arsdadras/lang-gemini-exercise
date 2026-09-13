"""Agent-level model fallback on top of LangChain's ``ModelFallbackMiddleware``.

An agent's model must be a plain ``BaseChatModel`` (DeepAgents calls
``bind_tools`` on it), so agents can't use ``llm_model.chain()``'s
``with_fallbacks`` wrapper. Instead the agent gets ``llm_model.get(tier, primary)``
and this middleware retries a failed model call on the same catalog's fallbacks.
The built-in middleware also re-raises ``GraphBubbleUp`` (interrupts) untouched
instead of treating them as model failures.
"""

from langchain.agents.middleware import ModelFallbackMiddleware

from agentlab.models import llm_model


def make_model_fallback(
    tier: str | None = None,
    *,
    primary: str | None = None,
    cascade: bool = False,
) -> ModelFallbackMiddleware:
    """Build fallback middleware for an agent whose model is ``llm_model.get(tier, primary)``."""
    fallbacks = llm_model.fallback_models(tier, primary=primary, cascade=cascade)
    if not fallbacks:
        msg = f"Tier {llm_model.resolve_tier(tier)!r} has no fallback provider configured"
        raise ValueError(msg)
    return ModelFallbackMiddleware(*fallbacks)
