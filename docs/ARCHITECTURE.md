# Architecture

The system this repo is building toward, where the current system stands, and how each quality
thread grows. The standards every component meets (the architecture principles, the four-scale
Wave-Particle Duality model, the scale seams, the composition patterns) are in the library:
[architecture standards](../library/architecture/standards.md). Coding conventions and repo
mechanics: [`AGENTS.md`](../AGENTS.md). Why each significant choice was made:
[`docs/adr/`](adr/README.md). Technology choices: the
[radar](../library/technology/radar.md).

## System in one picture (4-Scale Wave-Particle Duality, [ADR-0033](adr/0033-wave-particle-duality-and-workflow-specialist-layer.md))

```text
 user / CLI (teaching harness)          later: authenticated API, UI (Term E)
        |
 app (`apps/*_app.py`) = composition root: env, identity (`UserContext`), approval loop, redaction, tracing
        |
 Rung 3 — Macro / Enterprise Scale:
   Particle: Coordinators (`agents/coordinators/*`) — DeepAgents supervisors delegating to Specialists
   Wave:     Operations (`workflows/*_workflow.py`) — Macro-workflows (`Control Tower`) over Workflows
        |
 Rung 2 — Domain / Project Scale (Two Faces of One Coin per Project P1-P5+):
   Particle face: `Specialist[TInput, TReport]` (`as_subagent`, `as_tool`, typed metadata)
   Wave face:     `Workflow` (`run_<project>` in `workflows/<project>_workflow.py`) -> `SpecialistResult[TReport]`
   Reports:       P1 `ResearchReport` | P2 `RagReport` | P3 `CodeReviewReport` | P4 `InterpreterReport` | P5 `PersonalContextReport`
        |
 Rung 1 — Atomic / Unit Scale:
   Particle: `Agent` (`agents/*_agent.py`) — Homogeneous Hot Loop over `AgentState` (`messages` + `AgentMiddleware` + `Tools`)
   Wave:     `Graph` (`graphs/*_graph.py` + `nodes/*_node.py`) — Heterogeneous Stations over multi-field typed `State`
        |
 Rung 0 — Subatomic Primitives & Repo-Wide Cross-Cutting Infrastructure:
   `LLM / Decision Model (Jev)` | `Prompt` | `Tool (@tool / MCP)` | `AgentMiddleware` |
   `Memory / Store` | `Backend / Sandbox` | `Security / Redaction` | `UserContext` | `Checkpointer`
```

## Current system (2026-10-12)

| Part | Built as | Wave/Particle Density & Composition |
| :--- | :--- | :--- |
| P1 research | Research workflow & specialist (`ResearchReport`): plan, `Jev` source router, `Send` fan-out to `create_agent` per sub-question (`SourceRouteMiddleware`, `EvidenceStopMiddleware`), claim check | Balanced 50/50 Wave-Particle hybrid; composed by coding coordinator (`researcher`) and `lab-brief` |
| P2 RAG | RAG workflow & specialist (`RagReport`, transitioning from `str` in Phases 1-3): `StateGraph` over retrieve, grade, rewrite, web fallback, hallucination check; Chroma index | High Wave (`Graph`-dominant); composed by repo-insight coordinator |
| P3 code review | Code review workflow & specialist (`CodeReviewReport`): parent graph over three subgraphs; sandboxed pytest; `interrupt()` refactor gate | High Wave (`Graph`-dominant); composed by coding coordinator |
| P4 interpreter | Interpreter workflow & specialist (`InterpreterReport`, transitioning from `str` in Phases 1-3): DeepAgents agent over `LocalShellBackend` (virtual mode, allow-listed env); deliverable diff | High Particle (`Agent`-dominant); composed by coding coordinator |
| P5 personal context & assistant | Personal context workflow & specialist (`PersonalContextReport`, transitioning from `dict[str, str]` in Phases 1-3) + interactive `lab-assistant` app (background consolidator graph, skill designer graph) | Hybrid; memory, gated store, and redaction are Rung-0 repo-wide infrastructure ([ADR-0033](adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)) |
| Coordinators | `agents/coordinators/`: the coding coordinator (P1, P3, P4) and the repo-insight coordinator (P2), both `create_deep_agent` | Rung-3 Particle supervisors ([ADR-0030](adr/0030-role-agents-coordinators-and-subagent-versions.md)) |
| Specialist & Workflow contract | `Specialist[TInput, TReport]` and `SpecialistResult[TReport]`, `workflows/*_workflow.py` (`run_*`), thin `subagents/*_subagent.py` adapters, `failure_util`, timeouts, eval-lite harness | Every specialist and every caller ([ADR-0026](adr/0026-the-specialist-contract.md), [ADR-0033](adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)) |
| Decisions | `decision_model` seam (Jev direct, `jev-1.13.0`), `model_router` (`ADR-0031`), `DecisionRecord` per decision; active in R1 (`research_sources@1`, `evidence_enough@1`, `claim_check@1`) | Rung-0 primitive across R1 onward ([ADR-0021](adr/0021-decision-models-as-a-second-model-family.md), [ADR-0031](adr/0031-jev-model-router-and-test-mode-ladder.md)) |
| Models | 6 tiers (`high`/`medium`/`low`/`opensource`/`free`/`local`), weighted ranking, fallback middleware, test-mode ladder (`default`, `strong`, `strongest`) | Every agent and node ([ADR-0014](adr/0014-weighted-model-tier-catalog.md), [ADR-0015](adr/0015-local-tier-and-test-mode-profiles.md), [ADR-0031](adr/0031-jev-model-router-and-test-mode-ladder.md)) |
| Persistence | One SQLite checkpointer database per app under `out/state/` (`<app>_checkpoints.db`), `delegations` DB for delegated runs, and Rung-0 SQLite long-term store; in-memory savers as defaults for tests | Rung-0 infrastructure wired by `apps/` |

In flight: Phases 1-3 architectural adaptation (unifying `*Report` schemas, creating `src/agentlab/workflows/`, and promoting Rung-0 infrastructure) in a dedicated session, followed by R2-R5 teaching in separate `/mentor` sessions. Live state: [STATE.md](../mentor/STATE.md). Planned debt work: [BACKLOG.md](../mentor/BACKLOG.md).

## Target system

- **End of Term P (P14):** a bounded control-tower operation (`workflows/`) routing over typed
  `Specialist[TInput, TReport]` contracts through a capability catalog; planner/executor
  separation; compensation across specialists; long tasks as async runs on Agent Server; replay
  and audit.
- **Term E:** a shared runtime (lifecycle, event model, checkpoint, approval, and retry services;
  versioned registries; policy; model routing; memory and artifact services) proven by three
  workflows; distributed execution (authenticated API, queue and workers, durable run state,
  schedules, tenant isolation, metrics, logs, and traces); one vertical product with a thin UI.

## Quality ladder

Every project moves each thread one step. "Now" is the baseline all new code already meets.

| Thread | Now | Grows at |
| :--- | :--- | :--- |
| Contracts | Pydantic `*Report` output schemas, `Specialist[TInput, TReport]`, `SpecialistResult[TReport]` (R0 + ADR-0033) | Inter-specialist macro-workflows (P6, P7), capability catalog (P14) |
| Reliability | Model fallback, transient-only retries, `failure_util` failure contract | Failure classes (P7-B2), idempotency and compensation (P12, P14), timeouts and cancellation (E1) |
| Security | Secret isolation, `.env` denial, approval gates, Rung-0 memory gate and redaction | Content guards everywhere (R5), injection through documents (P8), action permissions (P9, P12), delegated authorization (P12), tenant isolation (E3) |
| Observability | LangSmith tracing on every run, trace masking | Masking in every app (Phases 1-3 / R5), per-run tags (P6, P7), production feedback (P9), metrics (E1) |
| Evaluation | Unit tests at boundaries; P5 eval-lite; shared eval harness (R0) | Retrieval metrics (R2), control comparison (P7), regression gate (P9), datasets (E1) |
| Cost and latency | Tier catalog with weighted ranking, Jev decider-first points (R1) and model router | Tier routing (R2, D1), cascades at scale (P9-C3), measured cost per question (P10), routing service (E2) |
| Decisions | Typed structured output from LLM tiers; `decision_model` seam and R1 claim/source/stop decisions | Graders and tiers measured (R2), AST+decider review labels (R3), guard and memory decisions (P5 pass), the workbench (D1), decided branches (P6, P7), schema choice and field verification (P8), the cascade at scale (P9-C3), a decision service (E2) |
| Delivery | CI on every push (lint, format, mypy, pytest, docs lint); Dependabot; the latest stable stack ([dependency policy](../library/engineering/dependency-policy.md)) | Eval regression gate in CI (P9-C2), deployment pipeline (E3) |

