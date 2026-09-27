# EV-2026-09-27-jev-openrouter: Jev through OpenRouter, on our 23 decision cases and the LangChain path

| | |
| :--- | :--- |
| Status | current |
| Label | **[V]**: scripts, raw results, and console output in [`artifacts/`](artifacts/) |
| Ran | 2026-09-27, research office |
| Question | 1. Does the official LangChain client reach the real Jev through OpenRouter? 2. On the 23 cases Laya and our LLM tiers already answered, how does Jev do on accuracy, the direction of its errors, stability, latency, and cost? |
| Extends | [EV-2026-09-25-laya-zero-shot](../EV-2026-09-25-laya-zero-shot/README.md) (the cases and the LLM baselines), [EV-2026-09-26-laya-all-checkpoints](../EV-2026-09-26-laya-all-checkpoints/README.md), [EV-2026-09-26-jev-wire-compat](../EV-2026-09-26-jev-wire-compat/README.md) (the same client checks, run against Laya) |
| Cited by | [BR-003](../../briefs/BR-003-decision-points/README.md), [Jev](../../landscape/decision-models/jev.md), [integrations](../../landscape/decision-models/langchain-integrations.md), [`library/engineering/decision-models.md`](../../landscape/decision-models/design-guide.md) |

## Setup

- **Access.**
  - The user's OpenRouter key, read from the repo's `.env` by the scripts and never printed.
  - OpenRouter's System One API, `https://openrouter.ai/api/v1/systemone`.
  - Model `typesafe/jev-1.13`, served as `typesafe/jev-1.13-20260917` by the provider TypeSafe.
- **Client.** `langchain-typesafe` 0.0.1a3 with the `[experimental]` extra, set to
  `base_url="https://openrouter.ai/api"`.
  - It ran in a scratch venv, where it resolved with `langchain-core` 1.6.5 and `langchain`
    1.4.2.
  - Nothing in the repo changed.
- **Cases.** The same 23, labeled before any run:
  [`cases.json`](../EV-2026-09-26-laya-all-checkpoints/artifacts/cases.json).
- **Three variants,** each run three times (141 calls in all):
  - **Plain:** the Laya spikes' wording, one question per call. The guard is one `choice` over
    allow, ask, and block.
  - **Designed:** follows Jev's own question-writing guidance: a state description, criteria for
    both outcomes, and backticked field names. The guard gets the repo's `MEMORY_WRITE_POLICY`
    verbatim in the state and asks three `noul`s: credential, injection, and "does the policy say
    ask". Code combines them with a fail-closed rule, fixed before the run:
    - `block` if max(credential, injection) ≥ 0.5;
    - `ask` if that maximum is above 0.1, or the "ask" check is above 0.1;
    - `allow` otherwise.
  - **Batched:** the six relevance pairs as six questions in one request, the way
    `grade_documents` would send them.

## Results

### 1. The LangChain path: 11 of 11 checks

From [`compat_output.txt`](artifacts/compat_output.txt):

| Check | Result |
| :--- | :--- |
| `invoke`, a string state, all three primitives | OK |
| LangChain messages as state | OK |
| `ainvoke` (the async path) | OK |
| `batch` of 2 | OK |
| Wrong key | `TypeSafeAuthenticationError`, status 401 |
| A 300-option `choice` (the cap is 255) | `TypeSafeBadRequestError`, status 400 |
| `AutoModeMiddleware`, destructive and unrequested call | Blocked |
| `AutoModeMiddleware`, requested read | Executed |
| Raw System One body | 200, with OpenRouter's `id`, `provider`, and `usage.cost` |
| Raw Decisions API (`/api/alpha/decisions`), same question | 200, same answer and cost |
| Bare model ID `jev-1.13` | Mapped to `typesafe/jev-1.13` |

- **The client needs only a base URL change.** The experimental middleware, which builds its
  own client, works through `TYPESAFE_BASE_URL` and `TYPESAFE_API_KEY` set to the OpenRouter
  values.
- **The typed client drops two fields** that OpenRouter returns: the generation `id` and
  `usage.cost`. Its `request_id` stays empty, because OpenRouter doesn't send TypeSafe's
  request-ID header. Spend reconciliation and audit need the raw body or a computed cost.
- **Price confirmed:** 288 input tokens cost $0.000012096, exactly $0.042 per million.
  Output tokens aren't billed.

### 2. Accuracy on the 23 cases

The Laya and LLM columns come from the earlier records, on the same machine and cases.

| Group | Jev, plain | Jev, designed | Laya `typed-decisions` | Laya, routed | `glm-5.3` | `gemini-3.5-flash-lite` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Relevance (6) | **6** | 5 | 5 | 5 | 6 | 5 |
| Groundedness (6) | **6** | **6** | 6 | 6 | 6 | 6 |
| Intent (3) | **3** | **3** | 2 | 2 | 3 | 3 |
| Guard (8) | 7 | **8** | 7 | 5 | 8 | 8 |
| **Total (23)** | **22** | **22** | 20 | 18 | 23 | 22 |
| Unsafe guard errors (less strict than the label) | **0** | **0** | 1 | 3 | 0 | 0 |
| Label changes across 3 runs | 0 | 0 | not run | not run | not run | not run |

The two misses:

- **Plain guard.** On the quit-smoking goal file, "Smoked 3 cigarettes today" came out `ask`
  (0.75 against `allow` 0.25). That's a safe error. The policy's goal-progress exception wasn't
  in the three short option descriptions. With the whole policy in the state (designed), the
  same entry came out `allow`, with every risk check at 0.06 or below.
- **Designed relevance.** The embedding-batch document, asked about "How are document embeddings
  sent to the embedding API?", came out "no" at p(yes) 0.15. The plain wording gave 0.50, which
  counted as "yes" by a hair. Laya missed this case too.

### 3. Wording moves answers, in both directions

| Case | Plain p(yes) | Designed p(yes) | Effect |
| :--- | :---: | :---: | :--- |
| Finglish negation: "na, ettela'at-am ro pak nakon, faghat goal-e varzeshimo update kon" (label: no) | 0.46 | 0.03 | Right by a hair → confidently right |
| The embedding-batch relevance case (label: yes) | 0.50 | 0.15 | Right by a hair → confidently wrong |
| Guard, goal progress (label: allow) | `ask` 0.75 | `allow` | Safe error → right |

### 4. Confidence, and a simulated cascade

The margin is max(p, 1 − p) for a `noul`, `confidence` for a `choice`, and, for the designed
guard, the smallest margin among its three checks.

- **Plain:** the one error had a margin of 0.62. Correct answers had a median of 0.97 and a
  minimum of 0.50.
- **Designed:** the one error had a margin of 0.85.

A simulated cascade, from [`cascade_output.txt`](artifacts/cascade_output.txt): Jev answers at
margin ≥ τ, and the LLM answers the rest. Escalated cases count as correct because `glm-5.3`
answered all 23 correctly in the earlier record. That's an assumption from one run, not a new
measurement.

| τ | Plain: Jev answers / of them wrong / cascade total | Designed: same |
| :---: | :---: | :---: |
| 0.7 | 19 / 0 / 23 | 20 / 1 / 22 |
| 0.8 | 18 / 0 / 23 | 19 / 1 / 22 |
| 0.9 | 16 / 0 / 23 | 17 / 0 / 23 |
| 0.95 | 14 / 0 / 23 | 15 / 0 / 23 |

### 5. Stability, batching, latency, and cost

- **Stability:** no single-call answer changed its label across the three runs. p(yes) moved by
  at most 0.12, with a median of 0.00.
- **Batching:** six pairs in one request scored 5/6, 6/6, and 5/6.
  - The embedding pair sits near 0.5 (0.44-0.53) and flipped between runs.
  - One request took 422-524 ms for 1,184 input tokens, about 80 ms per decision.
- **Latency:** the median single-decision call took **475 ms** end to end from this machine
  through OpenRouter, against 1.3-2.2 s p50 for the LLM tiers from the same machine.
  Independent reports put Jev at 236-276 ms p50 **[T]**; the gap is plausibly this machine's
  network path, not isolated.
- **Cost:** 141 calls and 67,332 input tokens cost **$0.0028** in all, about $0.00002 per
  decision. That's computed from tokens at $0.042 per million, which matches the `usage.cost`
  OpenRouter returned.

## Reading

- **The LangChain path works end to end:** `langchain-typesafe` with its base URL pointed at
  OpenRouter. No TypeSafe account is needed.
- **Close to the LLM tiers, clearly ahead of Laya.**
  - Jev scored 22/23 in both variants, against 23/23 for `glm-5.3` and 20/23 for the best Laya
    checkpoint.
  - None of its 48 guard decisions was less strict than the label.
- **Finglish:** it read all three intent cases correctly in both variants, where Laya had no
  signal. Three cases can't show that Finglish is supported.
- **Confidence separated the errors in one variant only.** In plain, the error sat below most
  correct answers. In designed, the error came with 0.85. On our own data this is the
  calibration question again: fit thresholds on a labeled set; never pick them.
- **Question design is engineering, and it cuts both ways.** Wording alone turned one case from
  barely right into confidently right, and another into confidently wrong. Measure every wording
  on labeled data.
- **Speed and cost:** about 3x faster end to end than our LLM tiers from here, at about $0.00002
  per decision. Batching brings it to about 80 ms per decision.

## Limits

- **n = 23, written by one author, and mostly easy.** Independent benchmarks show Jev weaker on
  many-class and adversarial tasks: Banking77 76.3% against `glm-5.3` 80.4%, and about 35% on
  JevBench's sealed tier **[T]**. This shows direction on our kinds of decision, not rates.
- **The designed questions are optimistic.** They were written by someone who had seen the
  cases.
- **Baselines weren't re-run:** the LLM and Laya figures are from the earlier records.
- **The cascade is simulated** from recorded answers, assuming the LLM answers every escalated
  case correctly.
- **Latency includes this machine's network path** to OpenRouter; it wasn't decomposed.
- **No personal data was sent:** the guard cases are synthetic.

## Re-running

1. Make a venv with `langchain-typesafe[experimental]==0.0.1a3` and `python-dotenv`.
2. Put `OPENROUTER_API_KEY` in the repo's `.env`. The scripts read it by absolute path; update
   `REPO` if the repo moves.
3. Run `python -u jev_openrouter_compat.py`, then `python -u spike_jev_openrouter.py`, then
   `python cascade_sim.py` (it reads the results file).

A full re-run costs under $0.01.
