# The Jev File: the Lead's Dossier

| | |
| :--- | :--- |
| Status | **Decided 2026-09-28:** the user accepted every leaning below after the joint review ([DECISIONS](../DECISIONS.md) DEC-022 to DEC-025, [ADR-0021](../../../docs/adr/0021-decision-models-as-a-second-model-family.md)). Opened 2026-09-27 on the user's word ("parvande-ye Jev ro shoru konim"). The binding rules now live in [`library/architecture/decision-models.md`](../../../library/architecture/decision-models.md); this dossier stays as the reasoning and the idea bank |
| Read for it | Research's whole dossier: [BR-003](../research/briefs/BR-003-decision-points/README.md) version 3 with its [second review](../research/briefs/BR-003-decision-points/second-review.md), use cases, plan, curriculum, and agent guidance; the nine [decision-model landscape](../research/landscape/decision-models/README.md) pages; the six Jev and Laya evidence records with their scripts and raw results; BR-001 and [BR-002](../research/briefs/BR-002-model-catalog-evidence-map/README.md). The four sources the user sent (shipwithjev.com; LangChain's *Building a harness with Jev* and *Building prod with Jev and LangGraph*; the video *7 Jev Repos That 10x Claude Code*, title only). The user's two reviews and later guidance, as research recorded them |
| Code read | `f261b6e`: the models layer, the output schemas, and every `llm_model` call site |

## 1. The position

- **Two model families.** A language model *writes*: answers, plans, code, rewrites. A decision
  model *decides*: typed answers to closed questions (`choice`, `score`, `noul`), with a
  probability per option, many questions per request, in about half a second and $0.00002 per
  decision from here. Agentic systems now fly on both wings.
- **The triangle.** Every AI step is designed from three corners: **code** (whatever a parser,
  a lookup, arithmetic, or a rule settles), **a decision model** (closed judgments over
  natural-language state), and **an LLM** (everything that writes, and the escalation path).
  The design question at each step is which corner takes it, and how the corners compose.
- **The rule, in order** (research's A10, adopted):
  1. A step that writes goes to an LLM. A step that decides *and* explains is split: the decider
     decides, an LLM or a template words it.
  2. A step code can decide goes to code.
  3. Every other decision point takes the **decider first and the LLM as its escalation**, both
     measured on the same labeled set. The LLM stays primary only where the measurement says so.
- **Natural, not a subject.** `decision_model` sits beside `llm_model` in `models/`. From R1 on,
  the learner writes a decision call the way they write a model call, inside each stage's own
  work.
- **Decision engineering is a discipline,** like prompt, context, graph, and harness
  engineering: designing the state and the questions, decomposing judgment, fitting thresholds
  from error costs, measuring. It is practiced from R1 and taught in depth at D1.
- **Gates escalate; they never approve.** That is a rule for every model, LLMs included
  (ARCHITECTURE principle 4), not a verdict on one vendor.

**The numbers the designs rest on** (all from research's records):

| Property | Measured |
| :--- | :--- |
| Latency per decision, end to end from here | 439-475 ms, against 1.3-2.3 s for our LLM tiers: 3-5x **[V]** |
| Batching | Six relevance pairs in one request in 422-524 ms, about 80 ms per decision **[V]** |
| Like for like, independent | About 25x **[T]** |
| Cost | $0.042 per million input tokens, output free: about $0.00002 per decision **[V]**; 551 builds classified in 33 s for $0.029 **[V]** |
| Our graders and guard | 22/23 in both question variants (`glm-5.3` 23/23); 0 of 48 guard decisions less strict than the label **[V]** |
| Our routing | 32/32 in three runs, including 12 Finglish requests and three negation traps; two LLM tiers 30/32, both sending vague requests to `memory` instead of `clarify` **[V]** |
| Our memory staleness | 59/60; thin margins exactly on the implied cases **[V]** |
| Decomposition | One task: 62.6% as one broad question, 95.0% as five atomic questions combined in code **[T]** |

The speed gain per call is real but smaller than the vendor's 200x; the cost gain is large; the
accuracy is close to our LLMs on well-phrased binary checks and better on routing and
abstention. Those facts shape the designs below (batching, cascades, decomposition). They don't
decide whether to use the wing.

## 2. Research's BR-003 version 3, read closely

**What holds up.** I re-checked the numbers BR-003 quotes against its records and scripts; they
match. Its strongest parts:

- the file-level retrofit of P1 to P5 (A2), which answers the user's "apply best practice to
  what exists" point;
- the field-by-field reading of our output schemas (A3);
- the honest corrections of speed and RAG claims, with its own arithmetic (A9, A4);
- **A10, one standard for every decision point.** Version 2 held the decider to a bar our LLM
  deciders never met: none of them has a labeled set. This is the most important amendment;
- the evidence that question design is engineering: wording alone turned one Finglish negation
  from 0.46 to 0.03 (right by a hair to confidently right) and one relevance case from 0.50 to
  0.15 (right by a hair to confidently wrong);
- the designed guard: three narrow `noul` checks with the whole policy in the state, combined
  fail-closed by a rule fixed before the run. It turned the plain variant's one safe miss into a
  correct answer, and it is the best teaching exemplar the file has.

**Where the lead's view differs or adds:**

| # | Point | Research v3 | Lead's leaning |
| :-: | :--- | :--- | :--- |
| a | Tier selection | A per-request prediction from atomic questions (A5) | Three mechanisms: calibrate the catalog, route per request, and verify then escalate (section 5) |
| b | Schema determination | Filling a schema's closed fields (A3) | Also choosing the contract, and verifying fields an LLM filled (section 4) |
| c | Tier-routing labels at R2 | "R2 builds the answer-quality eval" | R2's hard concept is retrieval evaluation. Its labeled set must carry **reference answers** as a stated requirement, or tier labels have nothing to judge against |
| d | R0 | No change | R0's next topic is the shared eval harness. Its case and metric shape must hold decision datasets (label, answer, probabilities, path, latency, cost) now, because R1's first consumer is a decision point |
| e | Migration recipe | Nine steps, starting from 50 hand labels | Add **shadow mode** before promotion: the decider runs beside the current backend, and their disagreements become the next items to label |
| f | Development-loop hooks | "The user's security call" | `.claude/` and `scripts/` are lead tooling (ADR-0019, ADR-0020). What needs the user's consent is the data flow: session content sent to a hosted decider, and past transcripts read for a replay |
| g | The design guide in the library | Promote it, maintained by research | Research writes nothing outside its office (the user's standing rule), so a library file can't be research-maintained. Split it: the binding rules go to the library, lead-maintained; the facts and evidence stay in research's landscape, linked from it |
| h | Radar | *Trial* at R2 | *Trial* at R1, where A2 put the first consumer |
| i | D1 | Between R5 and P6, reframed as the compositional layer with the workbench as its main build | **Agree.** The lead's first leaning was a foundation stage right after R0; A2 made that unnecessary, since everyday calls enter R1-R4 inside their own hard concepts. By R5 about six decision points will have been measured by hand, which makes the workbench an observed abstraction (principle 3), not a predicted one |

**Per proposal:** 1, 2, 5, 6, 8, 10, 11, 13, 14, and 15 agree as written (1 reworded around
the two families, not only "the System-1 layer"). 3 agrees (row i). 4 amends (row h). 7 amends
(row f). 9 amends (row g). 12 amends (rows a and c).

## 3. Level 1: the retrofit, stage by stage

The return pass already visits a decision point in almost every stage's own hard concept, so
the wing is woven in rather than bolted on. Each row names what each corner does.

| Stage | Decision point | Today | With both wings | LLM / decider / code |
| :--- | :--- | :--- | :--- | :--- |
| R1 | Claim support (`response_groundedness`, unused today; BACKLOG wires it in at R1) | `low` LLM, no consumer | One `noul` per claim against its sources, in one request; thin margins escalate | writes claims / judges support / splits claims, derives `confidence` from agreement |
| R1 | `ResearchReport.confidence` | A float the LLM writes about itself | Computed from the per-claim decisions | none / per-claim support / the formula |
| R1 | When to stop searching (with BACKLOG's search budget) | The model stops when it stops | "Is the evidence enough for this sub-question?" as the loop's stop condition, inside a budget code enforces | plans queries / judges sufficiency / enforces the budget |
| R2 | `grade_documents_node` | One sequential `opensource` call per document | One request, one named question per document; the probabilities also rank (BACKLOG's batch grading and reranker) | none / grades and ranks / top-k cut |
| R2 | Query entry | Fixed path | Every entry question asked at once (speculative fan-out): needs retrieval, corpus or web, clarify, multi-hop | none / all entry questions / picks the path |
| R2 | `check_hallucination_node` | `low` LLM | Per-claim support; unsupported claims reroute to rewrite or web (BACKLOG's reroute), thin margins escalate | writes / verifies / reroutes |
| R2 | Which tier writes the answer | Static `medium` | Measured here first (section 5) | writes / predicts difficulty / maps answers to a tier |
| R3 | `CodeIssue.severity`, `category`; `ReviewResult.score` | The LLM fills the whole review | `ruff` and the AST find issues; the decider labels each; the LLM explains | explains / labels and scores / finds |
| R4 | `execute` approval | Static HITL on every call | HITL stays on every call; a risk label is added to the approval prompt as triage for the person | none / risk label / the gate |
| P5 pass | Memory guard (`GuardVerdict`) | `low` LLM | The designed guard: three `noul`s, fail-closed rule, beside the LLM, tightening only | reason or template / three checks / the rule |
| P5 pass | Consolidation | The LLM writes all edits | A staleness pre-pass proposes; `kind`, `path`, `section`, `old` picked from code-listed candidates; `new` and `reason` stay with the LLM; implied changes escalate | writes `new` / picks and flags / lists candidates, applies |
| P5 pass | Recall and skills | Everything listed in the prompt | Which memories and skills enter the context, ranked (trigger: more skills than the prompt lists legibly) | uses / ranks / enforces the budget |
| R5 | Coordinator delegation | LLM tool calling | A pre-router with `clarify`, measured on research's 32-request set; built in P6-A1 | escalation / routes / dispatch |

Stays code: `route_after_grading`, the Finglish detector, exit codes, sizes. Stays LLM: the
rewrite, the answer, the Finglish repair, skill drafts, test generation.

## 4. Schema determination and structured output

"Schema determination" is three different decisions, and a decider serves all three.

1. **Filling a schema.** A decider fills a field whose value comes from a closed set. The
   mapping from Pydantic types:

   | Field type | Question | Note |
   | :--- | :--- | :--- |
   | `Literal[...]`, an enum | `choice` | Add `none` or `unclear` when the set isn't exhaustive |
   | `bool` | `noul` | The field's `description` becomes the criteria |
   | An ordered scale (`score: int` 1-10, severity) | `score` | Thresholds fitted on labels; the expected value isn't a calibrated number |
   | `list[Literal[...]]` (multi-label) | One `noul` per option | A `choice` picks exactly one |
   | A reference to something that exists (a memory file, a heading, a line, a row) | `choice` over candidates code lists, plus `none` | "Extraction without guessing" |
   | Free text, numbers, dates | none | The LLM writes; code parses and compares numbers and dates |

   Code merges the decider's fields, code's fields, and the LLM's fields into one validated
   object, and records per field where the value came from and its probability. The three binary
   graders and the guard already carry `Field` descriptions that read like criteria, so the
   compiler reaches its third consumer in the P5 teaching pass (principle 3).
2. **Choosing the schema.** Before extracting or generating, which contract applies: the
   document family and its schema (P7), the ticket's intent and its handler contract (P8), the
   response shape a request needs (a short answer, a report, a table), the specialist and its
   output contract (P6, P12). A `choice` over contracts, with `none` escalating.
3. **Verifying a filled schema.** When an LLM extracts a value, the decider checks it against
   the source: "does `document` state that the invoice number is `X`?" Per-field support becomes
   the per-field confidence P7-A1 and P7-B2 need, instead of a number the model writes about
   itself.

## 5. Model tier selection

Three mechanisms make one system, "cheap by default, frontier on exception":

1. **Calibrate the catalog.** Every tier's primary is picked from hand-estimated speed, power,
   and cost scores ([BR-002](../research/briefs/BR-002-model-catalog-evidence-map/README.md)
   #1: an engine without calibration data). A decider is a cheap, consistent judge: it scores
   every tier's answers on our labeled sets with a typed rubric, so the scores can be measured
   instead of guessed. The judge itself is checked against a hand-labeled sample. This makes
   P9-B2's "measured tier and cost choices" possible well before P9.
2. **Route per request.** Before generating, four or five atomic questions (several reasoning
   steps? code or data work? long context? user-facing prose? Finglish?) are mapped to a tier by
   a rule or a small fitted model in code (research's A5). For agents, LangChain's dynamic-model
   hook, `wrap_model_call` with `request.override(model=...)`, keeping the tier's fallback chain.
   For chains, the caller picks `llm_model.chain(tier)` from the decision. Labels: the lowest tier
   whose answer passes against the reference answer.
3. **Verify, then escalate.** After generating on the cheap tier, the decider checks the answer
   (support, completeness against the question); a failure escalates one tier. This needs no
   prediction of difficulty, only a check of the outcome.

Measured as one system: answer quality against cost and latency, on the same set. Reasoning
effort is part of the route where a provider offers it (OpenRouter's Jev Router picks model and
effort per request; it serves OpenRouter's catalog, so it is a reference, not a drop-in).

**A name to fix.** "Cascade" means two opposite things in the repo today. `TIER_CASCADE_ORDER`
in `configs/models_config.py` falls *down* the tiers when providers fail (availability), while
ARCHITECTURE's "Cascade" pattern goes *up* when a cheap decider isn't confident (quality). When
the quality escalation lands, the availability one becomes "fallback order", so "cascade" means
one thing.

## 6. RAG in about a second, for the top k

| Step | Corner | Time |
| :--- | :--- | :--- |
| Entry questions (retrieval needed, corpus or web, clarify, multi-hop) | Decider, one request | about 0.45 s |
| Candidate retrieval over the whole corpus | Code: the index, BM25 plus vectors (R2's hybrid retrieval) | fast |
| Grade and rerank the top k: one named `noul` per chunk; the probability is the ranking score | Decider, one request | about 0.45 s |
| Keep or drop passages verbatim before generation | Decider (same request) | included |
| The answer | LLM, tier from section 5 | the LLM's time |
| Split the answer into claims; support per claim; reroute or escalate | Code, then decider, one request | about 0.45 s |

"Any number of documents in a second" holds for the top k, not the corpus: 10,000 chunks of 300
tokens are 3 million tokens per query, which is about $0.13, at least 94 requests of 32k tokens,
and about 12 s at TypeSafe's published rate. The index stays the first stage.

## 7. Level 2: compositions

Research's patterns, and four the lead adds (marked **new**, hypotheses until measured):

| Pattern | LLM | Decider | Code |
| :--- | :--- | :--- | :--- |
| Decided graph: every conditional edge a decision with an escalation edge | on escalation | picks the branch | owns the graph |
| Speculative fan-out: every question the flow might need, asked once at entry | none | answers all | ignores what doesn't apply |
| Draft, verify, escalate | drafts | verifies support | escalates |
| Generate N, select one | drafts N | scores each on atomic criteria | combines, picks, or escalates |
| Menu-constrained action (tools, files, rows, UI elements) | fills arguments | picks from the menu | lists the menu |
| Context by decision; verbatim compaction | reads what passed | keeps or drops each item | enforces the budget |
| Decomposed judgment | none | atomic questions | rules, weights, or logistic regression |
| Memory leases | none | "does new evidence end this fact?" | expires it |
| Compile, then run | turns a prose policy into questions, once | runs them per case | the labeled set is their test suite |
| Evals that are guardrails | none | one question set offline and online | aggregates, alerts |
| Decision cache and replay | none | answers once | keys on model, question version, and state |
| **New: redundancy as uncertainty.** A question, its paraphrase, and its negation in the same request (nearly free, since latency is flat in the number of questions). Disagreement escalates; averaging lowers variance. Jev's own docs show a `noul` and its negation summing to 1.19, so the gap is a signal | none | answers all forms | measures agreement |
| **New: shadow mode.** The decider runs beside the current backend before promotion; disagreements go to review and become labels | the current backend | the candidate | logs, compares, queues |
| **New: evidence span first.** Code or an LLM cuts the span that matters; the decider judges only the span (against context rot, and within 32k tokens) | cuts, when code can't | judges the span | cuts, when it can |
| **New: trace taxonomy.** Every trace labeled with its failure mode (tool misuse, unsupported claim, loop, refusal, off task) | explains a flagged trace | labels every trace | aggregates by mode |

## 8. Level 3: the components to build

| # | Component | Stage |
| :-: | :--- | :--- |
| 1 | **The decision wing's infrastructure** (section 9) | R1 |
| 2 | **Primitives:** `decide`, `rank`, `route`, `gate`, `verify`, `cascade`, `decide_fields`, each extracted by the rule of three | R1 to the P5 pass |
| 3 | **The hybrid structured-output compiler** (section 4) | P5 pass |
| 4 | **Retrieval engine v2** (section 6) | R2 |
| 5 | **The tier system:** measured catalog, per-request routing, verified escalation (section 5) | R2 measurement; D1 build; P9-B2 cost |
| 6 | **The decision workbench:** an LLM compiles a policy or rubric into candidate question sets; each runs on the labeled data; thresholds are fitted from error costs; wordings compared; the winner versioned; drift watched | D1's main build |
| 7 | **Calibration and drift service:** coverage at an error budget per decision point, probability-distribution drift, a labeling queue fed by shadow disagreements | D1, then P8-C2 and C3 |
| 8 | **A decision-first workflow,** compared with code rules and a supervisor agent on one eval set | P6-C1 |
| 9 | **Search with a decider as the value function:** the LLM expands plans, the decider scores states, code runs the beam | D1 lab; P9-C2, P12-B1 |
| 10 | **Capability and tool selection over a catalog,** hierarchical beyond 255 options | P11-C3, P12-C1 |
| 11 | **Oversight:** the trace monitor online (off task, looping, a claim without evidence) and the trace taxonomy offline | P6-B2, P8-C2, E1 |
| 12 | **A decision service:** versioned question sets beside the versioned context registry, shadow evaluation, promotion gates, per-tenant thresholds | E2 |
| 13 | **The learner model,** formative only: which misconception, stuck signals, calibration of the learner's own predictions | From R1, the mentor's procedure |

## 9. The infrastructure seam (a sketch for the ADR)

- **`decision_model` beside `llm_model`** in `models/`, obtained the way a tier is: the pinned
  model ID (`typesafe/jev-1.13`) and base URL in `configs/models_config.py`, the key by variable
  name (`OPENROUTER_API_KEY`), an explicit timeout, a scripted fake for unit tests.
- **Client:** `langchain-typesafe` behind the seam (convention 9: built-ins before custom code),
  with a recorded pre-release reason and exit criteria (its first non-alpha release, or a small
  in-house client over `/v1/systemone` if it is still alpha at P8-C3). No call site imports it.
- **Backends by configuration:** Jev through OpenRouter now; TypeSafe direct; a local server on
  the same protocol for private state (the llama.cpp adapter, Open-Jev, or Laya). Swapping one
  changes no call site.
- **Conventions:** exactly one retry layer on the node (the client doesn't retry); a decider
  error in a cascade takes the LLM path; test mode keeps the backend, and a test profile may
  route decisions to the LLM path for comparison.
- **The decision log:** the state's hash, the question set's version, the served snapshot, the
  probabilities, the path taken, latency, and cost computed from input tokens (the client drops
  OpenRouter's `usage.cost`). It feeds the cache, replay, drift, and labels.
- **Question sets are versioned artifacts with their labeled sets,** reviewed like code; a
  rewording is an API change. Where they live is settled in the ADR (leaning: beside the prompts
  they parallel, thresholds in `configs/`).
- **No registry of decision points before E2,** where versioned registries arrive (ADR-0006).

## 10. Decision engineering: the accuracy techniques

The user's stated priority is raising decision accuracy through the semantics of the state and
the question. The techniques to measure on our own sets (routing 32, staleness 20, graders 12,
guard 8, lint 16 x 8; with Finglish subsets):

| Technique | Our evidence so far |
| :--- | :--- |
| A state `description`; named, backticked fields the questions refer to | Part of the designed variant [V] |
| The whole policy in the state, not compressed into option descriptions | Fixed the guard's goal-progress case [V] |
| Criteria for both outcomes, with the edge cases written in ("a visit is not a move") | Staleness traps all right [V] |
| Decomposition, combined by a rule or a fitted model | 62.6% to 95.0% [T]; the designed guard [V] |
| An honest answer set: `none`, `unclear`, `clarify` | Vague requests to `clarify` where LLMs weren't [V] |
| User content labeled as data, never instructions | Used in the designed variants [V]; injection remains [T] |
| English instructions over non-English state | Spanish study [T] |
| Every batched item named | Unnamed items decay to 0.150 [T] |
| Option-order shuffling, measured | 13% of answers changed on reorder [T] |
| Paraphrase and negation ensembles (section 7) | Hypothesis |
| Evidence span first (section 7) | Hypothesis |
| Thresholds per class, from error costs | The simulated cascade: at a 0.7 margin, 19 of 23 decided with no error, the rest escalated [V] |

## 11. The development loop in this repo

Lead-owned tooling, advisory first, each measured before anything blocks:

- **Document health** (principle 9, the lead's project-boundary review): code shortlists similar
  paragraphs across the docs; a `noul` per pair asks whether they state the same fact; duplicates
  and statements that contradict a state file are reported.
- **Done gate** (principle 5): a Stop hook that asks whether "done" is backed by a check that
  ran, when files changed. The ecosystem's best-measured hook reported AUROC 0.976 [T].
- **Shell edits and ownership** (ADR-0020's open gap: the guard doesn't see shell commands):
  code flags commands that can write (redirects, `sed -i`, `tee`, `mv`, `python -c`); the decider
  asks whether one writes outside the role's paths; a yes asks the person, never allows.
- **Meaning-level conventions** in CI: only the rules a parser can't decide (our lint spike:
  clean separation on meaning rules, weak on the two parser rules).
- **The user's consent needed:** session content goes to a hosted decider, and a replay of past
  sessions reads the user's transcripts.

## 12. The program

| When | Lead | Mentor | Research | Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Now, R0** | After the joint review: DECISIONS entries and an ADR (two model families, the one standard, the seam); ARCHITECTURE (a principle, a Decisions thread, generate-then-decide among the patterns, the cascade name); radar; design-card point 17; the library entry and a `decision-points` skill; the P1 design card with its decision points | Topic 3's eval harness shaped for decision datasets | Seed labeled sets from its cases, with Finglish subsets; the accuracy-techniques study (section 10) | The joint review |
| **R1** | `langchain-typesafe` enters; radar to *Trial*; `AGENTS.md` convention 3 names `decision_model` | The seam integrated as plumbing; the learner writes the claim check and the sufficiency stop | Labels from R1's decision log | Claim check against the LLM on R1's set |
| **R2** | Tier-routing and catalog-calibration measurement defined | Grading, reranking, entry fan-out, per-claim verification; R2's set with reference answers | Measurement support | Cascade matches the LLM grader on held-out data |
| **R3, R4** | | The review triangle; the `execute` triage label | | Per stage |
| **P5 pass** | | Designed guard, staleness pre-pass, recall ranking; the schema compiler at its third consumer | | No unsafe guard error |
| **R5** | | Pre-router measured; decision points in the first teach-back | | Coverage at an error budget |
| **D1** | Stage made ready | Workbench, then labs: generate-N-select, value-function search, composite scoring, active learning | | Per lab |
| **P6 onward** | Design cards name every decision point | Decided branches (A1), three control styles (C1), done checks on envelopes (B2), schema choice and field verification (P7), cascade at scale and trace taxonomy (P8), measured tiers (P9-B2), catalog selection (P11-C3, P12-C1) | | Per stage |
| **E1, E2** | Decision service, versioned question registry, shadow evaluation | | | Per stage |

## 13. For the joint review

1. **D1** between R5 and P6, as research's version 3 has it. Leaning: yes (section 2, row i).
2. **The client:** `langchain-typesafe` behind our seam, or an in-house client now. Leaning: the
   package behind the seam.
3. **Where question sets live.** Leaning: beside the prompts they parallel.
4. **Private state (P5 memory):** hosted with one data policy for every provider, or a local
   backend on the same protocol. Leaning: hosted now under the data policy; the local backend is
   the production path the seam keeps a swap.
5. **Development-loop hooks,** and consent for the data they send and for a replay.
6. **Tier-routing measurement at R2** with reference answers added to R2's set, or later at P6.
7. **The design guide:** rules to the library, facts to stay in research's landscape.

## 14. Found on the way

- The radar's Jev row says measuring it "needs a TypeSafe key"; the OpenRouter key has reached
  it since 2026-09-27 (research withdrew RS-007). The backlog item for a TypeSafe key is
  obsolete the same way. Both are corrected with the decisions.
- The radar holds OpenRouter at *Hold*, while it is Jev's access path; its ring moves with the
  decisions.
- A fourth role is coming (research's state, the user's word). The ownership map, the worktrees,
  and the hooks' role list will need it when it is defined.
