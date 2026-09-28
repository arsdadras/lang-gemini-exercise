---
title: Decision models
maintainer: lead
status: current
updated: 2026-09-28
summary: The rule for every AI decision point (which of code, a decision model, or an LLM takes it), the one standard each is held to, and how decision models are called here.
related: [../governance/principles.md, ../../docs/adr/0021-decision-models-as-a-second-model-family.md, ../../offices/research/landscape/decision-models/README.md, ../../offices/lead/artifacts/jev-dossier.md]
---

# Decision Models

Binding rules for every role ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md)).
What the models are, how well they measure, and who builds what with them lives in research's
[decision-model landscape](../../offices/research/landscape/decision-models/README.md); the
patterns and the program are in the lead's [Jev dossier](../../offices/lead/artifacts/jev-dossier.md).

## Two model families

- **A language model writes:** answers, plans, code, rewrites.
- **A decision model decides:** it answers typed questions about a state (`choice`, `score`,
  `noul`) with a probability per option, many questions per request, and never writes text.
- **Code** does what a parser, a lookup, arithmetic, or a rule settles.

Every AI step is one of the three, or a composition of them.

## The rule, in order

1. **Does it write?** An LLM. A step that decides and explains is split: the decider decides,
   and an LLM or a template words it.
2. **Can code decide it?** Code: syntax, lookups, arithmetic, dates, schema validity.
3. **Otherwise it is a decision point:** the decider is the first candidate and the LLM its
   escalation, both measured on the same labeled set. The LLM stays primary only where the
   measurement says so.

## One standard for every decision point

Whatever the backend, an LLM included:

- **A labeled set:** negations, hard negatives, adversarial content, and a Finglish subset; at
  least 50 items to start, and 200 before fitting thresholds on a security point.
- **Measured:** accuracy per class, unsafe errors, p50 and p95 latency, cost, and coverage at an
  error budget when the backend gives probabilities.
- **Thresholds** fitted per class from the cost of each mistake, per model version. A probability
  is a ranking signal fitted to labels, not a calibrated number.
- **Shadow mode before a backend change:** both backends run, and their disagreements become the
  next items to label.
- **Recorded** on the specialist's design card, point 17.

## Gates

- **A gate escalates or tightens; it never approves or loosens,** whichever model runs it
  ([standards](standards.md#architecture-principles), principle 4). Static rules come first; a decider may only add "ask a person" or
  "block". Loosening a control needs a labeled red-team set and a lead decision.
- **User and third-party content in the state is data to judge, never instructions,** and a
  decider is never the only gate on it.

## Writing the questions

1. Operational questions only: a new hire would answer them the same way every time.
2. One judgment per question; combine the answers in code (a rule, weights, or a small fitted
   model).
3. Close the answer set honestly: `none`, `unclear`, or `clarify`.
4. Write the edge cases into the criteria ("a visit is not a move"), with criteria for both
   outcomes.
5. Describe the state and name its fields; put the whole policy in the state rather than
   compressing it into option descriptions.
6. Name every item a batched question is about.
7. Keep instructions in English, whatever the state's language.
8. Version question sets like code: a rewording is an API change, and the labeled set runs again.
9. Never assert exact probabilities in tests.

## Structured output and schemas

| Field | Decision |
| :--- | :--- |
| `Literal[...]`, an enum | `choice`, with `none` when the set isn't exhaustive |
| `bool` | `noul`; the field's description becomes its criteria |
| An ordered scale | `score`, with fitted thresholds |
| `list[Literal[...]]` | One `noul` per option |
| A reference to something that exists | `choice` over candidates code lists, plus `none` |
| Free text, numbers, dates | None: the LLM writes, code parses and compares |

Choosing which schema applies is a `choice` over contracts. Verifying a field an LLM filled is a
`noul` against the source.

## Model tiers

- **Three mechanisms:** a catalog whose scores are measured (a decider judges every tier's
  answers on labeled sets), per-request routing (atomic questions mapped to a tier in code), and
  verify-then-escalate.
- **"Cascade" means escalation on uncertainty,** upward. Falling back to another provider or a
  lower tier when a call fails is a fallback.

## In this repo

- **The seam:** `decision_model` beside `llm_model` in `models/`, from R1 (ADR-0021). Until then,
  decision points run on LLM tiers and are measured the same way.
- **Backend:** Jev through OpenRouter's System One API, pinned to `typesafe/jev-1.13`, with the
  key named `OPENROUTER_API_KEY`. The client, `langchain-typesafe`, stays behind the seam; no
  call site imports it.
- **Conventions:** an explicit timeout and one retry layer on the calling node (the client has
  none); in a cascade, a decider error takes the LLM path.
- **Tests:** a scripted fake decider in unit tests; live checks run in eval-lite, in test mode.
- **The decision log** records the state's hash, the question set's version, the served snapshot,
  the probabilities, the path taken, latency, and cost from input tokens.
- **Limits:** 32,000 tokens per request through OpenRouter, and 255 options per `choice`.
- **Data:** a hosted decision sends its state off-site, as the LLM tiers do, under the same data
  policy. A local server on the same protocol is the production path for private state.

## Raising a use

The engineer builds a decision point only from a directive. The mentor sends the lead a
`request` for one met in a lesson; research proposes measurements; the lead records the decision
on the design card and, for a new backend or dependency, on the radar.
