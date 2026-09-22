# Curriculum Roadmap (v3)

Adopted 2026-09-13, refined 2026-09-14 ([ADR-0009](adr/0009-stage-admission-rule.md)) and
2026-09-22 (return pass and difficulty curve, [ADR-0011](adr/0011-return-pass-before-p6.md)). Replaces
the original 6-project roadmap and Roadmap v2. Both are still readable in git history
(`git show 85f714d:docs/ROADMAP.md`,
`git show "85f714d:docs/Agentic AI Curriculum Roadmap v2.md"`). Live status lives in
`docs/MENTOR_HANDOFF.md`.

## Shape

- **Term P:** 11 projects. P1-P5, P7-P9, and P11 build specialists; **P6** and **P12** are
  capstones that compose them. P10 (multimodal perception) was folded into P7; project
  numbers stay stable so ADRs and history keep their meaning. Small composition exercises
  ("mini-workflows") recur throughout, instead of waiting for the end.
- **Return pass (R0-R5):** after P5 and before P6, P1-P5 are brought to one specialist
  contract, and each gets one real upgrade.
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

## Difficulty curve

The level rises only at project boundaries, never mid-project. Within a stage there is at
most one hard new concept (a stage that needs two is split), and a steep stage is followed
by a lighter one that practices it.

| Level | What gets hard | Where |
| :--- | :--- | :--- |
| L1 | One agent with tools and structured output | P1 |
| L2 | Explicit graphs: state, loops, checkpoints, streaming | P2 |
| L3 | Composed subgraphs, sandboxes, approval gates, subagent adapters | P3, P4 |
| L4 | Governance, memory, guards, background work, contracts | P5, return pass |
| L5 | Multi-specialist workflows: parallelism, failure classes, eval-driven choices | P6-P9 |
| L6 | Actions with side effects: authorization, catalogs, compensation, hierarchy | P11, P12 |
| L7 | Production platform: runtime services, distribution, tenancy | Term E |

The return pass is L4 practice: known techniques applied to earlier code, plus one new
concept per stage.

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

## Order from here

P5 is paused after B4 topic 1 (2026-09-22). The return pass runs first, then P5 resumes and
is finished against the specialist contract, then R5 closes the pass with every specialist,
P5 included:

**R0-R4 -> P5 (rest of B4, C1-C4) -> R5 -> P6 -> P7 -> P8 -> P9 -> P11 -> P12 -> Term E**

Stages are planned below with the one hard concept each one teaches. They are re-cut at each
phase start when the build shows a better split; the difficulty rules above still apply.

## P5: Memory-rich personal assistant (paused after B4 topic 1)

Done: **A** (`CompositeBackend`: thread state plus per-user `/memories/` in a store,
profile loaded each turn), **B1** (skills library on `/skills/`), **B2** (memory write
governance by operation, [ADR-0008](adr/0008-memory-write-governance.md)), **B3** (content
guardrails: one gate in the memory storage, security guard, secret detectors, Finglish repair,
[ADR-0010](adr/0010-one-gate-in-memory-storage.md)), and **B4 topic 1** (the assistant only
reads memory; a background consolidator proposes line-level edits applied one per graph step,
[ADR-0012](adr/0012-memory-consolidation-single-writer.md)). No semantic search: the profile
and its goal index are in the prompt every turn (trigger in the handoff backlog).

Remaining, after R4:
- **B4, rest:** topic 1's tests-and-demo step (a live `lab-assistant` run); **previous
  versions** of changed lines, so the guard may let a correction the user asked for pass
  without approval; **rejected edits remembered**, so the consolidator doesn't propose the
  same change after every conversation; **long threads**: what summarization does to a thread
  and what must survive it.
- **C1, durable memory:** `SqliteStore` plus checkpointer, with identity end to end
  (`thread_id` x `user_id`), durable proposals awaiting review, CLI session resolution, and
  user-requested deletion ("forget me").
- **C2, memory eval-lite:** recall, update, conflict, cross-user isolation, false "I saved it"
  claims, the security guard's accuracy, and the consolidator's edits (missed conflicts,
  invented facts, re-proposed rejections), reviewed with traces. Built on R0's harness.
- **C3, governed procedural memory (`skill_designer`):** the only writer to the skills
  library; other agents request instructions from it. Publishing a shared skill is draft ->
  guard -> human approval. `SkillsMiddleware` caches the skill list per thread, so decide how
  running threads pick up a published skill.
- **C4, composition boundary:** P5 as a context provider (tool or middleware) that meets the
  specialist contract. Input protection has to travel with the agent once other workflows call
  it, so `PIIMiddleware` joins here. Mini-workflow: personalized research brief (P5 plus the
  upgraded P1). Then the design card update and retrospective.

## Return pass (R0-R5), before P6

P1-P5 were built at rising levels and share no contract (audit 2026-09-22,
[ADR-0011](adr/0011-return-pass-before-p6.md)). The pass brings every specialist to one
baseline before P6 composes them. Conformance work is done by the mentor directly; each
stage's lesson is its upgrade. No rewrites unless a project can't meet the contract. Every
stage ends with a before/after demo of the same scenario.

**Specialist contract** (defined in R0 from P6's needs, checked in every R stage):
a typed result envelope (output, provenance, status: ok / partial / failed, declared side
effects); `UserContext` wherever user data is touched; one approval path (the standard HITL
request, streamed by the app); secret redaction at the app boundary and trace masking in
every app; a design card; an eval-lite smoke set of 5-10 scenarios.

| Stage | Hard concept | Also lands (mentor-direct) |
| :--- | :--- | :--- |
| **R0, the specialist contract** | What a caller must know about a specialist: result envelope, provenance, status, declared side effects, and the failure contract (what "partial" means, who retries) | Shared eval-lite harness (first consumer: R1); design cards for P1-P4; chat prompts split from worker prompts; per-app checkpoint databases |
| **R1, P1 evidence-grounded research** | Claim-level provenance: read the pages instead of snippets, map every claim to its supporting source, confidence computed from source agreement | The unused groundedness middleware wired in; a search budget replaces approving every search |
| **R2, P2 retrieval you can measure** | Retrieval evaluation: a small labeled question set and hit rate at k, so changes are judged by numbers | Incremental re-index with stale-source detection; batch grading; ungrounded answers rerouted instead of a disclaimer |
| **R3, P3 hybrid analysis** | Deterministic tools first, model second: ruff and AST findings feed the review, and the model explains instead of hunting | Diff and multi-file input |
| **R4, P4 side effects as contract** | Declared side effects: the artifact diff becomes part of the result, so a caller knows what changed on disk | A light stage by design, after R1-R3 |
| **R5, close** | None new: practice | One CLI approval loop; secret redaction and trace masking in every app; dead code removed; study guides for P1 and P2; every specialist, P5 included, run on one scenario. P6 Session 0 starts from here |

## P6: Capstone I, Research-to-Decision workflow (L5)

Turn an open question into a grounded decision brief: external research, private
knowledge, optional analysis, verification, approval.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | A deterministic parent workflow over specialists: P1 and P2 called through the specialist contract, synthesis, delivery gated on approval |
| **B1** | Fan-out and fan-in: parallel research branches with `Send`, merged by a reducer; source conflicts surface in the synthesis |
| **B2** | Failure by error class: retry transient errors, feed recoverable ones back to the model, pause for a human, cap runaway loops |
| **B3** | Nested runs: approvals raised inside subagents surfaced to the app, progress streamed across namespaces, long checkpointed runs resumed |
| **C1** | Deterministic vs model-directed control: the same eval set against the workflow and a DeepAgents supervisor |
| **C2** | Evaluator-optimizer: a graph loop vs `RubricMiddleware`, and the control choice recorded in an ADR |

## P7: Document intelligence agent (L5)

Also covers visual perception (formerly P10).

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Extraction into typed schemas for one document family, with per-field confidence |
| **B1** | Vision: scanned pages and images, tables and layout |
| **B2** | Validation loops, and human review of ambiguous fields only |
| **C1** | Multi-document reasoning with provenance (page and region) and audit-ready output; reusable extraction skills |
| **C2** | Model-decided fan-out: an interpreter and dynamic subagents over many documents, contrasted with P6's code-decided `Send` |
| **C3** | Prompt injection carried in documents, including into model-written orchestration code, with a red-team scenario set |
| **C4** | Mini-workflow, Document Intake Cell: P7 extraction -> P2 lookup -> validation gate -> P4 report (practice) |

## P8: Customer support operations agent (L5)

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Classify a ticket, retrieve an answer, draft a response |
| **B1** | Multi-intent tickets with customer context from P5, SLA and priority routing |
| **B2** | Router vs handoffs (the active agent changes mid-conversation), compared on the same tickets |
| **B3** | Escalation states and HITL for sensitive actions |
| **C1** | Action permissions, ticket-system integration, audit trail, critic check |
| **C2** | A production feedback loop: user feedback and annotation queues feed a regression gate, tested with simulated multi-turn conversations |
| **C3** | Mini-workflow (required), Support Resolution Cell: triage -> P2 -> P1 fallback -> critic -> approval -> response or controlled ticket update. It teaches response vs side effect |

## P9: Data and SQL analytics agent (L5)

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Question -> query -> result, with a table or chart |
| **B1** | Query validation and repair, read/write separation, HITL before risky queries |
| **B2** | Sandboxed multi-step analysis through P4, with measured tier and cost choices (token cost per question, prompt caching) |
| **C1** | A semantic metric layer with provenance |
| **C2** | Reusable analysis plans and anomaly explanation |
| **C3** | Mini-workflow, Analytics-to-Report Cell: P9 analysis -> P4 artifacts -> P1 benchmark context -> verification (practice) |

## P10: folded into P7

Vision over scanned pages and images is P7-B1. Temporal media (audio, video) is out of scope.

## P11: API and business operations agent (L6)

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

A bounded control-tower workflow, not a generic super-agent. It routes a business request
across P5 context, P7 documents, P2 knowledge, P1 research, P9 analysis, P11 actions, and
P4 artifacts.

| Stage | Hard concept |
| :--- | :--- |
| **A1** | Explicit routing over typed contracts: a sequential path plus one parallel branch, approval before side effects |
| **B1** | Planner/executor separation with task dependencies |
| **B2** | Partial failure and compensation across specialists, persistent workflow state, per-specialist permissions, context budgets |
| **B3** | Served through Agent Server: long tasks as async subagents the user can check, steer, or cancel |
| **C1** | A typed capability catalog replacing hand-written routing (the first real consumer of a registry, [ADR-0006](adr/0006-remove-agent-registry.md)); hierarchical orchestration only if the number of domains needs it |
| **C2** | Replay and audit, and a documented line between deterministic control and model-directed agency |

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
- the return pass (R0-R5) complete;
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
