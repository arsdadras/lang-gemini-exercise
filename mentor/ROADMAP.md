# Roadmap (v5)

What gets built and taught, in which order, and the gates between. Mentor-owned.

- The rules this plan is built with (competencies, difficulty curve, admission rule, phases,
  readiness): [pedagogy](../library/teaching/pedagogy.md).
- System direction: [ARCHITECTURE.md](../docs/ARCHITECTURE.md). Candidates not yet placed, and the small
  items each stage carries: [BACKLOG.md](BACKLOG.md). Live stage status: the mentor's
  [state](STATE.md).
- v4 (2026-09-26) supersedes v3 (`git show 8ffbf09:docs/ROADMAP.md`); the changes are
  DEC-003 and DEC-004 in [DECISIONS.md](DECISIONS.md). v4.1 (the same day) adds P7-C2 and the
  E2 context registry (DEC-011, DEC-013). v4.2 (2026-09-28) weaves decision points through the
  return pass and adds D1 (DEC-024, [ADR-0021](../docs/adr/0021-decision-models-as-a-second-model-family.md)). Stages are re-cut at each phase start when
  the build shows a better split; the difficulty rules still apply.
- **v5 (2026-10-05, the learner's decision, written by the mentor):** Term P becomes 14 projects in
  two semesters of seven; a professional content generator is the new P6; R1 grows the
  researcher's capability (its writing and fact-checking ideas move to P6); R1b is dropped. Projects
  after P5 are renumbered (table under Program shape); records written before v5 keep the old
  numbers.

## Now, next, later

- **Now:** R1, a stronger researcher ([design card](../docs/design_cards/P1_research_agent.md#r1-redesign-a-stronger-researcher-2026-10-05-not-built)): topic 1 (claims instead of findings) is taught; options and planning, more sources with a source router, and the stop condition come next. R0 is closed ([ADR-0026](../docs/adr/0026-the-specialist-contract.md)).
- **Next:** R2 -> R3 -> R4 -> P5 teaching pass (B4 to C4) -> R5 -> D1 -> P6 (content generator) -> P7 (Capstone I).
- **Later:** P8 -> P9 -> P10 -> P11 (Capstone, midterm II) -> P12 -> P13 -> P14 (Capstone II) -> Term E.

## Program shape

- **Term P, 14 projects in two semesters of seven.** Semester 1: P1-P5 (specialists), P6 (content
  generator), P7 (Capstone I). Semester 2: P8-P10 (specialists), P11 (Capstone, midterm II), P12
  and P13 (specialists), P14 (Capstone II). Small composition exercises (mini-workflows) recur
  inside the projects instead of waiting for the end.

  | v4 number | v5 number | Project |
  | :--- | :--- | :--- |
  | (new) | P6 | Content generator |
  | P6 | P7 | Capstone I, Research-to-Decision workflow |
  | P7 | P8 | Document intelligence (P10, visual perception, stays folded in) |
  | P8 | P9 | Customer support operations |
  | P9 | P10 | Data and SQL analytics |
  | (new) | P11 | Capstone, midterm II |
  | P11 | P12 | API and business operations |
  | (new) | P13 | Open specialist slot, chosen by the mentor |
  | P12 | P14 | Capstone II, Business Operations Control Tower |

- **Return pass (R0-R5)** between P5 and P6: one contract for P1-P5 and one real upgrade each
  ([ADR-0011](../docs/adr/0011-return-pass-before-p6.md)).
- **Term E** (productization and scale) starts only after P14, through the entry gate below.

## Done

| Project | What it proved | Record |
| :--- | :--- | :--- |
| P1 Research agent | One DeepAgents agent with search, a structured cited report, fallback, approval before search, a researcher subagent | Handoff history |
| P2 RAG agent | Raw `StateGraph` with grading, a corrective loop, checkpoints, streaming, time travel, web fallback, a hallucination check; a coordinator with a retrieval skill | Handoff history |
| P3 Code review | Three compiled subgraphs, sandboxed tests, a self-correcting loop, an `interrupt()` gate | [Study guide](../docs/study_guides/p3_code_review/MASTER_GUIDE.md) |
| P4 Sandbox interpreter | Shell workspace with approval, artifacts, durable sessions, the first mini-workflow (coding coordinator) | [Study guide](../docs/study_guides/p4_sandbox_interpreter/MASTER_GUIDE.md) |
| Stage 0 stabilization | One package, composition root, identity as runtime context, secret isolation | ADR-0001 to ADR-0007 |
| P5 Memory assistant | Governed per-user memory with one writer, guards, undo, durable SQLite, eval-lite, governed skills, a context provider. Built by the mentor; taught again from B4 after R4 | [ADR-0013](../docs/adr/0013-p5-completion.md), [design card](../docs/design_cards/P5_memory_assistant.md) |

## Return pass (R0-R5)

**The specialist contract** is caller-agnostic, derived from the callers P1-P5 already have, and
checked in every R stage:

- a typed result envelope: output, provenance, status (`ok` / `partial` / `failed`), declared
  side effects, and the failure reason;
- `UserContext` wherever user data is touched;
- one approval path: the standard HITL request, streamed by the app;
- secret redaction at the app boundary and trace masking, in every app;
- a design card, written before the specialist's R stage, naming its decision
  points (point 17);
- an eval-lite smoke set of 5-10 scenarios.

Conformance work is done by the mentor directly; each stage's lesson is its upgrade. No rewrites
unless a project can't meet the contract. Every stage ends with a before/after demo of the same
scenario.

| Stage | Hard concept | Advances |
| :--- | :--- | :--- |
| **R0, the specialist contract** | What a caller must know about a specialist: envelope, provenance, status, declared side effects, and the failure contract (what "partial" means, who retries) | C4, C5 |
| **R1, P1 a stronger researcher** | Multi-source research with provenance: research options and planning, more sources (web, private corpus, academic, a research API) chosen by a source router, every fact traceable to its source ([design card](../docs/design_cards/P1_research_agent.md#r1-redesign-a-stronger-researcher-2026-10-05-not-built)) | C3 |
| **R2, P2 a stronger retriever** | The RAG agent's engine (P2's role is the RAG agent, ADR-0030): hybrid search, reranking, query rewriting, the index rebuilt; judged by hit rate at k (the harness itself is on the engineering track) | C3, C8 |
| **R3, P3 hybrid analysis** | Deterministic tools first, model second: `ruff` and AST findings feed the review; the model explains instead of hunting | C1, C9 |
| **R4, P4 capability upgrade** | Chosen with the mentor; declared side effects and the risk label moved to the engineering track (ADR-0027) | C4 |
| **R5, close** | None new: practice across all five specialists on one scenario, and the first teach-back. P6 Session 0 starts from here | C10 |

Each stage also carries its scheduled items from [BACKLOG.md](BACKLOG.md).

**Decision points in the return pass** (ADR-0021; the [dossier](attachments/jev-dossier.md),
section 3). Each lives inside its stage's own hard concept, so none adds a second one:

- **R1:** the `decision_model` seam with the source router (`research_sources@1`: which sources a
  question needs) and "is the evidence enough?" as the search loop's stop condition inside the
  budget. The claim check is built; its teaching moves to P6's fact-check stage.
- **R2:** grading and reranking in one request; the entry questions asked at once; per-claim
  verification with reroutes; tier routing and the catalog measured on a labeled set that
  carries reference answers.
- **R3:** `ruff` and the AST find issues, a decider labels severity, category, and score, the
  LLM explains.
- **R4:** a risk label on the `execute` approval prompt; the approval itself unchanged.
- **P5 teaching pass:** the guard as three checks combined fail-closed; the staleness
  pre-pass; recall ranking; the schema compiler at its third consumer.
- **R5:** the coordinator's pre-router, measured on a labeled routing set.

## Engineering track (repo level, ADR-0027)

Hardening and service health, applied to every project and no project's stage: security,
redaction and masking, observability, failure handling and timeouts, contract conformance
(`UserContext`, one approval path, declared side effects, an eval-lite set per specialist), the
retrieval harness, and R4's side effects and risk label. Waiting items: MN-018 (an undeclared
decider label counts as unsafe: built), MN-023 (a `read_page` budget, a cap on claims, the cost
of a decider outage at scale, sequential page requests).

## P5 teaching pass (after R4)

B4 to C4 again, one topic at a time, starting with B4 topic 1's tests-and-demo step, adapted to
whatever R0-R4 changed. C3's skill designer gets one line on its production analog, a
versioned context registry such as LangSmith Context Hub (DEC-011).

## D1: Decision engineering (between R5 and P6)

**Hard concept:** the compositional layer of decision models: decomposing a judgment into
atomic questions, fitting thresholds from the cost of each mistake, and measuring coverage at an
error budget. Advances C8, C9.

- **Main build:** the decision workbench. An LLM compiles a prose policy or rubric into
  candidate question sets; each runs on a labeled set; code fits thresholds, compares wordings,
  versions the winner, and watches drift. It generalizes the points R1-R5 measured by hand.
- **Labs:** generate N and select one; search with a decider as the value function; composite
  scoring (atomic questions and a small fitted model); active learning from low-confidence
  cases. The tier system (a measured catalog, routing, verify-then-escalate) is built here.

## P6: Content generator (new, 2026-10-05)

A professional content generator: from a brief (topic, audience, tone, length, format) to a
publishable, fact-checked piece (article, report, post). It calls P1 as its researcher subagent
and P2 for private knowledge. The learner's ideas and the decisions taken so far; the mentor writes
the design card and the stages.

- **Pipeline (sketch):** brief intake -> research plan -> P1 research (the fact pool: claims with
  URL and passage) -> fact check -> outline -> section writing -> grounding check -> editorial
  passes -> citations -> approval -> export.
- **Check first, then write.** Facts are checked before anyone writes (`check_claims`, decider
  first, the LLM only for the unsure). `supported` facts go to the writer; `unsupported` ones are
  omitted and listed (never silently); `doubtful` ones get one bounded re-research round and are
  checked again. Needs a fitted threshold on the decider's `none` (today a weak `none` is trusted).
- **Writer without tools,** natural prose with no per-sentence ids; a **grounding check** after it
  (`sentence_grounded@1`: one request, a question per sentence, against the supported facts),
  then one rewrite of the flagged sentences, then removal and `partial`.
- **One pipeline, profiles not modes:** a router decision (`brief` or `broad`) sets the budget,
  the planner, and the length; a specific question yields a short piece with few sources. `deep`
  is a later, bigger profile with corroboration (a second source for one-source facts).
- **Editorial passes:** outline approval (optional HITL), structure and coherence, a style guide,
  humanizing, format and SEO; judged by a rubric (evaluator-optimizer), with style guides as
  versioned skills.
- **Rejected so far:** a fact-checker *agent* holding the `decide` tool (the check is a fixed
  path; an agent would put `status` back under a model's opinion, against ADR-0026). An agent fits
  later for corroboration.
- **Stage sketch:** A1 brief to cited draft; B1 fact check, grounding check, doubtful
  retry; B2 parallel sections (`Send`) and cross-section consistency; B3 editorial passes with a
  rubric; C1 an eval set (groundedness, rubric score; the unsafe error is an unsupported fact in
  published text); C2 human review gates; C3 a mini-workflow.

## P7: Capstone I, Research-to-Decision workflow (L5)

Turn an open question into a grounded decision brief: external research, private knowledge,
optional analysis, verification, approval. Advances C4, C5, C8.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | A deterministic parent workflow over specialists: P1 and P2 called through the contract (P2's private knowledge a curated corpus of domain sources, so the brief can lean on established frameworks), its branches decided by typed decisions with escalation, synthesis, delivery gated on approval |
| **B1** | Fan-out and fan-in: parallel research branches with `Send`, merged by a reducer; source conflicts surface in the synthesis |
| **B2** | Failure by error class: retry transient errors, feed recoverable ones back to the model, pause for a human, cap runaway loops |
| **B3** | Nested runs: approvals raised inside subagents surfaced to the app (closes the coordinator's unapproved shell), progress streamed across namespaces, long runs resumed |
| **C1** | Deterministic vs model-directed control: the same eval set against the workflow with code rules, the workflow with decided branches, and a DeepAgents supervisor |
| **C2** | Evaluator-optimizer: a graph loop vs `RubricMiddleware`; the control choice recorded in an ADR |

## P8: Document intelligence (L5)

Also covers visual perception (formerly P10), and compiled knowledge (DEC-013). Advances C3, C6, C4.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Extraction into typed schemas for one document family, with per-field confidence (the family chosen by a decision; each field verified against its source) |
| **A2** | P2 grows into a RAG role agent (ADR-0030): a user's long documents ingested on demand into per-user collections, agentic retrieval (decomposition, multi-hop) as a graph with an agent node, served on its own and as a subagent and a tool |
| **B1** | Vision: scanned pages and images, tables and layout |
| **B2** | Validation loops, and human review of ambiguous fields only (confidence-based escalation to a person) |
| **C1** | Multi-document reasoning with provenance (page and region) and audit-ready output; reusable extraction skills |
| **C2** | Knowledge compilation: entities and relations extracted at ingest into our own typed schemas, with provenance, and an LLM-maintained, interlinked wiki over them; graph traversal combined with vector retrieval; judged against plain vector RAG on R2's harness with multi-hop and global questions |
| **C3** | Model-decided fan-out: an interpreter and dynamic subagents over many documents, against P7's code-decided `Send` |
| **C4** | Prompt injection carried in documents, including into model-written orchestration code, with a red-team scenario set |
| **C5** | Mini-workflow, Document Intake Cell: P8 extraction -> P2 lookup -> validation gate -> P4 report (practice) |

## P9: Customer support operations (L5)

Advances C4, C6, C8, C9.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Classify a ticket, retrieve an answer, draft a response |
| **B1** | Multi-intent tickets with customer context from P5, SLA and priority routing |
| **B2** | Router vs handoffs (the active agent changes mid-conversation), compared on the same tickets |
| **B3** | Escalation states and approval for sensitive actions |
| **C1** | Action permissions, ticket-system integration, audit trail, critic check |
| **C2** | A production feedback loop: feedback and annotation queues feed a regression gate, tested with simulated multi-turn conversations |
| **C3** | Calibrated cascade (System-1/System-2): a fast decider answers triage when confident and escalates to the LLM below a threshold fitted on C2's labeled data; asymmetric on sensitive classes; promoted only through C2's gate, with accuracy, latency, and cost measured against the LLM alone |
| **C4** | Mini-workflow (required), Support Resolution Cell: triage -> P2 -> P1 fallback -> critic -> approval -> response or controlled ticket update. Teaches response vs side effect (practice) |

## P10: Data and SQL analytics (L5)

Advances C3, C9, C4.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Question -> query -> result, with a table or chart |
| **B1** | Query validation and repair, read/write separation, approval before risky queries |
| **B2** | Sandboxed multi-step analysis through P4, with measured tier and cost choices (token cost per question, prompt caching) |
| **C1** | A semantic metric layer with provenance |
| **C2** | Reusable analysis plans and anomaly explanation |
| **C3** | Mini-workflow, Analytics-to-Report Cell: P10 analysis -> P4 artifacts -> P1 benchmark context -> verification (practice) |

## P11: Capstone, midterm II (new, 2026-10-05)

The second semester's midterm capstone, composing what semester 2 has built so far (P8 documents,
P9 support, P10 analytics) with P6's content generator, for example an insight-to-publication
workflow. Decided (ADR-0027): insight to publication, P10 analysis and P8 documents feeding P6, with
P9's review gate before publishing. Stages are written when semester 2 starts.

## P12: API and business operations (L6)

Advances C5, C6, C4.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Read-only integration with structured responses, through one MCP server |
| **B1** | Action proposals behind approval gates, with idempotency keys |
| **B2** | Retries, rate limits, and error mapping for external APIs |
| **C1** | Transactional boundaries and compensation |
| **C2** | Delegated authorization (the agent acts with the user's scoped credentials) and tenant isolation |
| **C3** | A connector catalog, with tool search (a decider over the catalog) once it outgrows the context |
| **C4** | Mini-workflow, Plan-to-Action Cell: plan -> context -> P12 proposal -> approval -> idempotent execution -> audit record (practice) |

## P13: Browser and computer-use agent (new, 2026-10-05; chosen in ADR-0027)

Chosen by the mentor before semester 2 starts. A candidate the mentor sees as uncovered: a browser
and computer-use agent (acting in web applications that have no API).

## P14: Capstone II, Business Operations Control Tower (L6)

A bounded control-tower workflow, not a generic super-agent: it routes a business request across
P5 context, P8 documents, P2 knowledge, P1 research, P10 analysis, P12 actions, and P4 artifacts.
Advances C4, C5, C10, C11.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Explicit routing over typed contracts: a sequential path plus one parallel branch, approval before side effects |
| **B1** | Planner/executor separation with task dependencies |
| **B2** | Partial failure and compensation across specialists, persistent workflow state, per-specialist permissions, context budgets |
| **B3** | Served through Agent Server: long tasks as async subagents the user can check, steer, or cancel |
| **C1** | A typed capability catalog replacing hand-written routing (the first real registry consumer, [ADR-0006](../docs/adr/0006-remove-agent-registry.md)); hierarchy only if the number of domains needs it |
| **C2** | Replay and audit, and a documented line between deterministic control and model-directed agency |

## Term E (after P14)

1. **E1, production hardening and evaluation:** eval datasets, trace taxonomy, timeouts and
   cancellation, idempotency, audit, authorization, sandbox and session isolation, threat modeling
   for excessive agency, a red-team suite.
2. **E2, shared runtime and platform:** lifecycle, event model, checkpoint, approval, and retry
   services; versioned agent, tool, workflow, and context registries (skills, instructions, and
   policies versioned and promoted like code; DEC-011); policy, model routing, decision (versioned
   question sets, shadow evaluation), memory, and artifact services. Proven by at least three workflows running on it.
3. **E3, distributed execution:** deployed agents behind an authenticated API, queue and workers,
   durable run state, scheduled jobs, a policy for new input on a running thread, tenant
   isolation, metrics, logs, and traces.
4. **E4, vertical product and adaptive systems:** one domain in depth, a thin UI over the event
   stream, trace-driven optimization behind evaluation and promotion gates.

Each E stage is planned in detail when it is reached.

**Entry gate from Term P:**

- the return pass complete;
- every specialist project complete, or waived with a recorded reason;
- P7 and P14 complete;
- at least three mini-workflows built during P8-P13;
- design cards and composition contracts for every retained specialist;
- deterministic and model-directed control compared at least once;
- an approval boundary and a side-effect boundary exercised;
- a failure replayed and analyzed;
- every shared abstraction justified by its consumers (Principle 3).

## Out of scope

Each line is a scope decision (Principle 2's "scope" argument); reopening one needs a recorded
decision.

| Out | Why |
| :--- | :--- |
| Training or fine-tuning neural models | A different discipline (ML engineering). In scope when a stage needs it: calibrating thresholds and fitting small classical classifiers on our own labeled data (P9-C3) |
| Temporal media and voice | Adds model plumbing, not agent architecture |
| Frontend engineering beyond a thin client | Not the subject; E4 has one thin UI |
| Editor and agent-to-agent protocols (ACP, A2A) | No cross-service consumer in Term P |
| LangSmith platform administration (self-hosting, BYOC, RBAC, gateway) | Operations of a vendor product, not system design |
