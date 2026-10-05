# Architecture

The system this repo is building toward, where the current system stands, and how each quality
thread grows. The standards every component meets (the architecture principles, the scale
seams, the composition patterns) are in the library:
[architecture standards](../library/architecture/standards.md). Coding conventions and repo
mechanics: [`AGENTS.md`](../AGENTS.md). Why each significant choice was made:
[`docs/adr/`](adr/README.md). Technology choices: the
[radar](../library/technology/radar.md).

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

## Current system (2026-10-05)

| Part | Built as | Composed by |
| :--- | :--- | :--- |
| P1 research | DeepAgents agent, Tavily search, structured cited report, approval before search | Coding coordinator (`researcher`), `lab-brief` |
| P2 RAG | Raw `StateGraph`: retrieve, grade, rewrite, web fallback, hallucination check; Chroma index | Repo-insight coordinator (`CompiledSubAgent`) |
| P3 code review | Parent graph over three subgraphs; sandboxed pytest; `interrupt()` refactor gate | Coding coordinator |
| P4 interpreter | DeepAgents agent over `LocalShellBackend` (virtual mode, allow-listed env); artifact diff | Coding coordinator (shell without per-command approval until P6-B3) |
| P5 memory assistant | DeepAgents agent reading memory; gated store backend; background consolidator graph; skill designer graph; context-provider tool | `lab-brief` (P5 + P1) |
| Specialist contract | `SpecialistResult[T]` envelope, a `run_*` boundary per specialist (P1-P4), the failure contract (`failure_util`), timeouts on every external client, the eval-lite harness | Every specialist and every caller ([ADR-0026](adr/0026-the-specialist-contract.md)) |
| Decisions | `decision_model` seam (Jev direct, `jev-1.13.0`), one `DecisionRecord` per decision; no consumer yet (the claim check is R1's) | R1 onward ([ADR-0021](adr/0021-decision-models-as-a-second-model-family.md)) |
| Models | 6 tiers (`high`/`medium`/`low`/`opensource`/`free`/`local`), weighted ranking, fallback middleware, test-mode profiles | Every agent and node ([ADR-0014](adr/0014-weighted-model-tier-catalog.md), [ADR-0015](adr/0015-local-tier-and-test-mode-profiles.md)) |
| Persistence | One SQLite checkpointer database per app under `out/state/` (`<app>_checkpoints.db`), and a `delegations` one for delegated runs; P5 has its own SQLite store and checkpointer; in-memory savers as defaults for tests | Apps |

In flight: R1 (P1, a stronger researcher; topics 1-2 built). Live issues:
the mentor's [state](../mentor/STATE.md). Planned debt work: [BACKLOG.md](../mentor/BACKLOG.md).

## Target system

- **End of Term P (P12):** a bounded control-tower workflow routing over typed specialist
  contracts through a capability catalog; planner/executor separation; compensation across
  specialists; long tasks as async runs on Agent Server; replay and audit.
- **Term E:** a shared runtime (lifecycle, event model, checkpoint, approval, and retry services;
  versioned registries; policy; model routing; memory and artifact services) proven by three
  workflows; distributed execution (authenticated API, queue and workers, durable run state,
  schedules, tenant isolation, metrics, logs, and traces); one vertical product with a thin UI.

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
| Delivery | CI on every push (lint, format, tests, docs lint); Dependabot; the latest stable stack ([dependency policy](../library/engineering/dependency-policy.md)) | Eval regression gate in CI (P8-C2), deployment pipeline (E3) |

