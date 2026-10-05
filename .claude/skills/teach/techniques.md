# Technique Cards

Step cards for the moves [SKILL.md](SKILL.md) names; open one when a probe or the topic plan
calls for it. Each card: when, steps, a repo example checked against the code, how it backfires
for an experienced learner, and one line of evidence ([evidence.md](evidence.md) owns sources).

1. [Probe and scaffold](#probe-and-scaffold): the prediction answer sets a component's depth.
2. [Runtime model and trace table](#runtime-model-and-trace-table): make execution visible.
3. [Labeled chunks](#labeled-chunks): purpose labels, fading from given to learner-made.
4. [Decision-point narration](#decision-point-narration): four beats per decision, none on routine.
5. [Design contrast](#design-contrast): the verified version beside a competent alternative.
6. [Rank and reveal](#rank-and-reveal): rank options for a production scenario, then the reasons.
7. [Reconstruct the decision](#reconstruct-the-decision): decide from an ADR's forces, then diff.
8. [Review the verified PR](#review-the-verified-pr): the learner reviews; my walkthrough settles.
9. [Refutation and feedback](#refutation-and-feedback): correct a wrong model so it stays fixed.
10. [Fading ladder](#fading-ladder): L1-L4 support per decision type, across projects.
11. [First-read opener](#first-read-opener): a short opening for a large, unfamiliar file.

## Probe and scaffold

**When:** before each core component's code, and again at each new framework mechanism.
1. Ask the component's prediction question as the probe, its expected answer written first.
2. Judge level as well as correctness: right and purpose-level is fluent; a right result with a
   wrong or line-by-line reason is partial; wrong on the new mechanism is shaky.
3. Fluent: no labels or traces; go to a contrast, a what-if, or the PR card. Partial: a trace
   table, then a purpose check. Shaky: the runtime model, a trace table, and labeled chunks.
4. Add at most one card per component to the required prediction, why, and what-if.
5. Keep the scaffold where experience misleads: a sequential call stack, "a retry is harmless".
6. Instant right answers drop a level at once; re-probe at the next new mechanism.
- **Repo example:** before `route_after_grading`: "Grading keeps nothing, every round. Which
  node runs after the third `grade_documents`?" Expected `web_search`: two rewrites made
  `retries` 2, and `2 < MAX_RETRIES` (2) is false. "`query_rewrite`" means partial: trace next.
- **Backfires for this learner:** full scaffolding on a mechanism read fluently adds load and
  reads as distrust. Fluent Python is not fluent reducers: expertise is per mechanism.
- **Evidence:** expertise reversal (Review) and a rapid first-step probe (QE, outside
  programming); moderate for the probe ([evidence](evidence.md#learning)).

## Runtime model and trace table

**When:** the probe shows a shaky model of how a graph runs: routing, reducers, loops, retries.
1. State the runtime model in one sentence before any table.
2. The learner fills the first two or three rows of a node-level table as the prediction.
3. Run it in test mode (streamed updates, or `history` in `lab-rag`); mark where it diverged.
4. Use a one-line path ladder for quick predictions, a per-step diff for reducer questions.
5. Add overlays one per message: failure, then persistence, then concurrency if present.
6. Stay at node level; go line by line only inside a router or reducer.
- **Repo example:** "Each node reads the whole state and returns a partial update; a field with
  no reducer is overwritten; the router reads the merged state; every step is checkpointed."
  ```text
  step | node            | writes                      | retries | router -> next
  1    | retrieve        | documents=[d1..d3]          | 0       | -> grade_documents
  2    | grade_documents | documents=[]  (overwrite)   | 0       | 0<2 -> query_rewrite
  3    | query_rewrite   | search_query=..., retries=1 | 1       | -> retrieve
  ```
  Failure overlay: `TRANSIENT_RETRY` on `retrieve` re-runs only the embedding call;
  `grade_documents` gets no node retry, since `llm_model.chain` has SDK retries and a fallback.
- **Backfires for this learner:** tracing a node body read at a glance; several overlays at once.
- **Evidence:** a tracing strategy with a memory table (RCT, 24 intro-course students); weak for
  experienced readers ([evidence](evidence.md#code-reading-and-design-judgment)).

## Labeled chunks

**When:** a structure's first appearance (graph, subgraph, middleware stack), probe not fluent.
1. Cut the component into three to six chunks by purpose, not syntax.
2. First appearance: I label each chunk; the learner says why one chunk earns its label.
3. Next appearance: I mark boundaries only; the learner labels; we discuss purpose differences.
4. Then the learner chunks and labels unaided; I correct only wrong or missing chunks.
5. One purpose-level answer advances a step; a new mechanism moves back one.
- **Repo example:** first appearance, `build_rag_graph`:
  ```text
  # 1. Register nodes; a retry policy only where a non-model external call lives
  # 2. Fixed spine START -> retrieve -> grade_documents, then branch on route_after_grading
  # 3. Close the loop: query_rewrite -> retrieve
  # 4. Terminal paths; compile with a checkpointer (InMemorySaver by default)
  ```
  Next appearance: `graphs/code_review_parentgraph.py`, markers only.
- **Backfires for this learner:** labels on familiar patterns or plumbing: redundant, and distrust.
- **Evidence:** subgoal labels (QE, novice programmers); given vs learner-made direction
  unverified; weak ([evidence](evidence.md#code-reading-and-design-judgment)).

## Decision-point narration

**When:** after a core component's code, in the walkthrough.
1. Take the component's three to five decision points from the topic prep.
2. At each, four beats: the force, two or three options, the choice, what the others break.
3. Routine lines get nothing; plumbing gets a link. Force before mechanism, never "obviously".
4. Close with the decision points as a numbered list: the teach-back asks about these.
5. Stop narrating a decision type once the learner produces its rationale unprompted.
- **Repo example:** `web_search`'s retry. Force: one non-model external call. Options: none; on
  the node; on the node and in the tool. Choice: `TRANSIENT_RETRY` on the node (convention 11).
  Breaks: none lets one timeout fail the answer; two layers of three attempts make up to nine calls.
- **Backfires for this learner:** narrating every line; narrating what the learner reasons out.
- **Evidence:** cognitive apprenticeship's modeling (Framework); no study of design-level
  narration; weak ([evidence](evidence.md#learning)).

## Design contrast

**When:** the architecture step or a fluent probe, where a competent engineer could choose
otherwise.
1. Show A (verified, diff-sized) and B (competent, one decision apart); B is labeled a variant
   in its first line and lives in `mentor/sandbox/`.
2. Name one scenario; the learner says where A and B diverge on it.
3. The learner says which ships and what the other invites, with a production force as reason.
4. Run both when the difference is observable.
5. Only then: the rule, and the record that holds it.
- **Repo example:** A keeps `retries` in `RAGState` with a `query_rewrite -> retrieve` edge; B
  loops in one `retrieve_and_grade` node under `TRANSIENT_RETRY`. On an embedding timeout, B's
  retry re-runs the grading model calls, and all attempts share one checkpoint.
- **Backfires for this learner:** a straw-man B; two differences at once; the rule told first.
- **Evidence:** comparing solutions (QE, 241 second-year CS students) and contrasting cases
  before telling (QE, college); moderate
  ([evidence](evidence.md#code-reading-and-design-judgment)).

## Rank and reveal

**When:** several defensible safeguards or placements, at the architecture step or for a
judgment gap; at architecture scale it is the design kata ([ai-engineering.md](ai-engineering.md)).
1. Write a five-to-ten-line scenario in production terms: users, load, a failure.
2. Offer three to five options: the design's, a competent novice's, one that breaks at load.
3. The learner ranks them, with two to four sentences of reasons.
4. Reveal the design's ranking and reasons, and a minority view where one is honest.
5. The learner writes what the design weighed that they didn't; feedback covers that gap only.
6. Record the gap as a review item ([materials.md](materials.md#review-items-table)).
- **Repo example:** a user asks P4's interpreter to clean up files. Rank: (A) a prompt forbidding
  it; (B) approval before every `execute`; (C) `virtual_mode=True`; (D) `build_sandbox_env()`.
  B and D are boundaries, neither replaces the other; C confines file tools only; A is no control.
- **Backfires for this learner:** straw men ranked by elimination; one right answer, no reasons.
- **Evidence:** ShadowBox rankings matched experts 28% and 21% better (QE, military, another
  domain); weak to moderate ([evidence](evidence.md#code-reading-and-design-judgment)).

## Reconstruct the decision

**When:** an ADR with context, alternatives, and consequences, on a decision type not yet met.
1. Give the context and forces only; hide the decision, alternatives, and consequences.
2. The learner writes a decision, two rejected alternatives, and one consequence that will hurt.
3. Reveal the full record as a full explanation, not only the answer.
4. The learner diffs: matches, what the record weighed that they didn't, what it lacks.
5. Feedback on the diff only; then "what would flip this decision?"
6. Ablation form, as a what-if: "Delete this decision. Walk the first production incident."
- **Repo example:** ADR-0006: a registry nothing looked agents up through; record: remove it
  until a coordinator selects specialists by metadata. Ablate ADR-0003 (`user_id` from
  `configurable`): `Runtime` has no `config`, so every user shares the default namespace.
- **Backfires for this learner:** forces the context only implies; a record with no alternatives
  (fixed first); a decision type already mastered.
- **Evidence:** problem solving before instruction (MA, g = 0.36); no study of ADR exercises;
  moderate for the order ([evidence](evidence.md#learning)).

## Review the verified PR

**When:** a fluent probe. It complements my walkthrough, never replaces it.
1. Intent first; the learner states two or three criteria a correct change must meet.
2. Tests beside the diff: which behavior each key test pins, what stays untested.
3. Three lenses: correctness under failure, conventions (`AGENTS.md`), the production path.
4. The learner writes two to four reviewer comments: question, suggestion, or reasoned approval.
5. My walkthrough sorts each: confirmed, answered by the design, or a finding to fix.
6. A seeded variant (one realistic defect) is labeled in its first line and lives in the sandbox.
- **Repo example:** `rag_graph.py`. "Who resets `retries`?" The caller, per `RAGState`; `run_rag`
  starts at 0 (`test_rag_from_the_corpus_is_ok_with_file_sources`). "Which test pins the router
  at `retries == MAX_RETRIES`?" None; `tests/` stubs the graph: a real finding.
- **Backfires for this learner:** no criteria means style nits; a large diff; bug-hunting framing
  on verified code feels staged, so frame it as understanding and challenging.
- **Evidence:** review yields knowledge transfer and education at Microsoft and Google (Q,
  professionals, perceived); weak to moderate
  ([evidence](evidence.md#code-reading-and-design-judgment)).

## Refutation and feedback

**When:** any wrong or partly right answer; the refutation step when it shows a wrong model.
1. Judge against the expected answer written before asking, never the learner's phrasing.
2. Sentence one: the verdict on the claim and the exact error. No praise padding.
3. What's right, only if specific and true; then the gap (force, mechanism, or boundary).
4. A misconception: name the wrong model, show where it fails, give the right one, re-predict.
5. End with one question that uses the correction.
6. Change position only on new evidence: a run, the source, a test.
- **Repo example:** "`virtual_mode=True` makes the interpreter safe." Partly: it confines file
  tools, not the shell. Re-predict: "Which control stops `cat ../../.env`?" Only approval before
  `execute`; `build_sandbox_env()` guards the environment, not files on disk.
- **Backfires for this learner:** a compliment sandwich; fixing all at once; no follow-up question.
- **Evidence:** information-rich feedback d = 0.99 vs 0.46, refutation g = 0.41, 38% of feedback
  interventions harmful (MA each); strong, general populations ([evidence](evidence.md#learning)).

## Fading ladder

**When:** a decision type recurs: retry layering, failure contracts, approvals, state reset.
1. L1 I narrate; L2 I ask and name the force to look for; L3 I ask, no hint; L4 the learner
   critiques a new variant I wrote (labeled, in the sandbox).
2. Start a new type at L1; a type from an earlier project at L2.
3. Up after two unaided right answers on that type; down one after a miss.
4. Fade on performance, never on schedule; keep each type's level in `STATE.md`.
- **Repo example:** retry layering. L2: "Look at what else this node calls; where does its retry
  go?" L3: "An agent gets a web-fetch tool; where does its retry go?" (`ToolRetryMiddleware`,
  `retry_on=is_transient`). L4: a sandbox `web_search_node` that also calls the model.
- **Backfires for this learner:** L1 on a familiar type; fading by calendar.
- **Evidence:** expertise reversal (Review), cognitive apprenticeship (Framework); the levels and
  thresholds are the mentor's choice; weak ([evidence](evidence.md#learning)).

## First-read opener

**When:** optional, about ten minutes before the probe, for a large or unfamiliar file.
1. First glance: "What caught your eye first and second? Do they relate?" I share mine.
2. The five most important lines, picked by each of us independently, then compared.
3. The why of two decisions: the assumption behind each and one alternative (the ladder).
4. Skip the club's other exercises (name lists, random lines, timed rounds).
- **Repo example:** my five in `rag_graph.py`: the conditional edge on `grade_documents`, the
  `query_rewrite -> retrieve` edge, `retries < MAX_RETRIES`, `TRANSIENT_RETRY` on `retrieve`,
  the `InMemorySaver()` default. Five `add_node` lines mean the design center was missed.
- **Backfires for this learner:** timed rounds on a short file; a pick of mine that isn't honest.
- **Evidence:** the Code Reading Club protocol (P), no outcome study; weak
  ([evidence](evidence.md#code-reading-and-design-judgment)).
