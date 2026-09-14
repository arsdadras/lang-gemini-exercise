# Curriculum Roadmap (v3)

Adopted 2026-09-13, refined 2026-09-14 ([ADR-0009](adr/0009-stage-admission-rule.md)). Replaces
the original 6-project roadmap and Roadmap v2. Both are still readable in git history
(`git show 85f714d:docs/ROADMAP.md`,
`git show "85f714d:docs/Agentic AI Curriculum Roadmap v2.md"`). Live status lives in
`docs/MENTOR_HANDOFF.md`.

## Shape

- **Term P:** 11 projects. P1-P5, P7-P9, and P11 build specialists; **P6** and **P12** are
  capstones that compose them. P10 (multimodal perception) was folded into P7; project
  numbers stay stable so ADRs and history keep their meaning. Small composition exercises
  ("mini-workflows") recur throughout, instead of waiting for the end.
- **Term E:** productization and scale, which starts only after P12.
- Every project has three phases. There is no fourth "hardening" phase
  ([ADR-0001](adr/0001-three-phase-project-model.md)).

## Stage admission rule

A topic, framework feature, or practice enters a stage only when all three hold:

1. **The project needs it now.** It solves a problem this project has at this stage, not one
   it might have later, and not one invented to show an API.
2. **It teaches something new.** A concept, trade-off, or failure mode not already learned.
   Reusing a known mechanism in a new domain is practice, and stays small.
3. **It fits the flow.** A stage has one central lesson and at most a few supporting ones.
   When it grows past that, split the stage or cut the item.

Framework features enter at the first stage with a real consumer, never as a tour. Beta APIs
are re-verified against the pinned version when that stage starts. An item that fails the
rule goes to the handoff backlog with the trigger that would admit it.

## Phase contract

| Phase | Goal | In scope | Out of scope |
| :--- | :--- | :--- | :--- |
| **A: domain core** | A useful vertical slice | One user job, minimal tools, typed output where something consumes it, one runnable app, a clear success condition | Generic registries or platform layers, deployment |
| **B: robust operation** | Resilient, meaningful behavior | Persistence and resume, recovery, streaming, validation and self-correction, HITL on consequential actions, domain errors | Extracting shared primitives before a second consumer exists |
| **C: composable specialist** | Safe reuse by later workflows | Explicit input/output contract, side-effect and risk declaration, failure contract, subagent or graph wrapper, domain verification (eval-lite), one small composition exercise | Full production hardening (Term E) |

## Cross-cutting threads

Every project moves each thread one step forward.

| Thread | Where it stands | How it grows |
| :--- | :--- | :--- |
| Contracts | Pydantic output schemas (P1+) | Typed inter-agent contracts (P6), capability catalog and workflow schemas (P12) |
| Observability | LangSmith tracing is already on for every run | Deliberate trace reading (P5-C), per-run tags (P6), production feedback (P8), metrics (E1) |
| Evaluation | Unit tests for deterministic code | Eval-lite scenario sets (P5-C), deterministic vs model-directed comparison (P6), regression gate (P8), datasets (E1) |
| Security | Allow-listed sandbox env, `.env` read denial ([ADR-0005](adr/0005-sandbox-secret-isolation.md)), memory write approval ([ADR-0008](adr/0008-memory-write-governance.md)) | Content guardrails (P5-B3), prompt injection through documents (P7), action permissions (P8, P11), delegated authorization (P11), tenant isolation (E3) |
| Cost and latency | Tier x provider model catalog | Measured tier and cost choices (P9), model routing (E2) |

Testing and evaluation rules: [ADR-0004](adr/0004-testing-and-evaluation-policy.md).

## Done

- **P1 Research agent:** DeepAgents orchestrator, Tavily search, structured cited report,
  model fallback, HITL before search, researcher subagent.
- **P2 RAG agent:** raw `StateGraph`, grading, corrective loop, checkpointing, streaming,
  time travel, web fallback, hallucination check, `CompiledSubAgent`, repo-insight
  coordinator with a retrieval-strategy skill.
- **P3 Code review and test generation:** three compiled subgraphs, sandboxed pytest runs,
  self-correcting test loop, `interrupt()` refactor gate, SQLite checkpoints, time travel,
  subagent adapter.
- **P4 Sandbox interpreter:** `LocalShellBackend` workspace, HITL on `execute`, artifacts,
  durable sessions, interpreter subagent with deliverable diffing, coding coordinator over
  P1/P3/P4 (first mini-workflow).
- **Stage 0 stabilization (2026-09-13):** single `agentlab` package, composition root,
  runtime-context identity, secret isolation, governance reset.

## P5: Memory-rich personal assistant (in progress)

Done: **A** (`CompositeBackend`: thread state plus per-user `/memories/` in a store,
profile loaded each turn), **B1** (skills library on `/skills/`), and **B2** (memory write
governance by operation, decided in code; read-only skills; streamed CLI approvals;
[ADR-0008](adr/0008-memory-write-governance.md)).

- **B3, content guardrails:** a **security guard** (a separate classifier model with a
  policy prompt and a structured verdict, failing closed) judges the memory writes the code
  layer lets through and routes sensitive ones to the user. One detector set for
  fixed-format secrets is applied where each risk is: redacted at the app boundary before
  input (so checkpoints, traces, and the model never see them), blocked in memory writes, and
  masked in LangSmith traces. `PIIMiddleware` isn't used here: it protects what the model
  sees, not checkpoints or tool-call arguments (verified). A deterministic output check
  enforces the Finglish rule. `memory-curation` then proposes sensitive facts instead of
  skipping them.
- **B4, memory consolidation:** hot-path vs background writes; deduplication, conflict, and
  staleness, using semantic search over the store to find related memories; how long
  threads are summarized. Changed memories keep their previous version, so the guard may let
  a correction the user asked for pass without approval.
- **C1, durable memory:** `SqliteStore` plus checkpointer, with identity end to end
  (`thread_id` x `user_id`), CLI session resolution, and user-requested deletion
  ("forget me").
- **C2, memory eval-lite:** scenarios for recall, update, conflict, cross-user isolation,
  and false "I saved it" claims, plus the security guard's accuracy, reviewed with traces.
  Includes rejection evasion: after a rejected change, the agent must not reach the same
  result through a different tool call (seen in B2: a rejected overwrite came back as two
  deleting edits).
- **C3, governed procedural memory (`skill_designer`):** the only writer to the skills
  library; other agents request instructions from it. One-off instructions pass the security
  guard. Publishing a shared skill is draft -> guard -> human approval, because it changes
  behavior for every user and future session. `SkillsMiddleware` caches the skill list per
  thread, so decide how running threads pick up a published skill.
- **C4, composition boundary:** P5 as a context provider (tool or middleware) rather than a
  chat subagent (ADR). Input protection has to travel with the agent once other workflows
  call it, so `PIIMiddleware` joins here. Mini-workflow: personalized research brief
  (P5 + P1). Then the design card update and retrospective.

## P6: Capstone I, Research-to-Decision workflow

Turn an open question into a grounded decision brief: external research, private
knowledge, optional analysis, verification, approval.

- **A:** a deterministic LangGraph parent workflow calls P1 and P2 through typed contracts,
  synthesizes, and gates delivery on approval.
- **B:** parallel research branches with fan-in (`Send`); failure handling by error class
  (retry transient errors, feed recoverable ones back to the model, pause for a human, cap
  runaway loops); source conflicts; long checkpointed runs; progress streaming, with
  approvals raised inside subagents surfaced to the app.
- **C:** deterministic vs model-directed control. The same eval set runs against the
  workflow and against a DeepAgents supervisor, each with its own evaluator-optimizer loop
  (a graph loop vs `RubricMiddleware`), and the choice is recorded in an ADR.

## P7: Document intelligence agent

Also covers visual perception (formerly P10).

- **A:** one document family, extraction into typed schemas, confidence reporting.
- **B:** multiple formats including scanned pages and images (vision models), tables and
  layout, validation loops, human review of ambiguous fields.
- **C:** multi-document reasoning with provenance (page and region) and audit-ready output,
  reusable extraction skills. Fan-out over many documents with an interpreter and dynamic
  subagents, contrasted with P6's code-decided `Send`.
- **Mini-workflow, Document Intake Cell:** P7 extraction -> P2 lookup -> validation gate ->
  P4 report.
- **New thread step:** prompt injection carried in documents, including into model-written
  orchestration code, with a red-team scenario set in the eval.

## P8: Customer support operations agent

- **A:** classify a ticket, retrieve an answer, draft a response.
- **B:** multi-intent tickets, customer context from P5, SLA and priority routing,
  escalation states, HITL for sensitive actions. Router vs handoffs (the active agent
  changes mid-conversation), compared on the same tickets.
- **C:** action permissions, ticket-system integration, audit trail, critic check. A
  production feedback loop: user feedback and annotation queues feed the regression gate,
  tested with simulated multi-turn conversations.
- **Mini-workflow (required), Support Resolution Cell:** triage -> P2 retrieval -> P1
  research fallback -> critic -> approval -> response or controlled ticket update.
  It teaches response vs side effect.

## P9: Data and SQL analytics agent

- **A:** question -> query -> result, with a table or chart.
- **B:** query validation and repair, read/write separation, sandboxed analysis through P4,
  multi-step metrics, HITL before risky queries. Measured tier and cost choices (token cost
  per question, prompt caching).
- **C:** a semantic metric layer, provenance, reusable analysis plans, anomaly explanation.
- **Mini-workflow, Analytics-to-Report Cell:** P9 analysis -> P4 artifacts -> P1 benchmark
  context -> verification.

## P10: folded into P7

Vision over scanned pages and images is P7-B. Temporal media (audio, video) is out of scope.

## P11: API and business operations agent

- **A:** read-only integration with structured responses, through one MCP server.
- **B:** action proposals, approval gates, retries and rate limits, error mapping,
  idempotency keys.
- **C:** transactional boundaries, compensation, tenant isolation, and a connector catalog
  with delegated authorization (the agent acts with the user's scoped credentials); tool
  search once the catalog outgrows the context.
- **Mini-workflow, Plan-to-Action Cell:** plan -> gather context -> P11 proposal ->
  approval -> idempotent execution -> audit record.

## P12: Capstone II, Business Operations Control Tower

A bounded control-tower workflow, not a generic super-agent. It routes a business request
across P5 context, P7 documents, P2 knowledge, P1 research, P9 analysis, P11 actions, and
P4 artifacts.

- **A:** explicit routing, typed contracts, a sequential path plus one parallel branch,
  approval before side effects.
- **B:** planner/executor separation, task dependencies, partial failure and compensation,
  persistent workflow state, per-specialist permissions, context budgets. Served through
  Agent Server: long tasks run as async subagents the user can check, steer, or cancel.
- **C:** a typed capability catalog replacing hand-written routing (the first real consumer
  of a registry, [ADR-0006](adr/0006-remove-agent-registry.md)), hierarchical orchestration
  only if the number of domains needs it, replay and audit, and a documented line between
  deterministic control and model-directed agency.

## Composition patterns

Use the simplest pattern that works. More agents do not make a better system.

| Pattern | Use when |
| :--- | :--- |
| Sequential | Steps are known and ordered |
| Routing | A request belongs to one of several specialist paths |
| Parallelization | Independent work can run concurrently, then merge |
| Orchestrator-workers | Decomposition is only knowable at runtime (needs clear worker contracts and a stop condition) |
| Evaluator-optimizer | Output can be checked against a meaningful rubric |
| Hierarchical | Multiple domains need supervisors (P12 or later) |
| Autonomous loop | The path can't be hardcoded, but progress is still verifiable |

Every new specialist gets a design card before code (template:
`docs/design_cards/README.md`).

**Deliberately out of scope:** model training and fine-tuning; temporal media and voice;
frontend engineering beyond a thin client; editor and agent-to-agent protocols (ACP, A2A)
without a cross-service consumer; LangSmith platform administration (self-hosting, BYOC,
RBAC, the LLM gateway).

## Term E (after P12)

1. **E1, production hardening and evaluation:** eval datasets, trace taxonomy, failure
   classes, idempotency, timeouts and cancellation, audit, authorization, sandbox and
   session isolation, threat modeling for excessive agency, and a red-team suite.
2. **E2, shared runtime and platform:** a common lifecycle, event model, and checkpoint,
   approval, and retry services; versioned agent, tool, and workflow registries; policy,
   model routing, and memory and artifact services. Proven by at least three workflows
   running on it.
3. **E3, distributed execution:** deployed agents behind an authenticated API, job queue and
   workers, durable run state, scheduled jobs, a policy for new input on a running thread
   (double-texting), tenant isolation, and the observability triad.
4. **E4, vertical product and adaptive systems:** one domain in depth, a thin UI over the
   event stream, and trace-driven optimization behind evaluation and promotion gates.

**Extraction rule:** one consumer, keep it local; two, extract carefully; three, formalize.

**Entry gate from Term P:**
- every specialist project (P1-P5, P7-P9, P11) complete, or waived with a rationale;
- P6 and P12 complete;
- at least three mini-workflows implemented during P7-P11;
- design cards and composition contracts for every retained specialist;
- deterministic and model-directed control compared at least once;
- an approval boundary and a side-effect boundary exercised;
- a failure replayed and analyzed;
- every shared abstraction justified by multiple consumers.

Each E stage gets planned in detail when it is reached.

## Pacing

Counted in stages, not weeks: one stage is one central lesson over a few sessions. Adjusted
together as we go.
