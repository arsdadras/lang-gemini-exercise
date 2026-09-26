# ADR-0014: Model catalog splits into 5 tiers, ranked by a weighted speed/power/cost score

- Status: Accepted
- Date: 2026-09-23

## Context

- The catalog had 3 provider tiers (`high`/`medium`/`low`, 2-3 hand-ordered providers each)
  plus an ad hoc `free` tier that actually held OpenRouter open-weight models
  (`z-ai/glm-5.3:free`, `nvidia/nemotron-...:free`), not a free model.
- The mentee asked for three changes: refresh the model IDs, add a real open-weight tier
  sourced from GapGPT (OpenRouter deferred for now), and stop hand-picking each tier's primary
  provider — pick it from an explicit speed/power/cost trade-off instead, since the three axes
  matter differently per tier (a `low`-tier call wants speed, `high` wants power, and so on).
- Anthropic's current model line (Opus 5.5, Sonnet 5, Haiku 4.5) is authoritative from the
  runtime's own system context; OpenAI's `gpt-5.6-{sol,terra,luna}` and Gemini's ids were last
  verified against GapGPT's `/v1/models` on 2026-08-26 and are carried forward unchanged for
  lack of a live check in this session.

## Decision

- **Five tiers.** `high`/`medium`/`low` keep their meaning (paid, capability-ordered), now with
  all three main providers (OpenAI, Anthropic, Gemini) present in each, all routed through
  GapGPT. `opensource` is new: cheap, well-known open-weight models (GLM, Qwen, DeepSeek),
  also through GapGPT. `free` is redefined to hold exactly one thing: Gemini Flash-Lite called
  directly against Google's own API (`GOOGLE_API_KEY`, no GapGPT). OpenRouter's builder and
  its free-tier entries are removed outright (cheap to re-add; nothing referenced it outside
  `models_config.py`).
- **A tier's provider order is computed, not hand-picked.** `ModelScore(speed, power, cost)`
  (0-1, `cost` inverted so higher is always better) scores each provider per tier; `TIER_WEIGHTS`
  gives each tier's own importance per axis (`high` weights power heaviest, `medium` cost,
  `low` speed, `opensource` cost then power). `_ranked()` sorts a tier's dict by the weighted
  dot product, descending; dict order is what `models.registry_model` already reads as
  primary-then-fallback, so no change was needed there.
- **`TEST_TIER` is derived the same way**, comparing each of `free`/`opensource`/`low`'s own
  primary under cost-and-speed-heavy test-mode weights. It resolves to `opensource` (`glm-5.3`):
  `free`'s Gemini Flash-Lite is scored down on speed because Google's no-cost quota has a
  strict RPM/RPD cap that throttles a real test loop, while the same model routed through
  GapGPT (the `low` tier's Gemini entry) has no such ceiling.
- **Call-site audit, applied everywhere `llm_model.get`/`chain` is called:**
  - Moved to `opensource`: [`rag_node.grade_documents_node`](../../src/agentlab/nodes/rag_node.py)
    and `query_rewrite_node` (per-document binary filter and a query rewrite — high call
    volume, low blast radius, self-corrects through the existing retry loop), and
    [`finglish_output_middleware`](../../src/agentlab/middlewares/finglish_output_middleware.py)
    (a fail-open formatting repair, not a quality or security gate).
  - Left on a paid tier, deliberately, with the reason now recorded as a comment at each site:
    - Every DeepAgents agent built with `llm_model.get()` (`web_researcher`, `repo_insight`,
      `coding_coordinator`, `interpreter`, `personal_assistant`): these bind tools and run
      multi-step tool loops, where AGENTS.md already documents low-tier proprietary models
      occasionally claiming a tool action they never took. GapGPT's open-weight catalog has no
      verified function-calling track record in this repo; regressing agentic reliability to
      chase a cost saving here is exactly backwards.
      `personal_assistant_agent` additionally pins `provider="openai"` on empirical grounds
      already in `personal_assistant_config.py` (Gemini on the same tier silently skipped a
      memory-write tool call), unaffected by the ranking change either way.
    - Quality/trust gates: `rag_node.check_hallucination_node`, `web_search_fallback_node`,
      `generate_node`, `groundedness_middleware`, `security_guard_middleware`,
      `code_review_node`'s three chains, `skill_designer_node`, `memory_consolidation_node`
      (the last pinned to `claude-sonnet-5` on a 6/6-vs-4/6 result already recorded in
      ADR-0012; see the erratum below). These are the specific things each project's lessons demonstrate working, or a
      security boundary; none has a live-verified opensource-tier baseline to fall back to.

## Consequences

- Adding, removing, or re-scoring one provider re-derives every tier's order and `TEST_TIER`
  automatically; a stale hand-ordered dict can no longer drift from the scores that justify it.
- `finglish_output_middleware` now repairs Perso-Arabic leaks with `glm-5.3` instead of a
  provider model. This task (targeted transliteration repair with a strict output schema) has
  no live-verified success rate on GapGPT's open-weight catalog; MENTOR_HANDOFF's existing
  Perso-Arabic known issue should get a follow-up measurement once the eval-lite pattern
  (ADR-0004) covers it. Failure is bounded (the guard fails open, per its own docstring) but
  not yet measured.
- `opensource` and `free` stay outside `TIER_CASCADE_ORDER`, so `cascade=True` still only
  reaches paid provider tiers; nothing implicitly downgrades to an open-weight or free model a
  caller didn't request.
- All `ModelScore` values are hand-estimated (see `models_config.py`'s module docstring), not
  measured; they're a documented, revisable starting point, not a benchmark result.

## Alternatives considered

- **Route the new open-weight tier through OpenRouter** (the original `free` tier's actual
  gateway): rejected for now per the mentee's own instruction; GapGPT already holds the
  provider tiers, so one gateway is one fewer credential and one fewer base URL to reason
  about until a concrete reason needs OpenRouter specifically.
- **Blanket-migrate every existing `low`-tier call to `opensource`:** rejected; several of those
  calls are exactly the quality or security gates each project's lessons rely on, and GapGPT's
  open-weight structured-output reliability isn't verified in this repo (MENTORING.md Principle
  3: verify before handing over).
- **Keep hand-ordered tiers and only refresh model ids:** rejected; it satisfies "update" but
  not "optimize the selection system," which the mentee asked for explicitly and separately.

## Erratum (2026-09-26)

The consolidator comparison cited above is 3/3 vs 0/3 in ADR-0012, not 6/6 vs 4/6; the two
records of that run disagree (`EV-2026-09-19-consolidator-model-comparison`). The pin and this
decision are unchanged; research is reconciling the records (LD-005).
