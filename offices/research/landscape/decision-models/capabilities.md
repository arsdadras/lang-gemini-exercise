# What Decision Models Change: Capabilities Today and Potential

[Decision models](README.md) › capabilities. As of **2026-09-27**. Labels: [V] verified here,
[S] primary source, [T] third-party, [C] vendor or partner claim. Unlabeled analysis is the
research office's own. What this means for this repo is in
[BR-003](../../briefs/BR-003-decision-points/README.md).

## The idea

A decision model is a building block beside the LLM and the embedding model. It reads a
**state** and answers **typed questions** about it: pick one option, say how likely a
statement is, or place the state on an ordered scale. It never writes text. In practice it's an
`if` whose condition is a judgment about unstructured data, and it costs about $0.00002 and a
few hundred milliseconds ([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md))
**[V]**.

## What is new, and what isn't

Each part of the idea has a precursor:

| Idea | Earlier form | What changed in 2026 |
| :--- | :--- | :--- |
| Zero-shot classification without generation | NLI-based zero-shot classifiers (Yin, Hay, and Roth, EMNLP 2019); cross-encoder rerankers | One instruction-following model answers arbitrary questions over arbitrary state (text, JSON, conversations) |
| Safety classification | Guard models such as Llama Guard (Inan et al., 2023), each with a fixed taxonomy | Any question you can write, not one taxonomy |
| Cascades | Viola and Jones's boosted cascade (2001) in vision; [FrugalGPT](https://arxiv.org/abs/2305.05176) (Chen, Zaharia, and Zou, 2023) for LLMs | The cheap stage returns probabilities by default and is priced per input token only |
| Routing between models | [RouteLLM](https://arxiv.org/abs/2406.18665) (Ong et al., ICLR 2025) | A general decider sold as a router: Jev Router on OpenRouter, listed 2026-09-25 **[S]** |
| Thresholds and abstention | Selective classification (Geifman and El-Yaniv, NeurIPS 2017); calibration and temperature scaling (Guo et al., ICML 2017) | A probability on every answer, and a ready-made "confidence" for `choice` and `score` |

The name comes from Kahneman's System 1, the fast and intuitive mode (*Thinking, Fast and Slow*,
2011).

So the idea isn't new. The packaging is:

- one general model for arbitrary decisions, zero-shot;
- typed primitives with probabilities;
- many independent questions over one state in one call, with latency flat up to 255 options
  **[S][T]**;
- input-only pricing;
- an ecosystem around it:
  - a wire protocol, `/v1/systemone`, served by TypeSafe, OpenRouter, and `laya-serve`
    **[V]**;
  - a LangChain client;
  - access through a general gateway.

## The architecture it makes cheap

TypeSafe describes three ways to build software with AI **[S]**:

1. **Traditional code:** a decision tree built from reliable primitives.
2. **Agents:** the model picks its own next step, so "every loop introduces another opportunity
   to go off the rails".
3. **AI-powered software:** code owns the control flow, side effects, and deterministic rules.
   The model appears only where the system needs programmable common sense, and each AI task is
   atomic and constrained.

Decision models are built for the third. One way to see what they add is to split the AI in a
system into two planes:

| Plane | Its jobs | What the jobs need | Served today by | Could be served by |
| :--- | :--- | :--- | :--- | :--- |
| **Control** | Route, gate, grade, verify, escalate, stop | Fast, cheap, typed, thresholdable, auditable, measurable | LLM structured output: slow, costly, with no native probabilities | A decision model, escalating to an LLM or a person when unsure |
| **Data** | Write, summarize, plan, explain, open-ended extraction | Generation | LLMs | LLMs |

An LLM can do both jobs, but the control plane then inherits generation's latency, cost, and
parsing risk. A cheap decider makes a separate control plane affordable at every step.

**LLM as compiler, decision model as runtime.** OpenRouter's "Prompt to questions" lab has an LLM
rewrite a prose classification prompt into typed questions once. The decider then answers them
for every row **[S]**. The questions become an artifact you can version and test against
labeled data, like code.

## Capabilities today

| Capability | What it gives a program | Evidence |
| :--- | :--- | :--- |
| **Typed answers by construction** | No parse step and no malformed output; the label is always one you defined | **[S]**. The contrast: a local 2B LLM failed our JSON schema ([EV-2026-09-23-local-ollama-qwen](../../evidence/EV-2026-09-23-local-ollama-qwen/README.md)) **[V]** |
| **A probability on every answer** | Thresholds, abstention, review bands, and ranking by risk | **[S]**. Bands on TweetTopic: 114/122 right at confidence ≥ 0.8, 9/18 at 0.5-0.8, 4/10 below 0.5 **[C]**. On our cases, the plain variant's one error sat below most correct answers **[V]** |
| **Many independent questions per request** | Fan-out over one state: tags, checks, or one question per item | **[S]**. Six relevance checks in one request, ~0.45 s in all **[V]** |
| **Low latency** | Inline use in request paths and interfaces | 92-276 ms p50 hosted **[T]**; 475 ms end to end from this machine **[V]** |
| **Low cost** | A decision at every step | $0.042 per million input tokens, output free **[S][V]**. About $0.00002 per decision on our cases **[V]**; $0.07 per 1,000 on Banking77 **[T]** |
| **Accuracy near LLMs on narrow checks** | Can replace or pre-screen an LLM judge where a narrow check is enough | 22/23 against `glm-5.3`'s 23/23 on our cases **[V]**. Below LLMs on hard many-class tasks: Banking77 76.3% vs 80.4% **[T]** |
| **Easy access** | One gateway key, two API surfaces, a LangChain client | **[S][V]** ([Jev](jev.md#access-through-openrouter)) |

## Patterns in use

Recipes published by TypeSafe and OpenRouter, each with runnable code. OpenRouter distributes
Jev, so its results count as partner claims.

| Pattern | Shape | Source | Reported result |
| :--- | :--- | :--- | :--- |
| **Decomposition** | Replace one broad question ("is this spam?") with atomic checks, and combine them in code. TypeSafe calls this "probably the most important concept" | TypeSafe, *How to build with System One* **[S]** | Every check becomes inspectable, tunable, and a named reason |
| **Thresholds that scale with risk** | A floor for "unsure", and a higher bar for costly actions: in a banking example, 0.6 to read a balance and above 0.85 to approve a transfer | TypeSafe, *Confidence-gated routing* **[S]** | n/a |
| **Three-way gate** | Deterministic checks first, then named `noul`s: all ≥ 0.9 → approve, any ≤ 0.1 → block, anything else → a person. Errors fail closed | OpenRouter cookbook, *Gate agent tool calls* **[S]** | Under $0.0001 per call **[C]** |
| **Auto-approving agent permission prompts** | A static risk list in code is the security boundary. Jev clears only commands it rates ≥ 0.9 on "reversible" and "serves the task"; everything else still prompts | OpenRouter cookbook, *Auto-approve coding agent permission prompts* (Claude Code, Codex, Cursor, OpenCode) **[S]** | $0.0000168 per check **[C]** |
| **Draft, verify, escalate** | A cheap LLM drafts from retrieved context, Jev labels the draft supported, unsupported, or declined, and only failures go to a frontier model or a person | OpenRouter cookbook, *Jev-verified cascade* **[S]** | 50 questions: 0 wrong for $0.012, against 2 wrong for $0.175 with the frontier model alone **[C]** |
| **Extraction without guessing** | Code finds candidates (regular expressions); a `choice` picks among them plus "none", so no value can be invented | Jev Lab, *Extract* **[S]** | n/a |
| **Batch labeling** | One `choice` per exclusive category and one `noul` per tag; per-tag thresholds fitted on 100-200 labeled items | OpenRouter cookbook, *Classify and tag text at scale* **[S]** | TweetTopic: 350/400 correct, $0.0256 per 1,000 items **[C]** |
| **Compile, then run** | An LLM writes the typed questions; the decider runs them per row | Jev Lab, *Prompt to questions* **[S]** | n/a |
| **Model routing** | Pick the model and reasoning effort per request | Jev Router on OpenRouter **[S]**; a routing benchmark by LiteLLM **[T]** | 95% vs 74% for Haiku, against the authors' own labels **[T]** |

## Potential

These follow from the capabilities above; none has been shown at scale.

- **Soft predicates in ordinary code.** Judgments over free text replace brittle regular
  expressions and heuristics:
  - log and CI-failure triage;
  - labels on pull requests and issues;
  - validating free-text input;
  - deduplication and entity matching as a choice among candidates.
- **Evaluation on all traffic, not samples.** Groundedness, relevance, and policy checks run as
  always-on telemetry. Drift shows up in the probability distributions before it shows up in
  complaints.
- **Active learning.** Low-confidence items go to people, and their labels fit thresholds or
  small classifiers.
- **Policy as tested code.** A prose policy becomes typed questions with a labeled test set, so a
  policy change is a reviewable diff with a measured effect.
- **Oversight of autonomous agents at every step.** Every step is checked, not samples, and
  people see only the ambiguous band.
- **Control-plane services in a platform.** Routing, gating, and grading run as shared services
  with one telemetry stream.
- **Private, local deciders** for data that can't leave. The encoder class (Laya) runs on CPU
  today; it doesn't yet reach the accuracy
  ([EV-2026-09-26-laya-all-checkpoints](../../evidence/EV-2026-09-26-laya-all-checkpoints/README.md))
  **[V]**.
- **Semantic checks over documentation.** Embeddings find candidate pairs; a `noul` asks "does A
  restate B?".

## Limits

- **Hard tasks.** Accuracy falls on many-class tasks and on sealed test sets: Banking77 76.3%,
  and about 35% on JevBench's sealed tier **[T]**.
- **Documented failure modes [S]:**
  - literal reading of negations;
  - numbers, dates, and multi-hop questions;
  - irrelevant context;
  - adversarial content in the state;
  - conflicting instructions;
  - broken structural invariants.

  Details: [Jev](jev.md#where-it-breaks-by-its-own-account).
- **Calibration is disputed.**
  - The one independent study found the worst ECE among its contenders, 0.246 **[T]**.
  - A partner's run and our small run found confidence that separates errors **[C][V]**.
  - The two can both hold. A threshold needs *discrimination*, meaning confidence ranks errors
    below correct answers, more than it needs a low ECE. Either way, fit thresholds per question
    on labeled data.
- **Not fully deterministic.** Probabilities "differ slightly from run to run" **[S]**, by up to
  0.12 on our cases **[V]**. Leave a margin around thresholds, and never assert exact
  probabilities in tests.
- **Sensitive to wording.** On our cases, wording alone moved one answer from barely right to
  confidently right, and another to confidently wrong **[V]**.
- **Size limits:** 32k tokens of context through OpenRouter (64k at TypeSafe), and 255 options
  per `choice` **[S][V]**.
- **English first.** Other languages work "not equally well" **[S]**. Our three Finglish cases
  passed **[V]**, which proves little.
- **No explanations.** Any reason comes from named checks or from an LLM **[S]**.
- **Concentration:**
  - closed weights, served by one provider behind OpenRouter;
  - aliases that move to new versions;
  - an alpha LangChain client.

  All **[S]**.
- **Data leaves your infrastructure.** Zero retention is offered to enterprise customers only
  **[S]**. The same is true of any hosted LLM.
- **Commoditization.** The idea has precursors, and the price floor of the layer trends to zero
  **[T]**.

## Separating hype from substance

**Durable**, and it will outlive any vendor:

- decision points as typed, thresholded, measured components;
- cascades, and gates with a review band;
- control flow owned by code;
- decomposition into atomic questions;
- a backend-neutral protocol.

**Perishable:** one model's accuracy, price, and latency, and any single vendor.

**Is it a gamechanger?**

- **For how AI systems are designed: largely yes.** It makes a separate control plane cheap
  enough to put at every step.
- **For replacing LLM judges wholesale: no.** The accuracy gap on hard tasks and the calibration
  dispute both point to cascading, not replacing.

Sources: [sources.md](sources.md).
