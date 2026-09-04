"""LLM model registry configuration — capability tier × provider.

Each tier ("low"/"medium"/"high"/"free") maps provider name -> `init_chat_model(...)`
kwargs. A tier's providers are tried in the order listed — the first is the
default/primary for that tier, the rest are the fallback chain *within the
same capability tier* (so a rate-limited call retries at the same capability
level, not silently downgraded to a cheaper tier). See `models.registry_model`.

Provider keys name the underlying model *brand* ("gemini"/"openai"/"anthropic"),
not the router used to reach it — GapGPT is a single OpenAI-compatible gateway
that proxies OpenAI *and* Anthropic models (and others); both use
`model_provider="openai"` (the wire protocol) with GapGPT's `base_url`/`api_key`,
same client class, different `model` string per underlying brand.

Only providers with a model verified to exist and respond are listed here —
don't add a placeholder model name that hasn't actually been confirmed to
work against the real API. Verified against GapGPT's own `/v1/models` list
and a live `.invoke()` per model (2026-08-26): `gpt-5.6-luna`, `gpt-5.6-terra`,
`gpt-5.6-sol`, `claude-opus-5`, `claude-sonnet-5` all exist and respond.
`free` tier verified against OpenRouter's own `/v1/models` list (only
`:free`-suffixed IDs) and a live `.invoke()`: `z-ai/glm-5.2:free`,
`nvidia/nemotron-3-ultra-550b-a55b:free`.
"""

import os

_GAPGPT_BASE = {
    "model_provider": "openai",
    "base_url": os.getenv("GAPGPT_BASE_URL"),
    "api_key": os.getenv("GAPGPT_API_KEY"),
    "temperature": 0,
}

_OPENROUTER_BASE = {
    "model_provider": "openai",
    "base_url": "https://openrouter.ai/api/v1",
    "api_key": os.getenv("OPENROUTER_API_KEY"),
    "temperature": 0,
}

_GEMINI_BASE = {
    "model_provider": "google_genai",
    "api_key": os.getenv("GOOGLE_API_KEY"),
    "temperature": 0,
    "top_p": 0.95,
}


MODEL_TIERS = {
    "high": {
        "gemini": {"model": "gemini-3.1-pro", **_GEMINI_BASE},
        "openai": {"model": "gpt-5.6-sol", **_GAPGPT_BASE},
        "anthropic": {"model": "claude-opus-5", **_GAPGPT_BASE},
    },
    "medium": {
        "gemini": {"model": "gemini-3.8-flash", **_GEMINI_BASE},
        "openai": {"model": "gpt-5.6-terra", **_GAPGPT_BASE},
        "anthropic": {"model": "claude-sonnet-5", **_GAPGPT_BASE},
    },
    "low": {
        "gemini": {"model": "gemini-3.5-flash-lite", **_GEMINI_BASE},
        "openai": {"model": "gpt-5.6-luna", **_GAPGPT_BASE},
    },
    "free": {
        "glm": {"model": "z-ai/glm-5.2:free", **_OPENROUTER_BASE},
        "nvidia": {
            "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
            **_OPENROUTER_BASE,
        },
    },
}

# Provider order per tier — first is primary/default, rest are same-tier fallbacks.
TIER_PROVIDER_ORDER = {tier: list(providers) for tier, providers in MODEL_TIERS.items()}

# "free" is opt-in only (explicitly request `.chain("free")`) — never a silent
# fallback destination for the paid tiers, so it's not the module default.
DEFAULT_TIER = "low"

# Opt-in cascade order for `.chain(..., cascade=True)` / `retry_on_failure(tier, cascade=True)`:
# once a tier's own providers are all exhausted, fall through to the next tier
# down rather than failing outright. Off by default everywhere — same-tier-only
# fallback (`fallback_models()`) is still what every call site uses unless it
# explicitly asks for cascade.
TIER_CASCADE_ORDER = ["high", "medium", "low"]

# Route every tier through TEST_TIER's models instead — flip via `.env`
# (`LLM_TEST_MODE=true`) to iterate on routing/prompt/fallback logic cheaply
# without spending paid-tier quota; leave unset (default off) for real runs.
TEST_MODE = os.getenv("LLM_TEST_MODE", "false").strip().lower() in {"1", "true", "yes"}
TEST_TIER = "low"

