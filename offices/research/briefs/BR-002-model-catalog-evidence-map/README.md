# BR-002: Which model choices in the code rest on evidence, and which don't?

| | |
| :--- | :--- |
| Status | current (code read 2026-09-26) |
| Addressed to | The project office (model tiers are a technology decision); the mentor, for measurement work |
| Related | [ADR-0014](../../../../docs/adr/0014-weighted-model-tier-catalog.md), [ADR-0015](../../../../docs/adr/0015-local-tier-and-test-mode-profiles.md), office risk RSK-08, `src/agentlab/configs/models_config.py`, `src/agentlab/configs/personal_assistant_config.py` |

## Short answer

The repo makes **eleven model choices** in code. **Three** rest on direct measurement, **five**
on partial or indirect evidence, and **three on none**. Most unmeasured is the ranking engine
itself: the speed/power/cost scores that order every tier are hand estimates.

## The map

| # | Choice in code | Evidence | Strength |
| :-: | :--- | :--- | :--- |
| 1 | **Tier ordering** from hand-scored `ModelScore` values and `TIER_WEIGHTS` (ADR-0014) | None. ADR-0014 itself says the scores are hand-estimated from public positioning | **None** |
| 2 | **`TEST_TIER` = `opensource` (`glm-5.3`)**, computed from those scores | `glm-5.3` scored 23/23 on our 23 decision cases ([EV-2026-09-25](../../evidence/EV-2026-09-25-laya-zero-shot/README.md)). The ranking that picked it comes from #1 | Partial |
| 3 | **Model IDs** in the catalog | 6 carried from the 2026-08-26 check (Gemini's two then on Google, not GapGPT); 2 Anthropic IDs from model knowledge; 4 never called. Two answer live today ([EV-2026-08-26](../../evidence/EV-2026-08-26-gapgpt-model-ids/README.md)) | Partial |
| 4 | **`local` tier:** 4B primary, opt-in only | Measured ([EV-2026-09-23-local-ollama-qwen](../../evidence/EV-2026-09-23-local-ollama-qwen/README.md)) | **Direct** |
| 5 | **P5 assistant pinned to `openai`** inside `low` | One qualitative observation, from before memory writes moved to the consolidator ([EV-undated](../../evidence/EV-undated-flash-lite-false-memory-claims/README.md)) | Partial and possibly stale |
| 6 | **Consolidator pinned to `claude-sonnet-5`** | Measured, but the two records disagree ([EV-2026-09-19](../../evidence/EV-2026-09-19-consolidator-model-comparison/README.md)) | **Direct**, but inconsistent |
| 7 | **Finglish repair on `opensource`** | The 215 → 55 result was measured on the old `low` repair model, and never re-run on `glm-5.3` ([EV-2026-09-17](../../evidence/EV-2026-09-17-finglish-line-repair/README.md)) | Indirect |
| 8 | **RAG document grading and query rewrite on `opensource`** | `glm-5.3` scored 6/6 on relevance in a small set; the rewrite is unmeasured | Partial |
| 9 | **Security guard on `low`** | The current `low` primary (`gemini-3.5-flash-lite`) scored 8/8 on memory-policy cases (EV-2026-09-25). The docstring's "live-validated against a data-exfiltration attempt" has no record in the repo | **Direct** on 8 cases |
| 10 | **Agent tiers:** researcher, repo-insight, and coordinator on `low`; interpreter on `medium` | None in this repo. AGENTS.md records low-tier models claiming tool actions they never took, which is qualitative | **None** |
| 11 | **`medium` for code review, skill drafting, and the RAG answer** | None | **None** |

## Reading

- **The ranking system is an engine without calibration data.** It is sound as design (one
  place owns the ordering and consumers follow it), but its inputs are guesses. So "the tier's
  primary" means "the best-guessed model", and nobody has measured whether it is the best.
- **Two pins may be obsolete or unexplained.**
  - #5: the failure that justified the pin (claiming a write) can't happen any more, because
    the assistant no longer writes memory.
  - #6: nobody can currently say what was measured.
- **The cheap-tier moves (#7, #8) carry the most unmeasured risk.** They route every RAG
  question and every Finglish repair. The office already tracks this as RSK-08.

## Recommendations

In order of value for effort. Advice only.

1. **Re-run the P5 eval-lite once per test profile** (`default`, `reliable`), and record each
   run as its own evidence record. It's the harness that already exists, and it refreshes #5,
   #6, and #7 at once.
2. **Verify every catalog ID** with one `GET /v1/models` on GapGPT plus one call per ID (#3).
   A wrong ID only surfaces when a fallback needs it.
3. **Measure the RAG graders and the Finglish repair on `opensource` against `low`**, using
   R2's planned labeled question set and a small leak corpus (#7, #8). That closes RSK-08.
4. **Replace the hand scores with measured ones when P9's "measured tier and cost choices"
   lands** (#1). This is sequencing: the metric definitions belong to that stage. Until then,
   the scores should say "estimated", as ADR-0014 does.
5. **Reconcile the consolidator records** (#6): find out whether two runs happened, or re-run the
   implicit-conflict scenario per model.
6. **Record the guard's live validation** (#9). If the run from the P5 C3 session can't be
   found, re-run a small adversarial set and record it.

## For the office

Mirrored in the [outbox](../../OUTBOX.md). Items 1-3 and 5-6 are mentor work that the office
may direct. Item 4 is already sequenced by the roadmap. The unexplained or possibly stale pins
(#5, #6) are a question for the office: keep them, drop them, or measure first.

## History

| Date | Change |
| :--- | :--- |
| 2026-09-26 | First version, from a repo-wide sweep for evidence behind model choices |
