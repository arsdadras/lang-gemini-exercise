# EV-2026-09-19-consolidator-model-comparison: Which medium-tier model catches conflicting memory facts

| | |
| :--- | :--- |
| Status | current, **with an unresolved inconsistency** (see Reading) |
| Label | **[R]**: reconstructed; no script or raw output preserved; not re-run |
| Ran | 2026-09-19 (per the config comment), during the P5 build |
| Question | When a new fact contradicts an old one under a different heading (a new diet vs an old food preference), which model notices and proposes the fix? |
| Cited by | `src/agentlab/configs/personal_assistant_config.py` (`CONSOLIDATOR_TIER`, `CONSOLIDATOR_PROVIDER`), [ADR-0012](../../../../../docs/adr/0012-memory-consolidation-single-writer.md), [ADR-0014](../../../../../docs/adr/0014-weighted-model-tier-catalog.md), [BR-002](../../briefs/BR-002-model-catalog-evidence-map/README.md) |

## Setup

The only surviving description is prose in the two places below:

- **Config comment:** "3 runs per case", with cases of an implicit conflict between facts
  under different headings. The case count isn't stated; 6 runs per model implies 2 cases.
- **ADR-0012:** one case, "an implicit diet conflict", 3 runs per model.

## Results

| Source | `claude-sonnet-5` | `gpt-5.6-terra` | `gemini-3.8-flash` |
| :--- | :---: | :---: | :---: |
| Config comment | 6/6 | 4/6 | rate-limited, no result |
| ADR-0012 | 3/3 | 0/3 | not mentioned |

## Reading

- **Both sources agree on the outcome:** `claude-sonnet-5` resolved every run and was pinned as
  the consolidator (medium tier, provider `anthropic`).
- **They cannot describe the same six runs.** If `gpt-5.6-terra` scored 0/3 on the diet case,
  a 4/6 total needs 4 of 3 runs on the other case. So either there were two separate runs (one
  of 2 cases, one of the diet case alone), or one of the two figures is wrong. This record can't
  tell which.
- **A third, wrong citation:** ADR-0014 cites this result as "6/6-vs-4/6 already recorded in
  ADR-0012", but ADR-0012 records 3/3 vs 0/3. Reported in the [outbox](../../../../../archive/offices/research/OUTBOX.md).

## Limits

- No raw output, no prompts, and no case list survive, so the result can't be audited.
- The sample is small either way: n = 3 or 6 per model.
- Gemini has no result at all; its rate limit, not its quality, excluded it.
- Re-measuring would need the P5 eval-lite's implicit-conflict scenario
  ([EV-2026-09-23-p5-eval-lite](../EV-2026-09-23-p5-eval-lite/README.md)) run per model.
