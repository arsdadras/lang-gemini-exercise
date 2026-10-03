---
title: Models at hand
maintainer: lead
status: current
updated: 2026-10-03
summary: The two model families as this repo runs them: the LLM tiers, fallback, and test mode; the decision models; which choices rest on measurement; and how tiers will be chosen.
related: [radar.md, ../architecture/decision-models.md, ../../docs/adr/0014-weighted-model-tier-catalog.md, ../../docs/adr/0015-local-tier-and-test-mode-profiles.md, ../../offices/lead/research/briefs/BR-002-model-catalog-evidence-map/README.md]
---

# Models at Hand

The practical picture of the models this repo runs. Model IDs live only in
[`configs/models_config.py`](../../src/agentlab/configs/models_config.py), and secrets are named
by environment variable; neither is copied here. Rings and versions:
[radar.md](radar.md). The rules for decision points:
[decision-models.md](../architecture/decision-models.md).

## Embeddings

The RAG index embeds with GapGPT's `text-embedding-3-small` (1536 dimensions), through the same
OpenAI-compatible gateway as the paid tiers (`EMBEDDING_SPEC` in `configs/models_config.py`,
live-verified 2026-10-03, with the same call timeout as every external client). It replaced
Gemini's embeddings at the user's instruction, so Google serves only the `free` tier. Changing the
embedding model means rebuilding `.chroma_index`: the old vectors are Gemini's and a different
width, so the RAG graph answers nothing until the rebuild (R2).

## LLM tiers

| Tier | Served by | Use |
| :--- | :--- | :--- |
| `high`, `medium`, `low` | GapGPT gateway: OpenAI, Anthropic, Gemini | The default tiers; `low` is the default |
| `opensource` | GapGPT: GLM, Qwen, DeepSeek | Low-stakes nodes only, until measured (RSK-08) |
| `free` | Google directly (Gemini Flash-Lite) | Quota-limited; a fallback when the gateway is down |
| `local` | Ollama on this machine | Opt-in; 90-360 s per structured call here |

- **Calling them** (`AGENTS.md` convention 3): an agent takes `llm_model.get(tier, provider)`
  with `make_model_fallback(tier, primary=provider)`; a graph node or middleware takes
  `llm_model.chain(tier, structured=Schema)`.
- **Inside a tier,** providers are ordered by a weighted speed, power, and cost score
  ([ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md)), and the fallback middleware
  moves to the next provider when one fails
  ([ADR-0007](../../docs/adr/0007-built-in-model-fallback.md)). An opt-in `cascade=True` also
  falls down the tiers (`high`, `medium`, `low`); it becomes the "fallback order" when the
  quality escalation lands (DEC-025).
- **Test mode:** `LLM_TEST_MODE=true` routes every tier to a test tier, per command, never by
  editing `.env`. `LLM_TEST_PROFILE` picks `default` (computed from the scores; `opensource` on
  2026-09-28), `cheapest` (`free`), `reliable` (`low`), or `local`
  ([ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md)).

## Decision models

Jev, pinned to `typesafe/jev-1.13`, through OpenRouter's System One API, behind `decision_model`
from R1 ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md)). Measured
here on 2026-09-27: about 0.45 s and $0.00002 per decision; 22/23 on our grader and guard cases
with no guard answer less strict than its label; routing 32/32 in three runs
(`EV-2026-09-27-jev-openrouter`, `EV-2026-09-27-jev-harness-decisions`). Everything else about
the class lives in the lead's research record,
[landscape](../../offices/lead/research/landscape/decision-models/README.md).

## What rests on measurement

The lead's map of the eleven model choices in the code
([BR-002](../../offices/lead/research/briefs/BR-002-model-catalog-evidence-map/README.md),
2026-09-26): three rest on direct measurement, five on partial evidence, and three on none.

- **The tier ranking itself is estimated:** its speed, power, and cost scores are hand estimates.
- **Unmeasured:** the agents' tiers, and `medium` for code review, skill drafting, and the RAG
  answer.
- **Least measured where it matters most:** `opensource` grades every RAG question and repairs
  the Finglish output (RSK-08).

## How tiers will be chosen

Three mechanisms, "cheap by default, frontier on exception" (ADR-0021):

1. **A measured catalog:** a decider judges every tier's answers on labeled sets, replacing the
   estimated scores.
2. **Routing per request:** atomic questions about the request, mapped to a tier in code.
3. **Verify, then escalate:** the cheap tier answers, a decider checks the answer, and a failure
   goes one tier up.

They are measured at R2, built at D1, and costed at P9-B2.
