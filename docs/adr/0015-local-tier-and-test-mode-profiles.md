# ADR-0015: A `local` model tier (Ollama), and named test-mode profiles

- Status: Accepted
- Date: 2026-09-23

## Context

- ADR-0014 gave the catalog `free`/`opensource`/`low`/`medium`/`high`, all API-metered (either
  GapGPT or Google's paid-adjacent free quota). The mentee is about to pull `qwen3.5:2b` into a
  local Ollama server (`OLLAMA_HOST=http://127.0.0.1:11434`, not downloaded as of this writing)
  and wants a $0, no-rate-limit option in the mix, with an explicit note to drop it again if it
  turns out not to earn its place.
- Separately, `LLM_TEST_MODE=true` only ever had one substitution target (`TEST_TIER`, fixed at
  import time). The mentee wants to switch which cheap tier test mode uses *while iterating*, no
  code change, no restart-and-edit-a-constant: e.g. a task the current cheap model keeps
  mishandling should be retryable on a different cheap tier without leaving test mode, and a
  scenario with no GapGPT credit (or one that wants to burn as few tokens as possible) should be
  reachable the same way.

## Decision

- **A fifth, opt-in-only tier, `local`** (`MODEL_TIERS["local"] = {"qwen": _ollama("qwen3.5:2b")}`
  in `models_config.py`). `_ollama()` sets `model_provider="ollama"` (needs `langchain-ollama`,
  added as a dependency) and `base_url_env="OLLAMA_HOST"`; no API key. `ModelSpec.api_key_env`
  became `str | None` for this (`build_chat_model` now only sets the `api_key` kwarg when an env
  var name is actually given — verified against `ChatOllama`'s fields, which has no `api_key` at
  all, and against a real `init_chat_model(..., model_provider="ollama", api_key=None)` call,
  which builds cleanly). `local` is excluded from `TIER_CASCADE_ORDER`, same as `free` and
  `opensource`: nothing should silently fail over to a server that might not be running.
  **Not live-verified**: the model isn't pulled yet, so nothing has actually called it. Treat
  every score and claim about it below as provisional until it is.
- **Named test-mode profiles.** `TEST_MODE_PROFILES` (`models_config.py`) maps a short name to a
  tier: `default` → `TEST_TIER` (currently `opensource`), `cheapest` → `free`, `reliable` → `low`,
  `local` → `local`. `LLM_TEST_PROFILE=<name>` (read fresh per call, mirroring
  `is_test_mode_enabled`) picks one; unset means `default`, so existing `LLM_TEST_MODE=true`
  usage is unaffected. `LLMRegistry.resolve_tier` only consults this map when a profile map was
  actually injected (production's `llm_model` singleton passes `TEST_MODE_PROFILES`; the
  registry's own unit tests never do, so they keep testing plain `test_tier` substitution
  unchanged). An unknown profile name raises immediately, same style as an unknown tier or
  provider, instead of silently falling back and hiding a typo.
- **Four profiles, not more, on purpose:** `default` covers the common case; `cheapest` and
  `reliable` are the two directions away from it that actually differ in kind (cost-not-power vs.
  power-not-cost, using two tiers already scored in ADR-0014); `local` is the only one that
  changes *where* inference happens rather than which paid tier answers. A profile per model or
  per project was considered and rejected: nothing yet needs finer granularity than "which of
  these four trade-offs", and `provider=` on `llm_model.get/chain` already lets any call pin an
  exact model when it needs to.

## Consequences

- Switching scenarios mid-session is `export LLM_TEST_PROFILE=local` (or `cheapest`/`reliable`)
  in the shell before the next `uv run lab-*` or `pytest` invocation — no code edit, no registry
  rebuild (each CLI run is a fresh process, so a fresh `os.getenv` read is all "mid-session
  switching" needs here).
- `local`'s `ModelScore` doesn't exist yet in `_CANDIDATE_SCORES` and it is deliberately kept out
  of the `TEST_TIER` auto-selection in ADR-0014: an unverified, possibly-offline backend must
  never become the automatic default. It's reachable only by explicitly asking for the `local`
  profile (or `tier="local"` directly).
- Follow-up, once the model is actually pulled and called at least a few times: measure it (does
  it answer at all through this stack, how slow, how good for the tasks it'll realistically see)
  and only then decide whether it earns a permanent `ModelScore` row and a place in automatic
  selection, or gets removed again per the mentee's own instruction to drop what doesn't pull its
  weight. Track this in `docs/MENTOR_HANDOFF.md` until it's resolved either way.

## Alternatives considered

- **Make `LLM_TEST_PROFILE` hold a tier name directly, no indirection through named profiles:**
  rejected; a bare tier name (`LLM_TEST_PROFILE=free`) is one env var away from being
  indistinguishable from just setting `tier=` per call, and loses the one thing a profile name
  buys: a short, memorable label for *why* ("cheapest", "reliable") instead of *what*.
- **Auto-detect whether Ollama is reachable and silently fall back:** rejected; the existing
  cascade/fallback machinery already exists for verified providers, and silently swallowing a
  down local server would hide exactly the signal ("is `local` actually usable yet?") this ADR
  is trying to preserve.
- **Wait until the model is downloaded and tested before adding any of this:** rejected for the
  tier/profile plumbing (cheap, reversible, and needed regardless of which local model ends up
  pulled) but is exactly why `local` stays unscored and out of automatic selection until then.
