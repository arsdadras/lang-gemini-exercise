# What Decision Models Change: Capabilities, Patterns, Limits

[Decision models](README.md) › capabilities. As of **2026-09-27** (rewritten the same day after
a wider source sweep). Labels: [V] verified here, [S] primary source, [T] third-party, [C]
vendor or partner claim. Unlabeled analysis is the research office's own. Who builds what:
[ecosystem.md](ecosystem.md). What it means for this repo:
[BR-003](../../briefs/BR-003-decision-points/README.md).

## The idea: judgment, unbundled

For three years, most AI systems sent every fuzzy step to one frontier LLM:

- writing;
- extraction;
- ranking;
- routing;
- checking.

A decision model pulls one capability out of that bundle, **judgment**. It reads a state and
answers typed questions (pick one, how likely, how much) with probabilities, and it never writes
text.

- LangChain calls the result "prod, not god". A frontier model is expensive and slow, and "you
  pay for that generality on every call, even when all you needed was a yes or no" **[S]**.
- Jaya Gupta calls the next phase "cheap by default, frontier on exception" **[T]**. As quoted by
  LangChain, that means a decision model makes the bounded calls it's sure about and hands the
  rest to an LLM.
- **What this changes: a judgment becomes a primitive,** like a function call. At about
  $0.00002 and half a second here **[V]**, you can put one at every step instead of rationing
  it.

## What is new, and what isn't

| Idea | Earlier form | What changed in 2026 |
| :--- | :--- | :--- |
| Classification without generation | NLI zero-shot classifiers (Yin, Hay, and Roth, 2019); cross-encoder rerankers; guard models such as Llama Guard (2023) | One instruction-following model answers any typed question over any state, zero-shot |
| Cascades and routing | Viola and Jones (2001); [FrugalGPT](https://arxiv.org/abs/2305.05176) (2023); [RouteLLM](https://arxiv.org/abs/2406.18665) (2025) | The cheap stage is general, returns probabilities by default, and is priced on input only |
| Thresholds and abstention | Selective classification (Geifman and El-Yaniv, 2017); calibration (Guo et al., 2017) | Probabilities on every answer, and a trained "admit uncertainty" objective (RLCD) **[C]** |
| Workflows with narrow AI steps | Anthropic's "workflows vs agents"; LangGraph's code-owned control flow | The AI step at a branch is now fast and cheap enough to sit at every branch |

The ideas have precursors; the change is economic and ergonomic. That is why the ecosystem grew
to 551 cataloged builds in twelve days **[V]**.

## Three loops it changes

**1. The product loop: agents inside software.**

- **Around the model.** An agent loop makes dozens of small decisions around each model call:
  - which model or specialist takes the turn;
  - which skills, rules, or memories to load;
  - which tool to call, and whether that call may run;
  - which tool results to keep;
  - when to compact;
  - whether the task is really done.
- **Offloading them.** Today each small decision is another LLM call or a hand-written rule. A
  decider takes the bounded ones, and the LLM keeps the writing and the open reasoning. Half the
  cataloged builds that use Jev do exactly this **[V]**.
- **Graphs.** In graph frameworks like LangGraph, every conditional edge is a decision point.
  LangChain's example is a litigation review graph: three questions per page decide the route,
  to set aside, to LLM redaction, or to a human interrupt. Jev was 5-6x faster than the LLMs
  tried on the classification step **[S][C]**.

**2. The development loop: coding agents building software.**

Coding agents fail in known ways:

- claiming "done" without running checks;
- breaking project rules no linter can express;
- wandering out of scope;
- loading the wrong context.

Hooks that ask a decider at those moments are the densest cluster in the ecosystem: one build in
four serves coding agents **[V]**.

- A Stop hook that checks for evidence behind "done" reported **AUROC 0.976**. Judging the
  wording alone reached 0.777 **[T]**.
- A rule checker replaying 93 real sessions against their own `AGENTS.md` reported a finding
  that matters for honesty: **10 of 39** flagged edits were confirmed **[T]**. The gates work,
  but only as escalations, never as verdicts.

**3. The learning loop: people learning a craft.** Cheap, consistent, typed judgments allow:

- formative feedback on every attempt, with the misconception named;
- item analysis across a cohort;
- noticing when a learner is stuck;
- training calibration itself, where the learner answers with a probability.

A decider can't write explanations, so it decides *which* feedback or hint applies, and an LLM or
a template words it. Summative grades stay human **[T]**.

## Where the decisions sit

**TypeSafe's ten decision shapes** **[S]**:

- classification;
- detection;
- scoring;
- routing;
- search;
- retrieval;
- ranking;
- verification;
- ML feature extraction;
- structured data extraction.

**Harness decision points,** in the order an agent loop meets them:

| When | Decision | Shape | Evidence |
| :--- | :--- | :--- | :--- |
| Before a turn | Which model, effort, specialist, or subagent | Routing | Our routing spike: 32/32 × 3, better abstention than two LLM tiers **[V]**; MetaTool abstention 87.0% vs 50.4% **[T]** |
| Before a turn | Which skills, rules, memories, or documents to load | Retrieval, ranking | Skill suggestion: wrong loads 16.8% → 7.3% **[C]**; jev-rules; FyleContext **[T]** |
| During | Which tool or UI action next, from a finite menu | Classification over candidates | Stagehand 1.97 → 0.46 s **[T]**; MetaTool 77.8% vs 69.1% **[T]** |
| During | May this call run: allow, ask a person, or block | Verification, detection | OpenRouter gate cookbook **[S]**; Vercel's fx safety reviewer **[T]** |
| During | Which tool results or turns stay in context | Scoring | fast-jev-compaction; LiteLLM's tool-result guardrail **[T]** |
| After | Is the task really done; do claims have evidence | Verification | jev-belay AUROC 0.976 **[T]** |
| After | Does the output follow the rules or the spec | Verification | Our lint spike: AUROC 1.0 on synthetic snippets, weak on syntax-only rules **[V]**; Abide 10/39 **[T]** |
| Around | Is a remembered fact stale; is it worth recalling | Detection | Our staleness spike: 59/60, thin margins on implied changes **[V]**; invalidate **[T]** |
| Around | Evals on saved traces, and the same checks live | Scoring, verification | LangSmith, Langfuse (91.5% agreement with Claude) **[C][T]** |

## Capabilities, with the evidence

| Capability | What it gives a program | Evidence |
| :--- | :--- | :--- |
| **Typed answers by construction** | No parsing, no malformed output, no invented label | **[S]**; a local 2B LLM failed our JSON schema **[V]** |
| **A probability per answer** | Thresholds, review bands, ranking by risk | Useful ranking: our plain variant **[V]**, TweetTopic bands **[C]**, a 0.99 band at 100% accuracy covering 60% of traffic **[T]** |
| **Many questions per request** | Fan-out over one state for almost the price of one | 200 questions matched single-question accuracy at nearly flat latency **[T]**; batching was 12.2x cheaper and 10x faster **[C]** |
| **Consistency** | Stable decisions, reproducible evals | Per-question standard deviation 0.0102 over 15 repeats **[C]**; 92-913x lower variance than LLM judges **[C]**; our runs: 0-3 label flips in hundreds of decisions **[V]** |
| **Abstention** | "None of these" as a real answer | MetaTool abstention 87.0% vs 50.4% **[T]**; vague requests routed to "clarify" where LLMs weren't **[V]** |
| **Latency** | Inline use, even real time | 92-276 ms hosted **[T]**; 440-480 ms end to end from here **[V]**; games at about 10 decisions a second **[T]** |
| **Cost** | Judgment on all traffic, not samples | $0.042 per million input tokens, output free **[S][V]**; $160 per million verdicts vs $33,000 for Claude Fable 5.1 **[T]** |

## Patterns

**From TypeSafe** **[S]**:

| Pattern | Shape | Reported result |
| :--- | :--- | :--- |
| Speculative fan-out | Ask every question the flow might need in one call; code ignores what doesn't apply | n/a |
| Confidence-gated routing | Confidence as a second axis, with thresholds that scale with risk | n/a |
| Composite scoring | Atomic scores combined with weights in code | n/a |
| Intent routing | Classify, then route to code, a specialist LLM, or a person | n/a |
| Skill suggestion (cookbook) | Rank 182 skills, re-check the top 3, suggest at most one | Wrong loads 16.8% → 7.3% **[C]** |
| Reranking (cookbook) | BM25 shortlist, then one question per candidate | Top-1 5% → 18%, top-10 38% → 62% on CLERC **[C]** |
| Citation check, classifying RAG passages, guardrails, SDE cascade, pre-parsed extraction, hierarchical classification, feature discovery (cookbooks) | As named | See the cookbooks |

**From OpenRouter and the ecosystem:**

| Pattern | Shape | Reported result |
| :--- | :--- | :--- |
| Draft, verify, escalate | A cheap LLM drafts, the decider checks support, a frontier model handles failures | 0 wrong at 7% of the cost **[C]** |
| Menu-constrained action | Code lists the candidates, the decider picks one, and low confidence falls back to an LLM | 4.3x faster browser actions **[T]** |
| Escalate, never approve | Gates that can stop a coding agent and ask a person, but never grant anything | jev-gates **[T]** |
| Done gate | Verify evidence before accepting "done" | AUROC 0.976 **[T]** |
| Rule selection | Load only the rules that apply to this prompt | jev-rules **[T]** |
| Verbatim compaction | Drop or keep whole tool results instead of summarizing | fast-jev-compaction **[T]** |
| Memory leases | A remembered fact expires when new evidence ends it | invalidate **[T]** |
| Evals that are guardrails | The same typed checks run offline on traces and live at runtime | jevals **[T]** |
| Decision cache | Key on (model, schema, state) for cheap repeats and deterministic replay | jevcache **[T]** |
| Compile, then run | An LLM writes the questions once; the decider runs them per row | Jev Lab **[S]** |

## Jev engineering: the skill it demands

A community guide names the craft "Jev engineering" **[T]**: turning a task into closed,
operational questions a decision model answers consistently. Its five principles:

1. **Operational questions only.** "Could a new hire answer this consistently on day one?"
2. **Decompose ruthlessly:** one judgment per question.
3. **Close the answer set honestly,** with an "unclear" option. Otherwise the model launders
   uncertainty into your categories.
4. **Legislate the edges inside the question:** "cosmetic damage counts; disliking the color does
   not".
5. **Calibrate, then version.** Measure against 50-100 known cases, and treat any rewording as an
   API change.

**The evidence that it matters:**

- **Decomposition.** On one phishing task, one broad question scored 62.6%. Five atomic
  questions combined by a fitted logistic regression scored 95.0%, matching Haiku (93.2%) at
  12-27x lower cost **[T]**.
- **Wording.** On our own cases, wording alone moved answers in both directions **[V]**.
- **A pre-registered prompting guide** (thirteen rules from 123,805 requests) exists **[T]**.

This is a distinct engineering skill: decomposing judgment and measuring it. It isn't prompt
engineering, and it's teachable.

## Potential

None of this is shown at scale yet; it follows from the capabilities above.

- **Every harness decision measured and swappable.** Routing, gating, context, and verification
  become typed components with labeled sets, instead of prompt text inside one agent.
- **Development discipline enforced cheaply.** "Done means verified", scope, conventions, and
  commit honesty become checks that escalate. That is today's human review, moved earlier and
  run on every turn.
- **Evaluation on all traffic.** The same questions serve as the eval suite, the online monitor,
  and the guardrail.
- **Memory that forgets correctly.** Facts carry leases, and new evidence retires them.
- **Policy as tested code.** A prose policy compiles into questions with a labeled test set.
- **Learning environments that respond to every attempt.** Formative feedback, stuck detection,
  and calibration training all become affordable.
- **Semantic features for classical models.** Probabilities become columns for ordinary ML;
  autoresearch loops find the questions that predict **[S]**.

## Limits

- **Reasoning and generation:** none. Implied conditions and multi-hop questions are weak **[S]**;
  our implicit staleness cases were right but unsure **[V]**.
- **Off-distribution calibration fails.** On 3-SAT it said "satisfiable" almost always, and on
  unknowable questions it was right 44.7% of the time at a mean probability of 0.74 **[T]**.
  Fit thresholds per question on your own labels.
- **Framing and position.** Performance depends on exact framing **[T]**. Unnamed items in a batch
  decayed from 1.000 to 0.150 accuracy **[T]**. Name every item a question is about.
- **Injection.** Direct injection failed on 199/200 tickets, but **authority-claiming text
  succeeded on 147/200** **[T]**. Never let it be the only security gate.
- **Languages.** Spanish cost 3-6 points and doubled ECE on harder tasks **[T]**. Persian and
  Finglish are untested beyond our small sets **[V]**; expect a gap.
- **Syntax is code's job.** Rules a parser can decide were our lint spike's weak spots **[V]**.
- **Gate precision on real work** can be low (10 of 39 edits confirmed) **[T]**. Gates escalate;
  people or LLMs decide.
- **Concentration:**
  - closed weights, one provider;
  - aliases that move;
  - an alpha LangChain client;
  - data leaving your infrastructure, as with any hosted model **[S]**.
- **Evidence is thin:** 6.7% of cataloged builds measure quality **[V]**.

## Separating hype from substance

- **Durable:**
  - judgment as a cheap, typed primitive;
  - code-owned control flow with decisions at the branches;
  - cascades, and gates that escalate;
  - decomposition, and measurement against labeled sets;
  - a backend-neutral protocol, already served by TypeSafe, OpenRouter, `laya-serve`, and a
    llama.cpp adapter.
- **Perishable:** any one model's scores and prices, and any one vendor.
- **Is it a gamechanger?**
  - **For how agent harnesses, development workflows, and learning loops are designed: yes.** It
    changes which designs are affordable.
  - **For replacing LLMs: no.** The best builds cascade to an LLM or a person.
