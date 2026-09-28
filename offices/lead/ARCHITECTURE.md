# Architecture

The system this repo is building toward, the standards every component meets, and where the
current system stands. Coding conventions and repo mechanics: [`AGENTS.md`](../../AGENTS.md).
Why each significant choice was made: [`docs/adr/`](../../docs/adr/README.md). Technology choices:
[TECH_RADAR.md](TECH_RADAR.md).

## System in one picture

```
 user / CLI (teaching harness)         later: authenticated API, UI (Term E)
        |
 app  = composition root: env, identity (UserContext), approval loop, redaction, tracing
        |
 workflow (P6, P12): deterministic control over specialists, merges, approvals
        |   specialist contract: typed envelope in, typed envelope out
 specialists: P1 research | P2 RAG | P3 code review | P4 interpreter | P5 memory
              later P7 documents | P8 support | P9 analytics | P11 business actions
        |
 infrastructure seams: model catalog + fallback | decision models | checkpointer | store |
                       vector index | sandbox | search/HTTP clients | tracing
```

## Architecture principles

Each line is the rule; its reason lives in the linked record.

1. **Layered, downward-only dependencies; apps are the composition root; nothing happens at
   import.** (`AGENTS.md` "Dependency direction"; [ADR-0002](../../docs/adr/0002-single-package-and-composition-root.md))
2. **Specialists sit behind one contract.** A typed result envelope (output, provenance, status
   `ok`/`partial`/`failed`, declared side effects, failure reason); callers never parse prose.
   Being defined in R0 ([ADR-0011](../../docs/adr/0011-return-pass-before-p6.md)).
3. **Identity is runtime context,** never a shared default.
   ([ADR-0003](../../docs/adr/0003-runtime-context-for-user-identity.md))
4. **Security by default.** Generated code never sees secrets
   ([ADR-0005](../../docs/adr/0005-sandbox-secret-isolation.md)); consequential actions wait for
   approval; one enforcement point per policy ([ADR-0010](../../docs/adr/0010-one-gate-in-memory-storage.md));
   security decisions fail closed, cosmetic repairs may fail open. A model, an LLM or a
   decider, may only tighten or escalate a security verdict, never loosen it.
5. **One writer per durable resource.** ([ADR-0012](../../docs/adr/0012-memory-consolidation-single-writer.md),
   [ADR-0013](../../docs/adr/0013-p5-completion.md))
6. **One retry layer per call, and a bounded wait on every external call.** Model calls: provider
   SDK retries plus model fallback ([ADR-0007](../../docs/adr/0007-built-in-model-fallback.md)); other
   external calls: one transient-only retry; a specialist boundary turns an external failure into
   a `failed` envelope (`AGENTS.md` convention 11).
7. **Every run is traced; personal data is masked before it leaves the process.**
8. **Framework boundaries are tested with the real framework and a scripted model; LLM
   behavior is checked with eval sets.** ([ADR-0004](../../docs/adr/0004-testing-and-evaluation-policy.md))
9. **Design load is production** ([PRINCIPLES.md](../../library/governance/principles.md#2-know-the-context-of-best-practice-asl-e-shenakht-e-context)):
   every component names its production path (design card point 16, and the seams table below).
10. **Every AI step is code, a decision model, or an LLM, or a composition of them.** A step that
    writes goes to an LLM, and code decides what it can. Every other decision point takes the
    decider first and the LLM as its escalation, held to one standard: a labeled set, accuracy
    per class, unsafe errors, latency, and cost ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md),
    [decision-models.md](../../library/engineering/decision-models.md)).

## Current system (2026-09-26)

| Part | Built as | Composed by |
| :--- | :--- | :--- |
| P1 research | DeepAgents agent, Tavily search, structured cited report, approval before search | Coding coordinator (`researcher`), `lab-brief` |
| P2 RAG | Raw `StateGraph`: retrieve, grade, rewrite, web fallback, hallucination check; Chroma index | Repo-insight coordinator (`CompiledSubAgent`) |
| P3 code review | Parent graph over three subgraphs; sandboxed pytest; `interrupt()` refactor gate | Coding coordinator |
| P4 interpreter | DeepAgents agent over `LocalShellBackend` (virtual mode, allow-listed env); artifact diff | Coding coordinator (shell without per-command approval until P6-B3) |
| P5 memory assistant | DeepAgents agent reading memory; gated store backend; background consolidator graph; skill designer graph; context-provider tool | `lab-brief` (P5 + P1) |
| Models | 6 tiers (`high`/`medium`/`low`/`opensource`/`free`/`local`), weighted ranking, fallback middleware, test-mode profiles | Every agent and node ([ADR-0014](../../docs/adr/0014-weighted-model-tier-catalog.md), [ADR-0015](../../docs/adr/0015-local-tier-and-test-mode-profiles.md)) |
| Persistence | SQLite checkpointer shared by the apps under `out/state/`; P5 has its own SQLite store and checkpointer; in-memory savers as defaults for tests | Apps |

In flight: R0 (the specialist envelope and failure contract across P1-P5). Live issues:
the mentor's [state](../mentor/STATE.md). Planned debt work: [BACKLOG.md](BACKLOG.md).

## Target system

- **End of Term P (P12):** a bounded control-tower workflow routing over typed specialist
  contracts through a capability catalog; planner/executor separation; compensation across
  specialists; long tasks as async runs on Agent Server; replay and audit.
- **Term E:** a shared runtime (lifecycle, event model, checkpoint, approval, and retry services;
  versioned registries; policy; model routing; memory and artifact services) proven by three
  workflows; distributed execution (authenticated API, queue and workers, durable run state,
  schedules, tenant isolation, metrics, logs, and traces); one vertical product with a thin UI.

## Scale seams

The production path for each seam. Lessons run the left column; designs must keep the right
column a swap, not a rewrite.

| Seam | Now | Production |
| :--- | :--- | :--- |
| Identity | `UserContext` passed by the CLI | Authenticated principal from the API, tenant in context |
| Checkpoints | `SqliteSaver`, one process | Postgres checkpointer behind the same interface; per-app databases first (R0) |
| Long-term store | `SqliteStore`, sequential connection | Postgres store; concurrent writers stay single-writer per resource |
| Vector index | Local Chroma, full rebuild | Managed vector store, incremental re-index, hybrid retrieval (R2); graph and vector combined (P7-C2) |
| Model access | Catalog, fallback middleware, tiers | Tier routing and verify-then-escalate (R2, D1), cascades at scale (P8), gateway and routing service (E2) |
| Decisions | LLM tiers with structured output; `decision_model` with Jev from R1 | A decision service: versioned question sets, shadow evaluation, per-tenant thresholds, a local backend for private state (E2) |
| Sandbox | Local shell backend, allow-listed env | Container or remote sandbox, session-scoped workspaces (E1) |
| Approvals | CLI loop over standard HITL requests | Approval service over the run's event stream (E2) |
| Execution | In-process CLI | Agent Server async runs (P12-B3); queue and workers (E3) |
| External calls | SDK defaults | Explicit timeouts, one retry layer, circuit-breaking at the platform (E1) |

## Quality ladder

Every project moves each thread one step. "Now" is the baseline all new code already meets.

| Thread | Now | Grows at |
| :--- | :--- | :--- |
| Contracts | Pydantic output schemas | Specialist envelope (R0), inter-agent contracts (P6), capability catalog (P12) |
| Reliability | Model fallback, transient-only retries | Failure contract (R0), failure classes (P6-B2), idempotency and compensation (P11, P12), timeouts and cancellation (E1) |
| Security | Secret isolation, `.env` denial, approval gates, memory gate | Content guards everywhere (R5), injection through documents (P7), action permissions (P8, P11), delegated authorization (P11), tenant isolation (E3) |
| Observability | LangSmith tracing on every run, P5 trace masking | Masking in every app (R5), per-run tags (P6), production feedback (P8), metrics (E1) |
| Evaluation | Unit tests at boundaries; P5 eval-lite | Shared eval harness (R0), retrieval metrics (R2), control comparison (P6), regression gate (P8), datasets (E1) |
| Cost and latency | Tier catalog with weighted ranking | Decider-first decision points (R1), tier routing (R2, D1), cascades at scale (P8-C3), measured cost per question (P9), routing service (E2) |
| Decisions | Typed structured output from LLM tiers; no labeled sets | The seam and the claim check (R1), graders and tiers measured (R2), guard and memory decisions (P5 pass), the workbench (D1), decided branches (P6), schema choice and field verification (P7), the cascade at scale (P8-C3), a decision service (E2) |
| Delivery | CI on every push (lint, format, tests, docs lint); Dependabot; the latest stable stack ([dependency policy](../../library/engineering/dependency-policy.md)) | Eval regression gate in CI (P8-C2), deployment pipeline (E3) |

## Composition patterns

Use the simplest pattern that works; more agents don't make a better system.

| Pattern | Use when |
| :--- | :--- |
| Sequential | Steps are known and ordered |
| Routing | A request belongs to one of several specialist paths |
| Cascade | A cheap decider answers when confident and escalates otherwise (asymmetric on security). "Cascade" always means this upward escalation; failing over to another provider is a fallback |
| Generate, then decide | An LLM drafts candidates, a decider judges them, code picks or escalates (best of N; draft, verify, escalate) |
| Parallelization | Independent work can run concurrently, then merge |
| Orchestrator-workers | Decomposition is only knowable at runtime (needs worker contracts and a stop condition) |
| Evaluator-optimizer | Output can be checked against a meaningful rubric |
| Hierarchical | Several domains need their own supervisors (P12 or later) |
| Autonomous loop | The path can't be hard-coded, but progress is still verifiable |
