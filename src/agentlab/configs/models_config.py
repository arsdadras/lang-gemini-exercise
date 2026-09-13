"""Chat model catalog: capability tier x provider.

Each tier ("low"/"medium"/"high"/"free") maps a provider key to a ``ModelSpec``.
The first provider of a tier is its primary; the rest are same-tier fallbacks.
Credentials are referenced by environment variable *name* and read only when a
model is built (``models.registry_model``), so importing this module never
touches secrets and never depends on ``.env`` having been loaded yet.

Provider keys name the model brand, not the gateway. GapGPT is one
OpenAI-compatible gateway serving OpenAI and Anthropic models, so both use
``model_provider="openai"`` (the wire protocol) with GapGPT's base URL.

Model IDs were verified against each gateway's ``/v1/models`` list and a live
call on 2026-08-26. Verify the same way before adding a new ID.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    """Arguments for ``init_chat_model``; secrets are referenced by env var name."""

    model: str
    model_provider: str
    api_key_env: str
    base_url: str | None = None
    base_url_env: str | None = None
    temperature: float = 0.0
    top_p: float | None = None


_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _gemini(model: str) -> ModelSpec:
    return ModelSpec(
        model=model,
        model_provider="google_genai",
        api_key_env="GOOGLE_API_KEY",
        top_p=0.95,
    )


def _gapgpt(model: str) -> ModelSpec:
    return ModelSpec(
        model=model,
        model_provider="openai",
        api_key_env="GAPGPT_API_KEY",
        base_url_env="GAPGPT_BASE_URL",
    )


def _openrouter(model: str) -> ModelSpec:
    return ModelSpec(
        model=model,
        model_provider="openai",
        api_key_env="OPENROUTER_API_KEY",
        base_url=_OPENROUTER_BASE_URL,
    )


MODEL_TIERS: dict[str, dict[str, ModelSpec]] = {
    "high": {
        "openai": _gapgpt("gpt-5.6-sol"),
        "anthropic": _gapgpt("claude-opus-5"),
    },
    "medium": {
        "gemini": _gemini("gemini-3.8-flash"),
        "openai": _gapgpt("gpt-5.6-terra"),
        "anthropic": _gapgpt("claude-sonnet-5"),
    },
    "low": {
        "gemini": _gemini("gemini-3.5-flash-lite"),
        "openai": _gapgpt("gpt-5.6-luna"),
    },
    # Opt-in only: never the default tier and never part of a paid tier's fallback.
    "free": {
        "glm": _openrouter("z-ai/glm-5.3:free"),
        "nvidia": _openrouter("nvidia/nemotron-3-ultra-550b-a55b:free"),
    },
}

DEFAULT_TIER = "low"

# Order for opt-in cross-tier cascade (``cascade=True``): after a tier's own
# providers fail, fall through to each lower tier in turn.
TIER_CASCADE_ORDER: tuple[str, ...] = ("high", "medium", "low")

# Set ``LLM_TEST_MODE=true`` to route every request to TEST_TIER while iterating
# on prompts or routing without spending higher-tier quota.
TEST_MODE_ENV = "LLM_TEST_MODE"
TEST_TIER = "low"
