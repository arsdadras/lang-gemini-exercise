# Roadmap (v4.1)

What gets built and taught, in which order, and the gates between. Lead-owned.

- The rules this plan is built with (competencies, difficulty curve, admission rule, phases,
  readiness): [PEDAGOGY.md](PEDAGOGY.md).
- System direction: [ARCHITECTURE.md](ARCHITECTURE.md). Candidates not yet placed, and the small
  items each stage carries: [BACKLOG.md](BACKLOG.md). Live stage status: the mentor's
  [state](../mentor/STATE.md).
- v4 (2026-09-26) supersedes v3 (`git show 8ffbf09:docs/ROADMAP.md`); the changes are
  DEC-003 and DEC-004 in [DECISIONS.md](DECISIONS.md). v4.1 (the same day) adds P7-C2 and the
  E2 context registry (DEC-011, DEC-013). Stages are re-cut at each phase start when
  the build shows a better split; the difficulty rules still apply.

## Now, next, later

- **Now:** R0, the specialist contract (topic 2, the failure contract, in progress).
- **Next:** R1 -> R2 -> R3 -> R4 -> P5 teaching pass (B4 to C4) -> R5 -> P6.
- **Later:** P7 -> P8 -> P9 -> P11 -> P12 -> Term E.

## Program shape

- **Term P, 11 projects.** Specialists: P1-P5, P7-P9, P11. Capstones that compose them: P6 and
  P12. P10 was folded into P7; numbers stay stable so records keep their meaning
  ([ADR-0009](../../docs/adr/0009-stage-admission-rule.md)). Small composition exercises
  (mini-workflows) recur inside the projects instead of waiting for the end.
- **Return pass (R0-R5)** between P5 and P6: one contract for P1-P5 and one real upgrade each
  ([ADR-0011](../../docs/adr/0011-return-pass-before-p6.md)).
- **Term E** (productization and scale) starts only after P12, through the entry gate below.

## Done

| Project | What it proved | Record |
| :--- | :--- | :--- |
| P1 Research agent | One DeepAgents agent with search, a structured cited report, fallback, approval before search, a researcher subagent | Handoff history |
| P2 RAG agent | Raw `StateGraph` with grading, a corrective loop, checkpoints, streaming, time travel, web fallback, a hallucination check; a coordinator with a retrieval skill | Handoff history |
| P3 Code review | Three compiled subgraphs, sandboxed tests, a self-correcting loop, an `interrupt()` gate | [Study guide](../../docs/study_guides/p3_code_review/MASTER_GUIDE.md) |
| P4 Sandbox interpreter | Shell workspace with approval, artifacts, durable sessions, the first mini-workflow (coding coordinator) | [Study guide](../../docs/study_guides/p4_sandbox_interpreter/MASTER_GUIDE.md) |
| Stage 0 stabilization | One package, composition root, identity as runtime context, secret isolation | ADR-0001 to ADR-0007 |
| P5 Memory assistant | Governed per-user memory with one writer, guards, undo, durable SQLite, eval-lite, governed skills, a context provider. Built by the mentor; taught again from B4 after R4 | [ADR-0013](../../docs/adr/0013-p5-completion.md), [design card](../../docs/design_cards/P5_memory_assistant.md) |

## Return pass (R0-R5)

**The specialist contract** is caller-agnostic, derived from the callers P1-P5 already have, and
checked in every R stage:

- a typed result envelope: output, provenance, status (`ok` / `partial` / `failed`), declared
  side effects, and the failure reason;
- `UserContext` wherever user data is touched;
- one approval path: the standard HITL request, streamed by the app;
- secret redaction at the app boundary and trace masking, in every app;
- a design card, written by the lead before the specialist's R stage;
- an eval-lite smoke set of 5-10 scenarios.

Conformance work is done by the mentor directly; each stage's lesson is its upgrade. No rewrites
unless a project can't meet the contract. Every stage ends with a before/after demo of the same
scenario.

| Stage | Hard concept | Advances |
| :--- | :--- | :--- |
| **R0, the specialist contract** | What a caller must know about a specialist: envelope, provenance, status, declared side effects, and the failure contract (what "partial" means, who retries) | C4, C5 |
| **R1, P1 evidence-grounded research** | Claim-level provenance: read pages instead of snippets, map every claim to its sources, confidence from source agreement | C3 |
| **R2, P2 retrieval you can measure** | Retrieval evaluation: a labeled question set and hit rate at k, so changes are judged by numbers | C3, C8 |
| **R3, P3 hybrid analysis** | Deterministic tools first, model second: `ruff` and AST findings feed the review; the model explains instead of hunting | C1, C9 |
| **R4, P4 side effects as contract** | Declared side effects: the artifact diff becomes part of the result. Light by design | C4 |
| **R5, close** | None new: practice across all five specialists on one scenario, and the first teach-back. P6 Session 0 starts from here | C10 |

Each stage also carries its scheduled items from [BACKLOG.md](BACKLOG.md).

## P5 teaching pass (after R4)

B4 to C4 again, one topic at a time, starting with B4 topic 1's tests-and-demo step, adapted to
whatever R0-R4 changed. C3's skill designer gets one line on its production analog, a
versioned context registry such as LangSmith Context Hub (DEC-011).

## P6: Capstone I, Research-to-Decision workflow (L5)

Turn an open question into a grounded decision brief: external research, private knowledge,
optional analysis, verification, approval. Advances C4, C5, C8.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | A deterministic parent workflow over specialists: P1 and P2 called through the contract, synthesis, delivery gated on approval |
| **B1** | Fan-out and fan-in: parallel research branches with `Send`, merged by a reducer; source conflicts surface in the synthesis |
| **B2** | Failure by error class: retry transient errors, feed recoverable ones back to the model, pause for a human, cap runaway loops |
| **B3** | Nested runs: approvals raised inside subagents surfaced to the app (closes the coordinator's unapproved shell), progress streamed across namespaces, long runs resumed |
| **C1** | Deterministic vs model-directed control: the same eval set against the workflow and a DeepAgents supervisor |
| **C2** | Evaluator-optimizer: a graph loop vs `RubricMiddleware`; the control choice recorded in an ADR |

## P7: Document intelligence (L5)

Also covers visual perception (formerly P10), and compiled knowledge (DEC-013). Advances C3, C6, C4.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Extraction into typed schemas for one document family, with per-field confidence |
| **B1** | Vision: scanned pages and images, tables and layout |
| **B2** | Validation loops, and human review of ambiguous fields only (confidence-based escalation to a person) |
| **C1** | Multi-document reasoning with provenance (page and region) and audit-ready output; reusable extraction skills |
| **C2** | Knowledge compilation: entities and relations extracted at ingest into our own typed schemas, with provenance, and an LLM-maintained, interlinked wiki over them; graph traversal combined with vector retrieval; judged against plain vector RAG on R2's harness with multi-hop and global questions |
| **C3** | Model-decided fan-out: an interpreter and dynamic subagents over many documents, against P6's code-decided `Send` |
| **C4** | Prompt injection carried in documents, including into model-written orchestration code, with a red-team scenario set |
| **C5** | Mini-workflow, Document Intake Cell: P7 extraction -> P2 lookup -> validation gate -> P4 report (practice) |

## P8: Customer support operations (L5)

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

## P9: Data and SQL analytics (L5)

Advances C3, C9, C4.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Question -> query -> result, with a table or chart |
| **B1** | Query validation and repair, read/write separation, approval before risky queries |
| **B2** | Sandboxed multi-step analysis through P4, with measured tier and cost choices (token cost per question, prompt caching) |
| **C1** | A semantic metric layer with provenance |
| **C2** | Reusable analysis plans and anomaly explanation |
| **C3** | Mini-workflow, Analytics-to-Report Cell: P9 analysis -> P4 artifacts -> P1 benchmark context -> verification (practice) |

## P11: API and business operations (L6)

Advances C5, C6, C4.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Read-only integration with structured responses, through one MCP server |
| **B1** | Action proposals behind approval gates, with idempotency keys |
| **B2** | Retries, rate limits, and error mapping for external APIs |
| **C1** | Transactional boundaries and compensation |
| **C2** | Delegated authorization (the agent acts with the user's scoped credentials) and tenant isolation |
| **C3** | A connector catalog, with tool search once it outgrows the context |
| **C4** | Mini-workflow, Plan-to-Action Cell: plan -> context -> P11 proposal -> approval -> idempotent execution -> audit record (practice) |

## P12: Capstone II, Business Operations Control Tower (L6)

A bounded control-tower workflow, not a generic super-agent: it routes a business request across
P5 context, P7 documents, P2 knowledge, P1 research, P9 analysis, P11 actions, and P4 artifacts.
Advances C4, C5, C10, C11.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Explicit routing over typed contracts: a sequential path plus one parallel branch, approval before side effects |
| **B1** | Planner/executor separation with task dependencies |
| **B2** | Partial failure and compensation across specialists, persistent workflow state, per-specialist permissions, context budgets |
| **B3** | Served through Agent Server: long tasks as async subagents the user can check, steer, or cancel |
| **C1** | A typed capability catalog replacing hand-written routing (the first real registry consumer, [ADR-0006](../../docs/adr/0006-remove-agent-registry.md)); hierarchy only if the number of domains needs it |
| **C2** | Replay and audit, and a documented line between deterministic control and model-directed agency |

## Term E (after P12)

1. **E1, production hardening and evaluation:** eval datasets, trace taxonomy, timeouts and
   cancellation, idempotency, audit, authorization, sandbox and session isolation, threat modeling
   for excessive agency, a red-team suite.
2. **E2, shared runtime and platform:** lifecycle, event model, checkpoint, approval, and retry
   services; versioned agent, tool, workflow, and context registries (skills, instructions, and
   policies versioned and promoted like code; DEC-011); policy, model routing, memory and
   artifact services. Proven by at least three workflows running on it.
3. **E3, distributed execution:** deployed agents behind an authenticated API, queue and workers,
   durable run state, scheduled jobs, a policy for new input on a running thread, tenant
   isolation, metrics, logs, and traces.
4. **E4, vertical product and adaptive systems:** one domain in depth, a thin UI over the event
   stream, trace-driven optimization behind evaluation and promotion gates.

Each E stage is planned in detail when it is reached.

**Entry gate from Term P:**

- the return pass complete;
- every specialist project complete, or waived with a recorded reason;
- P6 and P12 complete;
- at least three mini-workflows built during P7-P11;
- design cards and composition contracts for every retained specialist;
- deterministic and model-directed control compared at least once;
- an approval boundary and a side-effect boundary exercised;
- a failure replayed and analyzed;
- every shared abstraction justified by its consumers (Principle 3).

## Out of scope

Each line is a scope decision (Principle 2's "scope" argument); reopening one needs a lead
decision.

| Out | Why |
| :--- | :--- |
| Training or fine-tuning neural models | A different discipline (ML engineering). In scope when a stage needs it: calibrating thresholds and fitting small classical classifiers on our own labeled data (P8-C3) |
| Temporal media and voice | Adds model plumbing, not agent architecture |
| Frontend engineering beyond a thin client | Not the subject; E4 has one thin UI |
| Editor and agent-to-agent protocols (ACP, A2A) | No cross-service consumer in Term P |
| LangSmith platform administration (self-hosting, BYOC, RBAC, gateway) | Operations of a vendor product, not system design |
