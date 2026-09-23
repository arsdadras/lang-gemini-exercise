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

## Follow-up: measured 2026-09-23

Both models pulled (`qwen3.5:2b`, Q8_0; `qwen3.5:4b`, Q4_K_M) and `ollama serve` running
locally. Called both, live, through `models.registry_model.build_chat_model` (no mocking) with
five checks each: a one-word plain chat, three of this repo's actual structured-output schemas
(`GradeDocument`, `GuardVerdict`, `FinglishLines`), and `bind_tools` with one tool. Script kept
at `alireza`-adjacent scratch, not committed (ADR-0004: live checks run by hand, not by pytest).

| Check | qwen-2b | qwen-4b |
| :--- | :--- | :--- |
| Plain chat | OK, 139s (cold start) | OK, 23s |
| `GradeDocument` (RAG relevance) | OK, 154s, correct | OK, 92s, correct |
| `GuardVerdict` (security guard) | OK, 211s, correctly blocked a prompt-injection attempt, reasoned answer | OK, 110s, correctly blocked, better-reasoned |
| `FinglishLines` (2-line repair) | **FAILED**, 241s, `OutputParserException: Invalid json output` | OK, 357s, correct transliteration |
| `bind_tools([add]).invoke(...)` | OK, 8s, correct tool call and args | OK, 11s, correct tool call and args |

**Reading it:**
- Both models are `qwen35` family with a `thinking` capability (per `ollama show`/API tags):
  they reason before answering, which is almost certainly why every structured-output call
  costs 90-360s even once "warm" — this looks CPU-bound with reasoning overhead, not raw
  weight-loading time (the 139s/23s plain-chat gap between 2b's first call and 4b's second is
  consistent with 2b eating the one-time cold-start cost). No GPU offload was confirmed either
  way; that's the most likely next lever if this needs to get faster.
- `qwen-4b` was strictly more reliable: it's the only one of the two that produced valid JSON
  for a task needing several correctly-formatted fields across multiple lines. `qwen-2b`
  handled the simpler single-field schemas fine but broke on `FinglishLines`.
- Tool-calling itself (`bind_tools`) worked correctly and fast (single digits of seconds) on
  both — the slow path is specifically structured-output-with-reasoning, not tool dispatch.
- **Decision:** keep both, `qwen-4b` primary (already the order in `MODEL_TIERS["local"]`,
  confirmed correct by this data, not just the a-priori guess it started as). Do **not** add
  `local` to `TEST_TIER` auto-selection or any profile's default — at 90-360s per call it is
  roughly 20-100x slower than `opensource`'s GapGPT-routed `glm-5.3` for the exact same kind of
  call, which is disqualifying for anything interactive. It stays reachable only via
  `LLM_TEST_PROFILE=local` or an explicit `tier="local"`, for genuinely patient, offline,
  zero-cost iteration — not for the two call sites already on `opensource`
  (`rag_node.grade_documents_node`/`query_rewrite_node`, `finglish_output_middleware`): at this
  latency those would turn a single RAG query or Finglish repair pass into several minutes.
  `qwen-2b`'s `FinglishLines` failure independently confirms ADR-0014's caution about
  unverified structured-output reliability on a cheap tier was the right call, not overcaution.

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
