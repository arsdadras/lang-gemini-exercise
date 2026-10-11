# EV-2026-08-26-gapgpt-model-ids: Which model IDs were actually checked against the gateway

| | |
| :--- | :--- |
| Status | current, partial: most IDs in today's catalog were **not** part of this check |
| Label | **[R]**: reconstructed from the `models_config.py` docstring; no raw listing preserved |
| Ran | 2026-08-26 |
| Question | Do the catalog's model IDs exist on the gateway and answer a live call? |
| Cited by | `src/agentlab/configs/models_config.py` (module docstring), [ADR-0014](../../../../docs/adr/0014-weighted-model-tier-catalog.md), [BR-002](../../briefs/BR-002-model-catalog-evidence-map/README.md) |

## Results

The docstring records a check of the model IDs of that date against each gateway's
`/v1/models` list, plus one live call each.

Today's catalog (ADR-0014, 2026-09-23) splits into three groups by what backs each ID:

| IDs | What backs them |
| :--- | :--- |
| `gpt-5.6-{sol,terra,luna}`, `claude-sonnet-5` | Carried over from this check (GapGPT) |
| `gemini-3.8-flash`, `gemini-3.5-flash-lite` | Checked then on **Google's own API**. Since ADR-0014 the paid tiers route them through GapGPT, which that check didn't cover. The `free` tier still calls flash-lite on Google directly |
| `claude-opus-5-5`, `claude-haiku-4-5-20251001` | The session's own model knowledge. **Not** a gateway listing or live call |
| `gemini-3.8-pro`, `glm-5.3`, `qwen3-235b-a22b-instruct`, `deepseek-v4` | Nothing: added 2026-09-23 as illustrative picks, "pending a live check" |

## Reading

- `glm-5.3` answers live through GapGPT: it passed 23/23 in
  [EV-2026-09-25-laya-zero-shot](../EV-2026-09-25-laya-zero-shot/README.md) as the test-mode
  model.
- `gemini-3.5-flash-lite` answers through GapGPT as the `low` tier's primary (same record).
- The other new IDs have never answered a call in this repo. A wrong ID only surfaces when its
  tier's primary fails and the fallback reaches it.

## Limits

- No listing output was preserved for the original check.
- Verifying every current ID is one `GET /v1/models` plus one call per ID. It's listed in the
  [outbox](../../../../archive/offices/research/OUTBOX.md) for the owner of the catalog.
