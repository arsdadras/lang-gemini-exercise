# EV-undated-flash-lite-false-memory-claims: Which low-tier model reliably calls the memory tool

| | |
| :--- | :--- |
| Status | current |
| Label | **[R]**: reconstructed from a code comment; no raw data; not re-run |
| Ran | During P5 Phase A, before 2026-09-13. The exact date isn't recorded |
| Question | Does the low-tier assistant model actually call the memory-write tool when it says it saved something? |
| Cited by | `src/agentlab/configs/personal_assistant_config.py` (`DEFAULT_ASSISTANT_PROVIDER = "openai"`), [P5 design card](../../../../docs/design_cards/P5_memory_assistant.md) point 13, [BR-002](../../briefs/BR-002-model-catalog-evidence-map/README.md) |

## Results

| Model (then `low` tier) | Behavior recorded |
| :--- | :--- |
| `gemini-3.5-flash-lite` | Claimed memory writes **without calling any tool** |
| `gpt-5.6-luna` | Did not show that behavior |

## Reading

This is why the P5 assistant pins provider `openai` inside the `low` tier. The pin still matters
since ADR-0014: the weighted ranking now puts Gemini first in `low`, and the pin overrides it.

## Limits

- No run count, scenario, or date survives. It's a qualitative observation, not a measurement.
- Architecture has changed since: memory writes moved to a background consolidator
  ([ADR-0012](../../../../docs/adr/0012-memory-consolidation-single-writer.md)) and the assistant only
  reads memory. So the original failure (claiming a write) can no longer happen the same way.
  The P5 eval-lite checks the related "false saved claim" case
  ([EV-2026-09-23-p5-eval-lite](../EV-2026-09-23-p5-eval-lite/README.md)).
- Whether the pin is still justified is an open question; see
  [BR-002](../../briefs/BR-002-model-catalog-evidence-map/README.md).
