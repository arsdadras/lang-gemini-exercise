# Jev (TypeSafe AI)

[Decision models](README.md) › Jev. As of **2026-09-27**. **Tested in this repo** through
OpenRouter ([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md)).
Labels: [V] verified here, [S] primary source, [T] third-party, [C] vendor or partner claim.

## At a glance

| | |
| :--- | :--- |
| Maker | TypeSafe AI, San Francisco, founded 2024. CEO Diogo Almeida, previously OpenAI (RLHF, InstructGPT, GPT-4); co-founders Erik Gafni and Sasha Sheng **[T]** |
| Launch | 2026-09-15 in early access, with a $40M seed round led by DCVC (valuation reported near $200M). Open sign-up since 2026-09-21, with $5 of starting credit **[T]** |
| Name | After William Stanley Jevons, of the Jevons paradox **[T]** |
| Model | `jev-1.13.0` at TypeSafe; the aliases `jev-latest` and `jev-preview` both resolve to it **[S]**. On OpenRouter: `typesafe/jev-1.13`, alias `~typesafe/jev-latest`, served as the snapshot `typesafe/jev-1.13-20260917` **[S][V]** |
| Internals | Closed. "A transformer trained on synthetic data with RLCD"; no paper or weights **[T]** |

## Access through OpenRouter

Read from OpenRouter's Jev documentation on 2026-09-27 **[S]**; every item marked **[V]** was
exercised in EV-2026-09-27.

- **No TypeSafe account needed.** An OpenRouter key authenticates, and usage is billed to the
  OpenRouter account **[S][V]**.
- **Two API surfaces,** same key, same answers **[S][V]**:

  | Surface | Endpoint | Use it with |
  | :--- | :--- | :--- |
  | System One API | `POST https://openrouter.ai/api/v1/systemone` | TypeSafe's SDKs and `langchain-typesafe`, by setting the base URL to `https://openrouter.ai/api` |
  | Decisions API (alpha) | `POST https://openrouter.ai/api/alpha/decisions` | Plain HTTP, or OpenRouter's own SDKs (`openRouter.alpha.decisions.create`) |

- **Model IDs.** Bare TypeSafe IDs are mapped: `jev-1.13` → `typesafe/jev-1.13` **[S][V]**.
  TypeSafe's SDK `models.list()` fails against OpenRouter, because the response shape differs
  **[S]**.
- **Response.** TypeSafe's shape (`model`, `answers`, `usage`), plus OpenRouter's `id`,
  `provider`, and `usage.cost` in USD **[S][V]**.
- **Context:** 32,000 tokens, counting the state and the questions. That's half of TypeSafe's
  own 64k **[S]**.
- **Price:** $0.042 per million input tokens; output is free **[S][V]**.
- **Repeatability.** "Your probabilities will differ slightly from run to run" **[S]**. Here,
  p(yes) moved by up to 0.12 over three runs, and no label changed **[V]**.
- **Rate limits.** A `402` whose `limit_source` is `openrouter_in_flight_budget` is transient:
  retry after `Retry-After`. Any other `402` means credits ran out **[S]**.
- **Around the model** **[S]**:
  - **Jev Lab** (openrouter.ai/labs/jev): six live recipes with their code: triage, agent
    oversight, extraction, prompt-to-questions, feed filtering, and a game.
  - **Five cookbooks:** tool-call gating, a verified cascade, batch classification with
    thresholds, comment classification, and auto-approving coding-agent permission prompts.
  - **Jev Router** (`typesafe/jev-router`, listed 2026-09-25): picks a model and reasoning
    effort per request, running on Jev.

  The patterns are catalogued in [capabilities.md](capabilities.md#patterns-in-use).

## Using the API directly (TypeSafe)

Facts below are **[S]** unless marked. Source: docs.typesafe.ai, read as raw markdown on
2026-09-26.

- **Calls.** `POST https://api.typesafe.ai/v1/systemone` with a bearer key; `GET /v1/models`
  lists the aliases.
- **Request.** A `model`, a `state`, and a map of named `questions`, each with a `type`,
  `instructions`, and `criteria`.
- **Limits.**
  - Context: 64k tokens per request; 32k for the state plus the single longest question.
  - Options per `choice`: up to 255. More returns `400` **[T][V]**.
  - Input: text only (a string, a JSON object, or an array of text values).
- **Rate limits.** 250,000 tokens/s and 1,200 requests/min, "adjusting dynamically" and subject
  to change without notice. Excess returns `429` with `retry-after`.
- **Price.** $0.042 per million input tokens; output is free.
- **Customization.** None per account: no fine-tuning or adapters. You steer it through the
  state, instructions, and criteria only.
- **Languages.** English is where accuracy is best. Others are "handled but not equally well";
  test before relying on them.
- **Data.** Customer requests and responses are not used for training. Zero data retention is
  offered to enterprise customers only; a DPA and privacy policy are published.
- **Versions.** An alias moves on release, and "the answers behind it can change without a
  change on your side". Pin the versioned ID if thresholds are tuned.
- **Clients.** The Python SDK `typesafe_sdk` retries with backoff by default; the JavaScript SDK
  is `@typesafe-ai/sdk`.
- **LangChain.** `langchain-typesafe`, maintained by LangChain; see
  [langchain-integrations.md](langchain-integrations.md#langchain-typesafe).
- **What "confidence" means is stated two ways.**
  - `langchain-typesafe`'s docstring: how concentrated the distribution is, "not the selected
    label's probability" **[S]**.
  - One OpenRouter cookbook: "Jev's probability that the chosen label is correct" **[S]**.

  Threshold on it as a ranking signal fitted to labels, not as a probability.

## Where it breaks, by its own account

TypeSafe keeps a "jaggedness" page for `jev-1.13`, reviewed 2026-09-17 **[S]**. It lists these
failure modes:

1. **Literal reading:** negations and implied conditions are read at face value.
2. **Numbers:** unreliable counting; weak on numeric forms; `score` expectations aren't
   numerically calibrated.
3. **Dates:** comparing them is unreliable; extract the parts and compare in code.
4. **Indirection:** multi-hop questions lose accuracy.
5. **Irrelevant state:** "context rot"; filter before sending.
6. **Adversarial content:** state isn't treated as hostile, and injected instructions "can move
   the answer".
7. **Conflicting instructions and criteria** confuse it.
8. **Structural invariants don't hold.** A `noul` and its negation summed to 1.19; a `noul` and
   the equivalent yes/no `choice` gave 0.22 and 0.01.
9. **Generation:** not trained for it.

## Measurements

**This repo [V]**, 23 of our own decision cases
([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md)):

- 22/23 in both question variants, against 23/23 for `glm-5.3` and 20/23 for the best Laya
  checkpoint.
- None of its 48 guard decisions was less strict than the label, and it read three Finglish
  intent cases correctly.
- No label changed over three runs.
- Median 475 ms end to end from this machine, and about $0.00002 per decision.
- Wording alone moved answers in both directions.

**Vendor claims [C]:**

- 40-200x faster and 40-400x cheaper than comparable LLMs, peaking at 193.6x and 444.6x;
  70-500 ms end to end. TypeSafe calls these the high end.
- About 68% agreement on its own workflow evaluation. Critics note the reference answers there
  come from frontier models, not verified ground truth **[T]**.

**Independent [T]:**

| Study | What was compared | Result |
| :--- | :--- | :--- |
| nibzard, *decision-model-benchmark*, v2 report of record (2026-09-18/19): $28 of paid calls, raw logs published | Jev, 8 constrained LLMs, and deterministic baselines, under a frozen protocol | Banking77, 77-way: Jev **76.3%** vs glm-5.3 80.4%, gpt-oss-120b 81.3%, claude-haiku-4.5 75.7%, gpt-5.4-mini 74.0%. Spam: 93.0% vs glm-5.3 94.9%. Permuted options: 76.7% vs 82.0%. Latency p50 **264-276 ms**, flat from 2 to 255 options (1.2x faster than gpt-oss-120b on Cerebras; 10-16x faster than thinking-mode models). Cost **$0.07 per 1k** vs $0.19 for the cheapest LLM. **Worst ECE (0.246)**. Admitted uncertainty on 49.7% of unanswerable items (LLMs 97.3-100%). Changed 13% of answers when options were reordered (worst LLM: 37%) |
| AbdelStark, *jev-benchmarks*, pilot (2026-09-17): n=100 per condition, bootstrap CIs | Jev vs GLiNER2.5, zero-shot classification | AG News 0.910, Banking77 0.870, DAIR Emotion 0.480. On DAIR Emotion Jev put **zero probability on the true label for 16%** of items. Coverage at ≤5% error: 0.83, 0.86, **0.00**. p50 236-256 ms, called from France |
| LiteLLM (2026-09-18): 80 cases × 3 repeats | Four-tier request routing, Jev vs claude-haiku-4.5 | 95.0% vs 73.75% against labels the authors wrote themselves; p50 127 vs 688 ms; $0.0077 vs $0.1985 for 240 calls. The authors caution: labels not blind-adjudicated, downstream quality unmeasured |
| Context Studios: three measurement waves, 2026-09-19 to 23 | Latency and cost in real workflows | 92-214 ms per decision. **About 25x** faster like for like, not 200x: the vendor's figure compares a full generation pass, including warm-up |
| JevBench, Benchmark Heaven (scored 2026-09-24): 231 public tasks + 308 sealed | Composite of intelligence, calibration, speed, and cost | Jev ranks second among Jev-class systems (63.3, behind "decider-4b v2" at 64.1). Sealed-tier accuracy is about 35%, against 75-99% on the public tiers. *Read through a summarizing fetch* |
| Open-Jev's own audit (2026-09-23) | JevBench public 231 | Jev 200/231, and 81/111 on the Hard tier |

**Partner-published [C]:** OpenRouter's captured runs report 350/400 on TweetTopic, with
confidence bands that separate errors, and a verified cascade with no wrong answers on 50
questions ([capabilities.md](capabilities.md#patterns-in-use)).

**Overall:**

- **Speed and cost:** the fastest and cheapest option measured.
- **Accuracy:** close to our LLM tiers on narrow binary checks, our own included, and mid-pack
  on hard many-class tasks.
- **Calibration:** contested. It was worst in the one independent study, and useful in the
  partner's run and ours.

## Reception

- **Attention [T]:** the Hacker News launch thread reached 1,655 points and 456 comments in a
  day. Forbes reported that Vercel and Cloudflare rushed to add it (headline only; the page
  returned 403). LangChain shipped its integration two days after launch **[S]**.
- **Ecosystem [S]:**
  - OpenRouter serves it with labs, cookbooks, and Jev Router.
  - shipwithjev.com, a community catalog "not affiliated with TypeSafe", lists 551 builds in
    eight categories. The largest are tools and apps (213), agents and browsers (79), and
    research and data (72).
  - A sister directory covers Laya.
- **Criticism [T]:**
  - no published calibration evidence;
  - speed comparisons aren't like for like;
  - "can't hallucinate" overclaims;
  - the idea has academic precursors, and the price floor of this layer trends to zero;
  - the headline accuracy is agreement with frontier models, not ground truth.

## For this repo

What it would mean here, and our position:
[BR-003](../../briefs/BR-003-decision-points/README.md), which supersedes BR-001. In short:

**Strengths:**

- typed answers with probabilities;
- flat latency however many options, and parallel questions;
- the lowest cost per decision;
- near-LLM accuracy on our narrow checks;
- the client already works through the gateway key we have.

**Concerns:**

- It is mid-pack on hard many-class tasks, and its calibration is contested.
- Adversarial content is a known weakness, so it must never be a security gate on its own.
- Finglish is barely tested (3 cases).
- The hosted API sends the state to third parties, as our LLM tiers already do.
- It is twelve days old, and the LangChain client is still alpha.
