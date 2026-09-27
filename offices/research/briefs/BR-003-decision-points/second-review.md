# BR-003 › The second review: verdicts and amendments

Supports [BR-003](README.md) **version 3**. Code read on 2026-09-27 at `f261b6e`. Everything
here is a proposal for the lead; the mentor implements whatever the lead accepts.

## What this records

After version 2, the user sent a second critique. It was based on the session's closing
summary, not on the records themselves. A redo it started was stopped and rewound before
anything was committed. The user then handed the critique back as notes.

This file records:

- each point, with the office's verdict under principle 1:
  - agreement where the evidence supports the point;
  - disagreement, with the numbers, where it doesn't;
- why version 2 missed what it missed;
- the amendments (A1 to A10) that version 3 adds.

Where an amendment changes the schedule in [plan.md](plan.md#schedule) or the stages in
[curriculum.md](curriculum.md), this file is the source; those files point here.

## The points and the verdicts

| # | The user's point | Version 2 | Verdict | Amendment |
| :-: | :--- | :--- | :--- | :--- |
| 1 | A decision model is a paradigm on a par with LLMs, not a harness add-on. Get the most out of it by combining it with software engineering, Python code, and every kind of LLM | Framed it as "the System-1 layer" around the model | **Agree.** Version 2's own evidence supported the wider frame | A1 |
| 2 | Many LLM calls in this repo could run on Jev, about 200x faster and cheaper | Listed decision points by loop; no file-level list | **Agree on the calls; disagree on "200x"** for speed. Ours: 3-5x per call end to end, and about 20x only when batching replaces sequential calls. Cost is where the gain is large | A2, A9 |
| 3 | Structured output becomes trivial with Jev | Schemas never read field by field | **Partly.** True for closed fields: `Literal`, booleans, ordered scales, a pick among candidates. False for free text, numbers, and dates | A3 |
| 4 | RAG retrieval, ranking, scoring, and binary evals in about a second, at the best accuracy, over any number of documents | Graders and reranking at R2 | **Partly.** Grading, reranking, routing, and verification over the top k: yes. First-stage retrieval over the corpus stays with the index. Accuracy was near the LLM's, not the best | A4, A9 |
| 5 | Update the infrastructure; first apply the best practice to what we already have, and learn by doing it | "Now: no code"; first code at R2 | **Agree.** This was version 2's main gap | A2, A10 |
| 6 | Simple, clear, valuable first uses were missing | [use-cases.md](use-cases.md) lists the points | **Partly.** The list exists, but it didn't say which file changes first, and when | A2, A3 |
| 7 | A next level: harder, compositional, creative uses, many still to be discovered; the LLM-decision-code triangle | A catalog of patterns | **Agree.** Patterns were catalogued; nothing was named to build | A6, A7 |
| 8 | Calling Jev should be as natural as calling a model, not a course subject | D1, a dedicated stage | **Agree on the call. Disagree on dropping the concept.** Decomposing and thresholding judgment is a hard concept (62.6% → 95.0% from decomposition alone). D1 is reframed, not removed | A1, A8 |
| 9 | Wherever there is an opportunity, it must be used | "Never forced"; the rubric | **Agree as the default for decision points. Disagree** on use without measurement, and on any gate that grants | A10 |
| 10 | Architect so that patterns built on decision models carry real weight | Architecture principle 10; design card point 17 | **Agree.** The composition patterns gain them | A1, A7 |
| 11 | Many small, very useful utilities can be built | None named | **Agree** | A6 |
| 12 | Future stages must use it | Placements through P6 to E2 | Already covered; A2 to A8 move some earlier | none |
| 13 | Build further, professional, deeper things with it; that is where the teaching happens | Five short labs | **Agree.** The labs were too small | A7, A8 |
| 14 | Don't forget the obvious: schemas and the model-tier selection system | Tier routing at P9-B2 and E2; schemas not analyzed | **Agree on both.** Tier routing moves to R2, not to "now": it needs an answer-quality eval, which R2 builds | A3, A5 |
| 15 | Decision models and language models are the two wings of agentic systems | "System-1 layer" | **Agree,** as the frame | A1 |

## Why version 2 missed these

- **A double standard.** Version 2 required a labeled set and a teaching stage before a
  decider could take a decision point. The LLM deciders already in the code have no labeled set
  at all (A2). Principle 2 applies one standard to every decision point, whatever its backend.
- **Sequencing read too conservatively.** Points were tied to the roadmap slot of the project
  they sit in (tier routing to P9-B2), not to the first stage where their prerequisites exist.
- **The analysis stopped at the call site.** The output schemas were never read field by field.
- **Patterns without builds.** The office catalogued what others built and named nothing for
  this repo to build.

## A1. Two model families in the models layer

- **The frame.** The system has two model families:
  - language models write;
  - decision models decide.

  Every AI step is one of them, plain code, or a composition of the three. "System-1 layer"
  remains the name for where decisions sit, not for what a decision model is.
- **The seam.** A decision model is a first-class citizen of `models/` and
  `configs/models_config.py`, obtained the way a tier is:
  - a pinned model ID in the config;
  - the key referenced by environment variable name;
  - defined test-mode behavior;
  - a scripted fake for unit tests.

  Proposed name: `decision_model`, beside `llm_model`. This is an infrastructure seam, which
  principle 3 builds production-grade from its first consumer. It is not a registry of agents
  (ADR-0006).
- **The client.** `langchain-typesafe` is alpha. Two options:
  - enter it with a recorded pre-release reason, as version 2 proposed;
  - write a small in-house client over the System One API (one POST, typed answers).

  Both passed the same protocol checks
  ([EV-2026-09-27-jev-openrouter](../../evidence/EV-2026-09-27-jev-openrouter/README.md), 11/11).
  The lead decides.
- **Timing.** It arrives with the first retrofit in A2 (R1), not at R2.
- **Composition patterns** in ARCHITECTURE gain two entries next to the gate:
  - **cascade:** decide when confident, escalate otherwise;
  - **generate, then decide:** an LLM drafts candidates, a decider judges them, code picks.

## A2. Phase 1: retrofit the decision points that already exist

The return pass (R0 to R5) and the P5 teaching pass revisit P1 to P5. Each revisit retrofits its
project's decision points, measured on a labeled set, with the LLM measured on the same set
first.

| # | Call site | Today | The decision | Proposal | Stage |
| :-: | :--- | :--- | :--- | :--- | :--- |
| 1 | `middlewares/groundedness_middleware.py`, `response_groundedness` | `low` LLM; **no consumer in `src/` today** | Is the final answer supported by the tool outputs (`GroundednessVerdict`) | Wire it into P1's researcher as R1's claim check: one `noul` per claim, the decider first, the LLM on a thin margin | R1 |
| 2 | `ResearchReport.confidence` (P1) | The LLM writes a float | How much the sources agree | Derived in code from per-claim support decisions, instead of a number the model writes | R1 |
| 3 | `nodes/rag_node.py`, `grade_documents_node` | `opensource` LLM, **one sequential call per document** | Is each document relevant (`GradeDocument`) | One batched request, one named question per document; thin margins escalate. The same request can rerank | R2 |
| 4 | `nodes/rag_node.py`, `check_hallucination_node` | `low` LLM | Is the answer grounded (`GradeHallucination`) | Decider first, LLM on a thin margin (draft, verify, escalate) | R2 |
| 5 | `nodes/rag_node.py`, `generate_node` and `query_rewrite_node` | `medium` and `opensource` LLMs | Which tier writes this answer | A5's tier decision, measured on R2's labeled set | R2 |
| 6 | `nodes/code_review_node.py`, review | LLM writes the whole `ReviewResult` | Each issue's severity and category; the score | R3's hybrid: `ruff` and the AST find issues; the decider classifies each finding; the LLM explains | R3 |
| 7 | `agents/interpreter_agent.py`, `execute` approval | Static HITL on every call | Should a person look at this command closely | **No loosening:** HITL stays on every call. The decider may add a risk label to the approval prompt, which is triage for the person | R4 |
| 8 | `middlewares/security_guard_middleware.py` (memory writes, skill publishing) | `low` LLM through the injectable `classifier=` | allow, ask, or block; the category; the reason | Three `noul` checks combined fail-closed in code, beside the LLM, tightening only; the reason comes from a template per category | P5 teaching pass |
| 9 | `nodes/memory_consolidation_node.py` | LLM writes `MemoryEdits` | Staleness; each edit's kind; which existing line and heading it touches; whether the user asked | Decisions over candidates code lists (A3); `new` and `reason` stay with the LLM; implied changes escalate | P5 teaching pass |
| 10 | `agents/coding_coordinator_agent.py`, `agents/repo_insight_agent.py` | Tool calling by the LLM | Which specialist takes the request, or "clarify" | A pre-router with "clarify", the LLM on a thin margin; measured on R5's scenario, built in P6-A1 | R5, P6 |
| 11 | `graphs/rag_graph.py`, `route_after_grading`; the Finglish detector | Code | none | **Stays code.** Code already decides | none |
| 12 | `query_rewrite_node`, `generate_node`, `finglish_output_middleware.py`, `skill_designer_node.py`, test generation | LLM | none: they write | **Stay LLM** | none |

## A3. Structured output, field by field

A decider fills a field when its value comes from a closed set: an option list, a yes or no, an
ordered scale, or a pick among candidates that code extracted from the input. It doesn't write
text, and numbers and dates are its documented weak spots
([Jev](../../landscape/decision-models/jev.md#where-it-breaks-by-its-own-account)). So the right
design is a split by field, not "Jev instead of structured output".

| Schema | Decider fields | Code fields | LLM fields |
| :--- | :--- | :--- | :--- |
| `GradeDocument`, `GradeHallucination`, `GroundednessVerdict` | `binary_score`: the whole schema | none | none |
| `GuardVerdict` | `decision`, `category` | the fail-closed combination | `reason`, or a template per category |
| `CodeIssue` | `severity`, `category` | `line_number`, from `ruff` or the AST (R3) | `description`, `suggestion` |
| `ReviewResult` | `score`, as an ordered scale with fitted thresholds (not a calibrated number) | none | `summary`, `refactored_code` |
| `MemoryEdit` | `kind`, `user_requested`; `path`, `section`, and `old` as picks among the existing files, headings, and lines | applying the edit | `new`, `reason` |
| `ResearchReport` | per-claim support (A2 #2) | `confidence`, derived | `topic`, `summary`, `key_findings` |
| `SpecialistResult` | whether a claimed `ok` is backed by its provenance (a check by the parent) | `status` from the specialist's own logic | `reason` |
| `ArtifactMetadata`, `TestExecutionResult` | none | everything: extension, size, exit code | `description` |
| `TestSuite`, `SkillDraft`, `FinglishLines` | none | none | everything |

**What it enables:** a utility that turns a Pydantic schema's closed fields into questions, using
the `Field` descriptions the schemas already carry. The binary graders' descriptions already read
like a `noul`'s criteria. Code merges the decider's fields with the code and LLM fields into
one validated object (A6 #2).

## A4. RAG, stage by stage

| Stage of the pipeline | Backend | Why |
| :--- | :--- | :--- |
| Candidate retrieval over the whole corpus | The vector index (and BM25 when hybrid) | A decider pays for every token it reads, and a request holds 32k tokens. Over 10,000 chunks of 300 tokens, one query would read 3 million tokens: about $0.13, at least 94 full requests, and about 12 s at TypeSafe's published 250,000 tokens per second **[S]** |
| Relevance grading of the top k | Decider, batched, one named question per chunk | Measured 6/6, and 5-6/6 batched in about 0.45 s **[V]** |
| Reranking the top k | Decider | Tied with Cohere's reranker over 14 datasets **[T]** |
| Routing: corpus, rewrite, web, or clarify | Code on the decisions' outputs | Code decides once the judgments are typed |
| Answer and rewrite | LLM, tier from A5 | They write |
| Groundedness, then per-claim support | Decider first, LLM on a thin margin | 6/6 on single-claim cases **[V]** |

**The honest numbers:** for four to six chunks, grading drops from several seconds of sequential
LLM calls to about half a second, at a small fraction of the cost. "About a second" holds for the
top k. It doesn't hold for "any number of documents", and accuracy was near the LLM's, not above
it. R2 measures the whole pipeline on its labeled set.

## A5. Model-tier selection, per request

- **Today.** A static tier per call site (ADR-0014). Within a tier, the provider order comes from
  a weighted score in `configs/models_config.py`. Nothing chooses per request.
- **The proposal.** A tier decision per request:
  - **For agents:** `wrap_model_call` with `request.override(model=...)`, LangChain's documented
    dynamic-model hook **[S]**.
  - **For chains:** the caller picks `llm_model.chain(tier)` from a decision on the input.
- **Question design** (decomposition, composite scoring). Don't ask "which tier" as one broad
  question. Ask four or five atomic questions, and let a rule or a small fitted model in code map
  the answers to a tier:
  - Does it need several steps of reasoning?
  - Does it need code or data work?
  - Is the context long?
  - Is it user-facing prose?
  - Is it in Finglish?
- **Labels.** Run every tier on a request set and judge each answer against a reference. The
  label is the lowest tier whose answer passes. R2's labeled question set is the first place
  where references exist, which is why this lands at R2, not before.
- **Evidence:**
  - LiteLLM's four-tier routing: 95.0% against 73.75% for `claude-haiku-4.5` **[T]**, on labels
    the authors wrote;
  - OpenRouter's Jev Router picks a model and effort per request **[S]**. It serves OpenRouter's
    catalog, not our GapGPT tiers, so it's a reference, not a drop-in.
- **Design question for the mentor and the lead:** the router has to choose a tier's primary and
  keep that tier's fallback chain (`make_model_fallback`). Middleware order decides whether that
  works.
- **Stage:** measured at R2, built into the models layer at D1, and taught in depth with cost at
  P9-B2.

## A6. Utilities

Small, each with its first consumer. They are plumbing, extracted by the rule of three: the
first two consumers keep them local.

| # | Utility | What it does | First consumers |
| :-: | :--- | :--- | :--- |
| 1 | `decision_model` (A1) | The seam: pinned ID, key, test mode, fake | Every point |
| 2 | Schema to questions (A3) | Builds questions from a schema's closed fields and their descriptions; merges the answers with code and LLM fields into one validated object | The three binary graders, the guard |
| 3 | Batch judge | One request, one named question per item. Naming every item is built in, because unnamed items decayed to 0.150 accuracy in one study | Document grading, reranking, memory recall, tool-result filtering |
| 4 | Cascade | The decider when the margin clears the threshold, otherwise the LLM; logs which path ran | Graders, staleness, routing |
| 5 | Escalate-only gate | Static rules decide "allow"; the decider can only add "ask" or "block" | The guard, `execute` triage |
| 6 | Decided edge | A LangGraph router whose branch comes from a `choice`, with a fallback branch for thin margins | P6's branches; semantic routing in the RAG graph |
| 7 | Decision log and cache | Logs the state hash, question version, probabilities, and path, keyed for cache and replay. Replays make tests deterministic, and the log is where labels come from | Every point |
| 8 | Threshold fitter | From a labeled set and a cost per mistake, the threshold, and coverage at an error budget | Every point; D1's core tool |
| 9 | Decision eval runner | Runs the LLM, the decider, and the cascade on one labeled set under `evals/`: accuracy per class, unsafe errors, coverage, p50 and p95, cost | Every point |
| 10 | Tool selector | A decider version of LangChain's `LLMToolSelectorMiddleware` (in `langchain` 1.4.2) **[S]** | Any agent with more tools than it picks reliably |
| 11 | Tier router (A5) | Per-request tier | R2's generation; every agent after |
| 12 | Keep or drop | Scores tool results before summarization or context editing | Long P4 and P1 sessions |
| 13 | Claim check | Verifies a specialist's `ok` against its provenance (R0's envelope) | Coordinators, P6 |

## A7. The compositional layer: the triangle

Each build names the job of each corner. The LLM writes, the decider judges, and code controls,
combines, and measures. These are where the deeper teaching happens.

| # | Build | LLM | Decider | Code | Teaches | Where |
| :-: | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Decision workbench.** It serves every other point, so it comes first | Compiles a prose policy or rubric into several candidate question sets | Runs each set over the labeled data | Fits thresholds, compares wordings, versions the winner, watches drift | Decomposition, measurement, versioning ("compile, then run") | D1's main build |
| 2 | Generate N, select one | Drafts N answers or plans | Scores each on atomic criteria: grounded, answers the question, follows the policy | Combines the scores and picks, or escalates when none pass | Cheap verification makes N affordable | D1 lab; R1 and P6 practice |
| 3 | Search with a decider as the value function | Expands plans or tool sequences | Scores each state: closer to the goal, breaks a constraint | Beam or tree search and pruning | Search with a learned heuristic | D1 lab; P9-C2, P12-B1 |
| 4 | Composite scoring | none | Answers atomic `noul`s | A small fitted model (logistic regression) combines them | Semantic features for classical ML: the 62.6% → 95.0% result | D1 lab; P8 triage |
| 5 | Active learning | Labels the low-confidence cases, or a person does | Answers everything | Adds the labels to the set, refits thresholds, tracks coverage over time | The data flywheel before P8-C2 | D1; P8-C2 |
| 6 | Speculative decisions | none | Answers every question the flow might need, in one request at the start of a turn | Ignores what doesn't apply | Latency engineering | P6 |
| 7 | Context assembly | Sees only what passed | Picks which memories, skills, documents, and tool results enter the context | Enforces a token budget | Context engineering as decisions | P5 teaching pass (recall); P12-B2 |
| 8 | Evals that are guardrails | none | Runs one question set offline on traces and online as middleware | Aggregates, alerts | One definition of quality in both places | R2 onward; P8-C2 |
| 9 | Trace monitor | Explains an escalation for the person | Watches each step of a running agent: off task, looping, a claim without evidence | Escalates or stops | Oversight of agents | P6-B2, P12 |
| 10 | Learner model | Words the hint | Picks the misconception | Tracks calibration and recurring gaps | The learning loop ([curriculum.md](curriculum.md#teach-with-it-the-learning-loop)) | From R1, formative only |

## A8. The curriculum

- **Everyday use is not a subject.** From R1 on, the learner writes a decision call the way they
  write a model call, inside each stage's own work (A2). No lesson is spent on "how to call Jev".
- **D1 stays, reframed.** Its hard concept is decision engineering and the compositional layer:
  - the workbench (A7 #1) is its main build;
  - A7 #2 to #5 are its labs.

  The placement is unchanged: between R5 and P6. That matches the user's point that the deeper,
  compositional layer is where the teaching happens.
- **The labs in [curriculum.md](curriculum.md#teach-by-building-it-labs)** are kept; A7 adds to
  them.

## A9. The numbers, corrected

| Claim | Evidence |
| :--- | :--- |
| Latency per call, end to end from the user's machine | Jev 439-475 ms; `glm-5.3` 2.2-2.3 s; `gemini-3.5-flash-lite` 1.4-1.6 s: **3-5x** **[V]** |
| Latency, like for like, measured independently | About **25x**; the vendor's 200x compares a full generation pass, warm-up included **[T]** |
| Latency when batching replaces sequential calls | Six documents in one request in about 0.45 s, against six LLM calls in series: roughly **20x** **[V]** for Jev, estimated for the LLM side |
| Cost | $0.042 per million input tokens, output free; about $0.00002 per decision here **[V]**. The vendor claims 40-400x cheaper **[C]**; $0.07 against $0.19 per thousand for the cheapest constrained LLM in one benchmark **[T]** |
| Accuracy | Near the LLM on well-phrased binary checks (22/23 against 23/23); better on routing and abstention (32/32 against 30/32) **[V]**; weaker on hard many-class intent and implied conditions **[T][V]** |

## A10. One standard for every decision point

- **Every decision point, whatever its backend, gets:**
  - a labeled set;
  - accuracy per class, and unsafe errors;
  - latency and cost.

  The LLM already in place is measured on the same set before any comparison.
- **The default flips.** At a decision point, the decider is the first candidate and the LLM is
  the escalation. The LLM stays primary only where the measurement says so, or where the step
  also writes. The rubric's order is unchanged: a step that writes goes to an LLM, and a step
  code can decide goes to code.
- **Gates are unchanged.** A decider may tighten or escalate. It never approves or loosens: 147
  of 200 authority-claiming injections succeeded **[T]**.
- **Languages.** Finglish subsets stay in every labeled set, and escalate until measured.

## What version 3 changes in BR-003's proposals

| # | Change |
| :-: | :--- |
| 3 | D1 reframed (A8) |
| 5 | The product harness starts with Phase 1 at R1, not R2 (A2) |
| 11 | **New:** decision models in the models layer (A1) |
| 12 | **New:** per-request tier selection, measured at R2 (A5) |
| 13 | **New:** field-level structured output, and the utilities (A3, A6) |
| 14 | **New:** the compositional builds, with the workbench first (A7) |
| 15 | **New:** one standard for every decision point, with the default flipped (A10) |
