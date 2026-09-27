# EV-2026-09-22-interrupt-resume-order: Resume values match `interrupt()` calls by order

| | |
| :--- | :--- |
| Status | current (LangGraph 1.2.11) |
| Label | **[R]**: reconstructed from ADR prose; the spike code wasn't kept |
| Ran | During the P5 consolidator build, recorded with [ADR-0012](../../../../docs/adr/0012-memory-consolidation-single-writer.md) (2026-09-22) |
| Question | If a node skips an `interrupt()` on re-run, which answer does the next `interrupt()` receive? |
| Cited by | [ADR-0012](../../../../docs/adr/0012-memory-consolidation-single-writer.md) ("one edit per graph step") |

## Results

Resume values are matched to `interrupt()` calls **by their order within a node**, not by
identity. The first consolidator build skipped files already stored before a pause, so on
resume the second question received the first answer, and a change the user had **rejected was
stored**.

## Reading

This is why the consolidator applies one edit per graph step, looping on a cursor, so each run
holds at most one pending approval and resumes exactly the question it paused on. It's a
general rule for any node with more than one `interrupt()`: never make the set of `interrupt()`
calls depend on state that changes across the pause.

## Limits

- Verified on LangGraph 1.2.11 only; re-check on upgrade.
- LangGraph also supports resuming by interrupt ID (visible in `tests/test_specialist_contract.py`
  fixtures, which build `Interrupt(..., id=...)`); whether ID-mapped resume avoids the problem
  wasn't tested in the spike.
