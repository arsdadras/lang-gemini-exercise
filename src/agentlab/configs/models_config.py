"""Chat model catalog: capability tier x provider, ranked by a weighted score.

Five tiers. ``high``/``medium``/``low`` are the three paid provider tiers (OpenAI,
Anthropic, Gemini), all routed through the GapGPT gateway. ``opensource`` is a
cheap tier of well-known open-weight models, also through GapGPT. ``free`` is the
only tier that bypasses GapGPT entirely: it calls Gemini Flash-Lite directly
against Google's own API, so it costs nothing even with no GapGPT credit.
OpenRouter is deferred for now (no tier routes through it); add an
``_openrouter()`` builder back when a real use case needs it.

Each tier's provider order (first = primary, rest = same-tier fallback, per
``models.registry_model``) is not hand-picked: it's the descending order of a
weighted score over three axes (speed, power, cost — see ``ModelScore``), with
weights chosen per tier in ``TIER_WEIGHTS``. So a tier's primary changes
automatically if a provider's scored profile changes, instead of silently
drifting out of sync with a hardcoded order.

Model IDs were verified against each gateway's ``/v1/models`` list and a live
call on 2026-08-26, except the Anthropic IDs (Opus 5.5, Sonnet 5, Haiku 4.5),
confirmed current as of this update, and the ``opensource`` entries, which are
illustrative reputable open-weight picks (GLM, Qwen, DeepSeek) pending a live
check against GapGPT's catalog. Verify any new ID the same way before relying
on it in production.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelSpec:
    """Arguments for ``init_chat_model``; secrets are referenced by env var name.

    ``api_key_env`` is ``None`` for a self-hosted backend (``local``) that takes no key.
    """

    model: str
    model_provider: str
    api_key_env: str | None = None
    base_url: str | None = None
    base_url_env: str | None = None
    temperature: float = 0.0
    top_p: float | None = None


@dataclass(frozen=True)
class ModelScore:
    """A profile over three axes, each normalized 0-1 where higher is always better.

    ``cost`` is inverted (1.0 = cheapest) so all three axes read the same direction
    and can be combined with a single dot product. Used two ways in this module:
    as a provider's scored profile in ``_CANDIDATE_SCORES``, and as a tier's axis
    weights in ``TIER_WEIGHTS`` (a weight triple also sums to ~1.0).
    """

    speed: float
    power: float
    cost: float

    def weighted(self, weight: "ModelScore") -> float:
        return (
            self.speed * weight.speed
            + self.power * weight.power
            + self.cost * weight.cost
        )


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


def _ollama(model: str) -> ModelSpec:
    """A model served locally by ``ollama serve`` (no API key; ``OLLAMA_HOST`` if not default)."""
    return ModelSpec(
        model=model,
        model_provider="ollama",
        base_url_env="OLLAMA_HOST",
    )


# Hand-estimated per provider/model family from public benchmark positioning
# (power), published gateway throughput (speed), and GapGPT per-1M-token pricing
# (cost, inverted). Re-score a row whenever that family's generation changes.
# The "free" row's gemini entry is the *same* flash-lite model as "low"'s gemini
# entry, scored lower on speed: Google's no-cost quota has a strict RPM/RPD cap
# that throttles it under sustained load, while the low tier's GapGPT-routed copy
# has no such ceiling.
_CANDIDATE_SCORES: dict[str, dict[str, ModelScore]] = {
    "high": {
        "openai": ModelScore(speed=0.45, power=0.90, cost=0.35),
        "anthropic": ModelScore(speed=0.40, power=0.95, cost=0.30),
        "gemini": ModelScore(speed=0.55, power=0.83, cost=0.45),
    },
    "medium": {
        "gemini": ModelScore(speed=0.75, power=0.65, cost=0.65),
        "openai": ModelScore(speed=0.65, power=0.70, cost=0.55),
        "anthropic": ModelScore(speed=0.60, power=0.75, cost=0.50),
    },
    "low": {
        "gemini": ModelScore(speed=0.90, power=0.40, cost=0.85),
        "anthropic": ModelScore(speed=0.85, power=0.50, cost=0.70),
        "openai": ModelScore(speed=0.80, power=0.45, cost=0.75),
    },
    "opensource": {
        "glm": ModelScore(speed=0.65, power=0.70, cost=0.95),
        "qwen": ModelScore(speed=0.70, power=0.65, cost=0.92),
        "deepseek": ModelScore(speed=0.55, power=0.75, cost=0.90),
    },
    "free": {
        "gemini": ModelScore(speed=0.55, power=0.40, cost=1.0),
    },
}

# Per-tier importance of speed/power/cost; this is what actually decides a tier's
# provider order (``_ranked`` sorts by this, descending). Only tiers with more than
# one candidate need a weight row.
TIER_WEIGHTS: dict[str, ModelScore] = {
    "high": ModelScore(speed=0.15, power=0.60, cost=0.25),  # capability leads
    "medium": ModelScore(speed=0.25, power=0.25, cost=0.50),  # cost leads
    "low": ModelScore(speed=0.55, power=0.10, cost=0.35),  # speed leads
    "opensource": ModelScore(speed=0.25, power=0.30, cost=0.45),  # cost leads, power over speed
}


def _ranked(tier: str, specs: dict[str, ModelSpec]) -> dict[str, ModelSpec]:
    """Order a tier's providers by weighted score, best first (= primary)."""
    weight = TIER_WEIGHTS[tier]
    scores = _CANDIDATE_SCORES[tier]
    order = sorted(specs, key=lambda name: scores[name].weighted(weight), reverse=True)
    return {name: specs[name] for name in order}


MODEL_TIERS: dict[str, dict[str, ModelSpec]] = {
    "high": _ranked(
        "high",
        {
            "openai": _gapgpt("gpt-5.6-sol"),
            "anthropic": _gapgpt("claude-opus-5-5"),
            "gemini": _gapgpt("gemini-3.8-pro"),
        },
    ),
    "medium": _ranked(
        "medium",
        {
            "gemini": _gapgpt("gemini-3.8-flash"),
            "openai": _gapgpt("gpt-5.6-terra"),
            "anthropic": _gapgpt("claude-sonnet-5"),
        },
    ),
    "low": _ranked(
        "low",
        {
            "gemini": _gapgpt("gemini-3.5-flash-lite"),
            "openai": _gapgpt("gpt-5.6-luna"),
            "anthropic": _gapgpt("claude-haiku-4-5-20251001"),
        },
    ),
    "opensource": _ranked(
        "opensource",
        {
            "glm": _gapgpt("glm-5.3"),
            "qwen": _gapgpt("qwen3-235b-a22b-instruct"),
            "deepseek": _gapgpt("deepseek-v4"),
        },
    ),
    # Opt-in only: never the default tier and never part of a paid tier's fallback
    # or cascade (see TIER_CASCADE_ORDER). The one tier that bypasses GapGPT.
    "free": {
        "gemini": _gemini("gemini-3.5-flash-lite"),
    },
    # Opt-in only, same as "free". $0 and no rate limit, but needs `ollama serve` running
    # with the model already pulled locally; nothing falls back to it automatically.
    # Order and both entries live-verified 2026-09-23 against a real `ollama serve` — see
    # ADR-0015's follow-up for what was actually measured.
    "local": {
        "qwen-4b": _ollama("qwen3.5:4b"),
        "qwen-2b": _ollama("qwen3.5:2b"),
    },
}

DEFAULT_TIER = "low"

# Order for opt-in cross-tier cascade (``cascade=True``): after a tier's own
# providers fail, fall through to each lower tier in turn. "free", "opensource", and
# "local" are opt-in only and deliberately excluded, so a cascade never lands on an
# unmetered, unverified-reliability, or possibly-offline model a caller didn't ask for.
TIER_CASCADE_ORDER: tuple[str, ...] = ("high", "medium", "low")

# Set ``LLM_TEST_MODE=true`` to route every request to TEST_TIER while iterating
# on prompts or routing without spending higher-tier quota.
TEST_MODE_ENV = "LLM_TEST_MODE"

# The best tier for iteration, picked the same way as a tier's primary provider:
# highest weighted(speed, power, cost) among each candidate tier's own primary,
# under test-mode weights that favor cost and speed over power (cheap, fast
# feedback loops while prompt-tuning don't need frontier reasoning). "free" loses
# to "opensource" here despite costing nothing, because its rate-limit-throttled
# speed score drags its total below glm-5.3's.
_TEST_MODE_WEIGHT = ModelScore(speed=0.35, power=0.15, cost=0.50)
_TEST_TIER_CANDIDATES = ("free", "opensource", "low")
TEST_TIER = max(
    _TEST_TIER_CANDIDATES,
    key=lambda tier: _CANDIDATE_SCORES[tier][
        next(iter(MODEL_TIERS[tier]))
    ].weighted(_TEST_MODE_WEIGHT),
)

# Test-mode profiles: with LLM_TEST_MODE=true, ``LLM_TEST_PROFILE=<name>`` picks which cheap
# tier every request routes to, read fresh on each call (models.registry_model), so switching
# scenarios mid-session is a shell env var, not a code change. Reach for a non-default profile
# when the current one keeps failing a specific task (swap to another cheap tier that handles
# it better) or when the scenario's cost/reliability trade-off changes (offline work, a task
# that can tolerate more token-burn savings, or trying the local model once it's usable). See
# ADR-0015 for why each of these four, and not more, earned a profile.
TEST_MODE_PROFILE_ENV = "LLM_TEST_PROFILE"
DEFAULT_TEST_PROFILE = "default"
TEST_MODE_PROFILES: dict[str, str] = {
    "default": TEST_TIER,  # best speed/power/cost mix across free/opensource/low; see TEST_TIER
    "cheapest": "free",  # $0 via Google directly; accept its rate limit and lower power
    "reliable": "low",  # a real paid provider tier, for when a cheap model mishandles a task
    "local": "local",  # $0, no rate limit, needs `ollama serve` with the model already pulled
}
