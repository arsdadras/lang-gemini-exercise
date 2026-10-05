# EV-2026-09-19-hot-path-memory-writes: What happens to a profile when the assistant writes memory mid-conversation

| | |
| :--- | :--- |
| Status | current |
| Label | **[R]**: reconstructed from ADR prose; no transcripts or profile snapshots preserved |
| Ran | 2026-09-19, P5 build |
| Question | Does the assistant keep an accurate profile when it writes memory itself, during the conversation ("hot path")? |
| Cited by | [ADR-0012](../../../../docs/adr/0012-memory-consolidation-single-writer.md) (context for moving to a single background writer) |

## Setup

A live run of six conversations with the P5 assistant, which at the time wrote memory itself.

## Results

After six conversations, the profile had:

- **a conflicting job:** old and new both present;
- **a duplicated** diet fact;
- **a stale** city and gym goal;
- **missing facts** that were mentioned in passing (e.g. "recommend a restaurant in Karaj, I
  live here now"): never saved, because the assistant was busy with the actual request.

## Reading

The evidence behind ADR-0012's decision: the assistant reads memory only, and a background
consolidator is the single writer.

## Limits

- One run, no transcripts kept, and the model and tier used aren't recorded.
- The P5 eval-lite now tests the successor design
  ([EV-2026-09-23-p5-eval-lite](../EV-2026-09-23-p5-eval-lite/README.md)).
