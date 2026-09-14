# Curriculum Roadmap (v3)

Adopted 2026-09-13. Replaces the original 6-project roadmap and Roadmap v2. Both are
still readable in git history (`git show 85f714d:docs/ROADMAP.md`,
`git show "85f714d:docs/Agentic AI Curriculum Roadmap v2.md"`). Live status lives in
`docs/MENTOR_HANDOFF.md`.

## Shape

- **Term P:** 12 projects. P1-P5 and P7-P11 build specialists; **P6** and **P12** are
  capstones that compose them. Small composition exercises ("mini-workflows") recur
  throughout, instead of waiting for the end.
- **Term E:** productization and scale, which starts only after P12.
- Every project has three phases. There is no fourth "hardening" phase
  ([ADR-0001](adr/0001-three-phase-project-model.md)).

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
| Contracts | Pydantic output schemas (P1+) | Typed inter-agent contracts (P6), workflow schemas (P12) |
| Observability | LangSmith tracing is already on for every run | Deliberate trace reading (P5-C), per-run tags (P6), metrics (E1) |
| Evaluation | Unit tests for deterministic code | Eval-lite scenario sets (P5-C), routing/synthesis evals (P6), regression gate and production feedback loop (P8), datasets (E1) |
| Security | Allow-listed sandbox env, `.env` read denial ([ADR-0005](adr/0005-sandbox-secret-isolation.md)), memory write approval ([ADR-0008](adr/0008-memory-write-governance.md)) | Content guardrails (P5-B3), prompt injection through documents (P7), action permissions (P8, P11), delegated authorization (P11), red-teaming (E1), tenant isolation (E5) |
| Cost and latency | Tier x provider model catalog | Measured tier choices (P9), model routing (E3) |

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
profile loaded each turn) and **B1** (skills library on `/skills/`).

- **B2, memory write governance (deterministic layer):** conditional HITL by operation type,
  decided in code through an HITL `when` predicate: adding a new fact is free; overwriting,
  destructively editing, or deleting a stored memory needs approval. `/skills/` is read-only
  for the assistant. CLI approval loop that works with streaming. Replace the placeholder
  coding skills with assistant-domain skills.
- **B3, content guardrail:** built-in `PIIMiddleware` for fixed-format data (block, redact,
  mask, or hash; input, output, tool results, and what reaches LangSmith traces), plus a
  **security guard**: a separate
  classifier model (engineered policy prompt, structured verdict) that judges additive
  memory writes by content and triggers HITL when a write is sensitive. Runs after the code
  layer, fails closed. Also a deterministic output check for the Finglish rule (the model
  leaks Perso-Arabic script into long replies). With the guard in place, `memory-curation`
  stops telling the model to skip sensitive facts: relevant ones get proposed and the guard
  routes them to the user for approval.
- **B4, memory consolidation:** hot-path vs background writes; deduplication, conflict,
  and staleness policy, using semantic search over the store to find related memories.
  Context growth in long threads (summarization and context-editing middleware).
- **C1, durable memory:** `SqliteStore` plus checkpointer, with identity end to end
  (`thread_id` x `user_id`), including CLI session resolution. User-controlled data
  lifecycle: export and "forget me" deletion.
- **C2, memory eval-lite:** scenarios for recall, update, conflict, cross-user isolation,
  and false "I saved it" claims, plus the security guard's accuracy, reviewed with traces.
  Include rejection evasion: after a rejected change, the agent must not reach the same
  result through a different tool call (seen in B2 exploration: a rejected overwrite came
  back as two deleting edits).
- **C3, governed procedural memory (`skill_designer`):** a specialist that is the only writer
  to the skills library. Other agents request instructions from it. One-off instructions for
  a single task pass the security guard. Publishing to the shared library (new or improved
  skills) is draft -> guard -> human approval, because a shared skill changes behavior for
  every user and every future session. `SkillsMiddleware` loads the skill list once per
  thread and keeps it in state, so a published skill only reaches new threads; decide how
  running threads pick it up.
- **C4, one controlled MCP integration:** reads by default, writes need approval.
- **C5, composition boundary:** P5 as a context provider (tool or middleware) rather than a
  chat subagent (ADR). Mini-workflow: personalized research brief (P5 + P1). Then the
  design card update and retrospective.

## P6: Capstone I, Research-to-Decision workflow

Turn an open question into a grounded decision brief: external research, private
knowledge, optional analysis, verification, approval.

- **A:** a deterministic LangGraph parent workflow calls P1 and P2 through typed contracts,
  synthesizes, and gates delivery on approval.
- **B:** parallel branches (`Send` fan-out; fan-in through a reducer or a deferred node),
  partial-failure recovery (node `RetryPolicy`; tool and model retry, tool-error, and
  call-limit middleware against runaway loops), source-conflict handling, checkpointed long
  runs and durability modes, progress streaming with `stream_events(version="v3")` subagent
  projections, and approvals raised inside subagents surfaced to the top-level app.
- **C:** an evaluator-optimizer loop (a graph loop in the workflow, `RubricMiddleware` on
  the supervisor); the same eval set run against the deterministic
  workflow and against a DeepAgents supervisor, with the choice recorded in an ADR; a typed
  capability catalog for selecting specialists (the first real consumer of a registry,
  [ADR-0006](adr/0006-remove-agent-registry.md)); local serving through Agent Server plus
  the SDK client, with async subagents (launch, check, steer, cancel) for long research runs.

## P7: Document intelligence agent

- **A:** one document family, extraction into typed schemas, confidence reporting.
- **B:** multiple formats, tables and layout, validation loops, human review of ambiguous
  fields, document comparison.
- **C:** provenance and lineage, multi-document reasoning, reusable extraction skills,
  audit-ready output. Fan-out over many documents with an interpreter and dynamic subagents,
  contrasted with P6's code-decided `Send`; model-written code becomes an injection surface.
- **Mini-workflow, Document Intake Cell:** P7 extraction -> P2 lookup -> validation gate ->
  P4 report.
- **New thread step:** prompt injection carried in documents, with a red-team scenario set
  in its eval.

## P8: Customer support operations agent

- **A:** classify a ticket, retrieve an answer, draft a response.
- **B:** multi-intent tickets, customer context from P5, SLA and priority routing,
  escalation states, HITL for sensitive actions. Router vs handoffs (the active agent
  changes mid-conversation), compared on the same tickets.
- **C:** action permissions, ticket-system integration, audit trail, critic check. A
  production feedback loop: user feedback and annotation queues feed the regression set,
  plus online evaluators and simulated multi-turn conversations.
- **Mini-workflow (required), Support Resolution Cell:** triage -> P2 retrieval -> P1
  research fallback -> critic -> approval -> response or controlled ticket update.
  It teaches response vs side effect.

## P9: Data and SQL analytics agent

- **A:** question -> query -> result, with a table or chart.
- **B:** query validation and repair, read/write separation, sandboxed analysis through P4,
  multi-step metrics, HITL before risky queries. Measured tier choices (cost tracking, prompt caching), with harness profiles
  for model-specific tuning; programmatic tool calling to aggregate results outside the
  context.
- **C:** a semantic metric layer, provenance, reusable analysis plans, anomaly explanation.
- **Mini-workflow, Analytics-to-Report Cell:** P9 analysis -> P4 artifacts -> P1 benchmark
  context -> verification.

## P10: Multimodal perception agent

Builds on P7's document pipeline instead of duplicating it.

- **A:** one non-text modality plus text context.
- **B:** multiple modalities, preprocessing, uncertainty, cross-modal evidence links, HITL on
  ambiguous perception.
- **C:** temporal media, provenance (pages, regions, timestamps), reusable perception
  subagents.
- **Mini-workflow, Multimodal Evidence Cell:** P10 -> P7 -> P2 -> verification -> P4 report.

## P11: API and business operations agent

- **A:** read-only API integration with structured responses.
- **B:** action proposals, approval gates, retries and rate limits, error mapping,
  idempotency keys. The Functional API (`@entrypoint`, `@task`), so completed side effects
  are not re-run on resume; emulated tools for testing actions.
- **C:** transactional boundaries, compensation, tenant isolation, connector catalog.
  Delegated authorization (the agent acts with the user's scoped credentials, MCP auth
  included); tool selection or tool search once the catalog outgrows the context.
- **Mini-workflow, Plan-to-Action Cell:** plan -> gather context -> P11 proposal ->
  approval -> idempotent execution -> audit record.

## P12: Capstone II, Business Operations Control Tower

A bounded control-tower workflow, not a generic super-agent. It routes a business request
across P5 context, P7 documents, P2 knowledge, P1 research, P9 analysis, P10 perception,
P11 actions, and P4 artifacts.

- **A:** explicit routing, typed contracts, a sequential path plus one parallel branch,
  approval before side effects.
- **B:** planner/executor separation, task dependencies, partial failure and compensation,
  intermediate evaluation, persistent workflow state, progress streaming, per-specialist
  permissions, context budgets.
- **C:** hierarchical orchestration, capability discovery, evaluator-optimizer, replay and
  audit, workflow variants on the same specialists, multi-user isolation, and a documented
  line between deterministic control and model-directed agency.

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

**Framework features.** A LangChain, LangGraph, or DeepAgents feature enters the curriculum
at the first stage that has a real consumer for it, not as a tour. Beta APIs (interpreters,
dynamic subagents, `RubricMiddleware`, harness profiles) are verified against the pinned
version when that stage starts, and the stage notes what replaces them if the API changes.
Coverage was checked against the LangChain, LangGraph, DeepAgents, and LangSmith docs on
2026-09-14.

**Deliberately out of scope:** model training and fine-tuning, frontend engineering beyond a
thin client, editor integration (ACP), voice agents (optional in P10), and LangSmith platform
administration (self-hosting, BYOC, RBAC, the LLM gateway).

## Term E (after P12)

1. **E1, production hardening and evaluation:** eval datasets, trace taxonomy, failure
   classes, idempotency, timeouts and cancellation, audit, authorization, sandbox and
   session isolation; threat modeling for excessive agency and a red-team suite.
2. **E2, shared workflow runtime:** a common lifecycle, event model, checkpoint, approval,
   and retry services, proven by two real workflows.
3. **E3, agent application platform:** versioned agent, tool, and workflow registries;
   policy; model routing; memory and artifact services.
4. **E4, multi-workflow portfolio:** at least three workflows on the platform, as an
   architecture fitness test.
5. **E5, distributed execution:** API boundary, job queue and workers, durable run state,
   tenant isolation, observability triad; Agent Server background runs, cron jobs,
   double-texting policy, custom auth, `RemoteGraph`, and A2A between services.
6. **E6, vertical product and adaptive systems:** one domain in depth; trace-driven
   optimization behind evaluation and promotion gates; a thin UI over the event stream.

**Extraction rule:** one consumer, keep it local; two, extract carefully; three, formalize.

**Entry gate from Term P:**
- at least 10 specialist roles built (or waived with a rationale);
- P6 and P12 complete;
- at least three mini-workflows implemented during P7-P11;
- design cards and composition contracts for every retained specialist;
- deterministic and model-directed control compared at least once;
- an approval boundary and a side-effect boundary exercised;
- a failure replayed and analyzed;
- every shared abstraction justified by multiple consumers.

Each E stage gets planned in detail when it is reached.

## Pacing

Default: 1-2 weeks per project. Adjusted together as we go.
