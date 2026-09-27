# EV-2026-09-23-p5-eval-lite: P5 memory assistant against real models, first full run

| | |
| :--- | :--- |
| Status | current |
| Label | **[R]** for the result (only the score survives); the harness itself is live code |
| Ran | 2026-09-23, P5 C2 ([ADR-0013](../../../../docs/adr/0013-p5-completion.md)) |
| Question | Do the real models behave as P5's design assumes: recall, isolation between users, honest "saved" claims, consolidation quality, and guard decisions? |
| Cited by | [MENTOR_HANDOFF.md](../../../../docs/MENTOR_HANDOFF.md) (P5 status), [ADR-0013](../../../../docs/adr/0013-p5-completion.md) |

## Setup

- **Harness:** [`evals/p5_memory_eval.py`](../../../../evals/p5_memory_eval.py), which the
  mentor owns. Scenario checks run outside pytest; the script exits 1 on any failure.
- **What it covers:**
  - assistant recall;
  - user isolation;
  - false "saved" claims;
  - consolidator updates, request flags, implicit conflicts, invented facts, and re-proposed
    rejections;
  - the guard on labeled writes.
- **Models:** the tiers configured in P5 at the time. Whether test mode was used isn't recorded.

## Results

**13/13 scenarios passed** on one live run.

## Reading

P5's model-dependent behavior held on that run. One run can't show a pass rate: each scenario
is a single sample from a stochastic model.

## Limits

- One run, and no per-scenario output or timing kept.
- The model catalog changed afterwards (ADR-0014): the `low` tier's primary, the Finglish repair
  model, and the RAG graders moved. A re-run is the cheapest way to refresh this record and would
  go in a new record.
- To use it for a model comparison, run it once per tier or profile and record them separately.
