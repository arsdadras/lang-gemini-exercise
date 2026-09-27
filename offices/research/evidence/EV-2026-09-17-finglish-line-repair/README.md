# EV-2026-09-17-finglish-line-repair: How much Perso-Arabic leaks, and how much line-level repair removes

| | |
| :--- | :--- |
| Status | current, but **the repair model has changed since** (see Limits) |
| Label | **[R]**: reconstructed from ADR and handoff prose; no raw data; not re-run |
| Ran | During P5 B3, recorded with [ADR-0010](../../../../docs/adr/0010-one-gate-in-memory-storage.md) (2026-09-17) |
| Question | How often does the assistant model write Perso-Arabic script in long replies, and which repair strategy fixes it? |
| Cited by | [ADR-0010](../../../../docs/adr/0010-one-gate-in-memory-storage.md) (decision and alternatives), `src/agentlab/middlewares/finglish_output_middleware.py` (design), [MENTOR_HANDOFF.md](../../../../archive/docs/MENTOR_HANDOFF.md) (known issue), [BR-002](../../briefs/BR-002-model-catalog-evidence-map/README.md) |

## Results

| Observation | Value |
| :--- | :--- |
| Leak rate of `gpt-5.6-luna` in a long plan | 30-50% of lines contain Perso-Arabic script |
| Line-level repair (leaked lines only, chunks of 20, two passes), on the `low` tier | 215 leaked lines → **55**, across three long plans: about a 75% reduction |
| Whole-answer rewrite | **Worse**: the rewriter introduced Perso-Arabic words of its own |

## Reading

- Line-level repair is the better strategy, and it is what the middleware implements. It fails
  open: a line that can't be repaired stays as it was.
- The root cause is the assistant model; repair only mitigates it.

## Limits

- **Three plans, one run each:** no per-plan breakdown survives.
- **The repair model has changed:** since 2026-09-23 the repair runs on the `opensource` tier
  (`glm-5.3`, [ADR-0014](../../../../docs/adr/0014-weighted-model-tier-catalog.md)). The 215 → 55
  figure was measured on the `low` tier and has not been re-measured on the new model. That is
  an open gap, also tracked by the office as RSK-08.
