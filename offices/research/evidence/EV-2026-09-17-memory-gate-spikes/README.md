# EV-2026-09-17-memory-gate-spikes: Where approval and refusal can live in a DeepAgents memory write

| | |
| :--- | :--- |
| Status | current (framework versions of that date) |
| Label | **[R]**: reconstructed from ADR prose; the spike code wasn't kept; not re-run |
| Ran | During P5 B3, recorded with [ADR-0010](../../../../docs/adr/0010-one-gate-in-memory-storage.md) (2026-09-17) |
| Question | Can a single enforcement point both ask for approval and refuse a memory write, and what breaks when a run resumes? |
| Cited by | [ADR-0010](../../../../docs/adr/0010-one-gate-in-memory-storage.md) |

## Results

| Spike or check | Finding |
| :--- | :--- |
| A storage backend that calls `interrupt()` itself | Pauses the run, works for the general-purpose subagent too, and needs no CLI change. One enforcement point can both ask and refuse |
| Custom agent middleware | Doesn't reach the general-purpose subagent (`deepagents/graph.py`, line 776 at the pinned version); the backend is shared by every agent |
| Resuming after an approval | The tool runs again, so a model-based verdict computed before the pause can differ after it: a rejected write executed because the second verdict was "allow" |
| `PIIMiddleware` | `apply_to_input` leaves the raw text in the input checkpoint; `apply_to_output` never touches tool-call arguments; `block` crashes the run. It protects the model's view, not persistence |

## Reading

These spikes are why approval lives in the storage layer and why the guard's verdict is cached
across a pause. See ADR-0010's decision.

## Limits

- The spike code and exact library versions weren't kept, beyond the line reference.
- These are framework behaviors that can change with any `deepagents` or `langchain` upgrade.
  Re-verify them when those pins move (the office's backlog plans upgrades to released
  versions, DEC-009).
