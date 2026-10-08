---
title: Models at hand
maintainer: mentor
status: current
updated: 2026-10-08
summary: The two model families as this repo runs them: the LLM tiers, fallback, and test mode; the Jev model router; the decision models; which choices rest on measurement; and how tiers will be chosen.
related: [radar.md, ../architecture/decision-models.md, ../../docs/adr/0014-weighted-model-tier-catalog.md, ../../docs/adr/0015-local-tier-and-test-mode-profiles.md, ../../docs/adr/0031-jev-model-router-and-test-mode-ladder.md, ../../mentor/research/briefs/BR-002-model-catalog-evidence-map/README.md]
---

# Models at Hand

The practical picture of the models this repo runs. Model IDs live only in
[`configs/models_config.py`](../../src/agentlab/configs/models_config.py), and secrets are named
by environment variable; neither is copied here. Rings and versions:
[radar.md](radar.md). The rules for decision points:
[decision-models.md](../architecture/decision-models.md).

## Embeddings

The RAG index embeds with `text-embedding-3-small` (1536 dimensions) through OpenRouter
(`openai/text-embedding-3-small`, `OPENROUTER_API_KEY`; `EMBEDDING_SPEC` in
`configs/models_config.py`, live-verified 2026-10-05, with the same call timeout as every external
client). GapGPT served it before (2026-10-03) until its host began resetting connections from the
cloud sessions; it is the same model, so an index built with either stays valid. Gemini's embeddings
were replaced earlier at the user's instruction, so Google serves only the `free` tier. The old
`.chroma_index` still holds Gemini's vectors, a different width, so the RAG graph answers nothing
until the rebuild (R2).

## LLM tiers

| Tier | Served by | Use |
| :--- | :--- | :--- |
| `high`, `medium`, `low` | GapGPT gateway: OpenAI, Anthropic, Gemini | The default tiers; `low` is the default |
| `opensource` | GapGPT: GLM, Qwen, DeepSeek | Low-stakes nodes only, until measured (RSK-08) |
| `free` | Gemini 3.5 Flash-Lite: GapGPT, OpenRouter, then Google directly | Test mode's default, opt-in |
| `strong` | Claude Haiku 5.5, then GPT-6 Luna, each on GapGPT then OpenRouter | Test mode, one rung up, opt-in |
| `strongest` | Gemini 3.8 Flash, Claude Sonnet 5.5, GPT-6.1 Sol, same gateways | Test mode, two rungs up, opt-in |
| `last_resort` | Gemini 3.5 Flash-Lite on Google, then a free OpenRouter model | The end of the Jev router's chain; never asked for |
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
  editing `.env`. `LLM_TEST_PROFILE` picks a rung of a ladder, used one at a time and only when
  the rung below was not enough because of the model: `default` (`free`), `strong`, `strongest`
  (the table above), or `local`
  ([ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md),
  [ADR-0031](../../docs/adr/0031-jev-model-router-and-test-mode-ladder.md)). Above `free` a model
  is called on GapGPT, then OpenRouter, never on Google (its quota is large for Flash-Lite only),
  and when both fail the call fails. Three GapGPT IDs (`claude-haiku-5-5`, `gpt-6-luna`,
  `gpt-6.1-sol`) were registered without a live call; `scripts/smoke_live.py` settles them.
- **The Jev router (outside test mode):** `model_router` picks a tier per task. See below.

## Decision models

Jev, pinned to `jev-1.13.0`, called directly at TypeSafe (key `TYPESAFE_API_KEY`; OpenRouter's System One API is the alternative), behind `decision_model`
from R1 ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md)). Measured
here on 2026-09-27: about 0.45 s and $0.00002 per decision; 22/23 on our grader and guard cases
with no guard answer less strict than its label; routing 32/32 in three runs
(`EV-2026-09-27-jev-openrouter`, `EV-2026-09-27-jev-harness-decisions`). Everything else about
the class lives in the research record,
[landscape](../../mentor/research/landscape/decision-models/README.md).

## The Jev model router

[ADR-0031](../../docs/adr/0031-jev-model-router-and-test-mode-ladder.md). It sits beside
`llm_model` and replaces nothing: `model_router.chain(task, structured=Schema)` for a node,
`model_router.plan(task)` for an agent. One Jev request with two questions, how demanding the
task is (a score over four levels) and whether a mistake would be costly, then code maps the
answers to `low`, `medium`, or `high`: "low" on evidence only, "high" only when earned, stakes
lift a task to "medium" and never to "high", and an outage of Jev routes to "medium". The call
goes to the tier's primary on GapGPT, then its OpenRouter backup, then the `last_resort` tier.
Jev is shown each tier's profile and its models; it judges the task and never picks a model name,
because a decision model has no knowledge of what a named model is good at. Thresholds are
provisional until `evals/model_route_eval.py` has been run on its labeled set. No call site has
moved to it yet.

## What rests on measurement

The map of the eleven model choices in the code
([BR-002](../../mentor/research/briefs/BR-002-model-catalog-evidence-map/README.md),
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
2. **Routing per request:** atomic questions about the request, mapped to a tier in code
   (built as `model_router`, 2026-10-08; unmeasured, no call site yet).
3. **Verify, then escalate:** the cheap tier answers, a decider checks the answer, and a failure
   goes one tier up.

They are measured at R2, built at D1, and costed at P9-B2.
