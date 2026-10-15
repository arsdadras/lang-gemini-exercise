---
title: Architecture standards
maintainer: mentor
status: current
updated: 2026-10-12
summary: The principles every component meets, the 4-scale Wave-Particle Duality model, the scale seams, and the composition patterns.
related: [decision-models.md, ../../docs/ARCHITECTURE.md, ../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md, ../governance/principles.md]
---

# Architecture Standards

The rules every design and every change meets. Where the system stands and where it is going
(the system picture, the current and target system, the quality ladder) is
[ARCHITECTURE.md](../../docs/ARCHITECTURE.md). Decision points follow
[decision-models.md](decision-models.md); coding conventions are in
[`AGENTS.md`](../../AGENTS.md).

## Architecture principles

Each line is the rule; its reason lives in the linked record.

1. **Layered, downward-only dependencies; `apps/` are the composition root; `workflows/` sit
   above `agents/` and `graphs/`; nothing happens at import.** (`AGENTS.md` "Dependency direction";
   [ADR-0002](../../docs/adr/0002-single-package-and-composition-root.md),
   [ADR-0033](../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md))
2. **Every domain project (P1-P5+) produces a two-sided `Specialist / Workflow` coin with a rich
   Pydantic `*Report`.** `run_<project>` in `workflows/<project>_workflow.py` returns
   `SpecialistResult[TReport]` (output, provenance, status `ok`/`partial`/`failed`, declared side
   effects, failure reason), where `TReport` is always a structured Pydantic model (`ResearchReport`,
   `RagReport`, `CodeReviewReport`, `InterpreterReport`, `PersonalContextReport`)—never a raw `str`
   or `dict`. Callers never parse prose ([ADR-0026](../../docs/adr/0026-the-specialist-contract.md),
   [ADR-0033](../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)).
3. **Identity is runtime context,** never a shared default.
   ([ADR-0003](../../docs/adr/0003-runtime-context-for-user-identity.md))
4. **Security, memory, and persistence are Rung-0 repo-wide infrastructure, never a single
   project's private domain.** Generated code never sees secrets
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
9. **Design load is production** ([PRINCIPLES.md](../governance/principles.md#2-know-the-context-of-best-practice-asl-e-shenakht-e-context)):
   every component names its production path (design card point 16, and the seams table below).
10. **Every AI step is code, a decision model, or an LLM, or a composition of them.** A step that
    writes goes to an LLM, and code decides what it can. Every other decision point takes the
    decider first and the LLM as its escalation, held to one standard: a labeled set, accuracy
    per class, unsafe errors, latency, and cost ([ADR-0021](../../docs/adr/0021-decision-models-as-a-second-model-family.md),
    [decision-models.md](../architecture/decision-models.md)).

## Four-scale Wave-Particle Duality

Both the **Particle (`Agentic`)** approach and the **Wave (`Graph-Based`)** approach compile to the
same runtime substrate (`CompiledStateGraph` + `Harness` + `Backend` + `Memory`), but they represent
opposite control poles across four hierarchical scales ([ADR-0033](../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)):

| Scale | Scope | Particle Pole (Model Owns Clock) | Wave Pole (Architecture Owns Clock) |
| :--- | :--- | :--- | :--- |
| **Rung 0: Subatomic Primitives & Infrastructure** | Repo-wide (`models/`, `prompts/`, `tools/`, `middlewares/`, `data/`, `utils/`, `schemas/`) | **Shared:** `LLM / Decision Model (Jev)`, `Prompt`, `Tool`, `AgentMiddleware`, `Memory / Store`, `Backend / Sandbox`, `Security / Redaction`, `UserContext` | **Shared:** Available to every node, agent, and workflow across the repository |
| **Rung 1: Atomic / Unit Scale** | Single execution unit (`agents/` vs. `graphs/` + `nodes/`) | **`Agent` (`create_agent` / `create_deep_agent`):** Homogeneous **Hot Loop** over `AgentState` (`messages`); every turn runs the full `AgentMiddleware` stack and bound `Tools` | **`Graph` / `Subgraph` (`StateGraph`):** Heterogeneous **Stations (`Nodes`)** over a multi-field typed `State`; each station uses only the narrow resource it needs (`Jev`, retriever, structured chain, or pure code) |
| **Rung 2: Domain / Project Scale (P1-P5+)** | One domain capability (`workflows/` + `subagents/`) | **`SpecialistSpec[TInput, TReport]` / `Specialist`:** External delegatable face with declarative spec (`name`, `description`, `input_schema`, `report_schema`), `run`, `as_subagent`, and `as_tool` | **`Workflow[TInput, TReport]` (`*_workflow.py`):** Graph-native workflow owning typed dependencies, compiling a `StateGraph` ending in `ResultNode`, and returning `SpecialistResult[TReport]` |
| **Rung 3: Macro / Enterprise Scale** | Multi-domain orchestration | **`Coordinator` (`agents/coordinators/`):** Deep agent delegating dynamically to Rung-2 `Specialists` | **`Operation` (`workflows/`):** Macro-workflow (`Control Tower`) orchestrating multiple Rung-2 `Workflows` / `Specialists` |

**Choosing Wave vs. Particle density inside a domain project:**
- Use a **Graph station (`Node`)** when the step's input/output contract and transition are known at
  design time, or when a step needs a single isolated external dependency under `TRANSIENT_RETRY`.
- Use an **Agent (`create_agent`)** inside a station when the sequence of tool calls and search/read
  iterations depends on intermediate observations within a bounded budget.
- Note on `AgentMiddleware`: `AgentMiddleware` hooks (`before_model`, `wrap_model_call`,
  `after_model`, `wrap_tool_call`) attach to `create_agent` / `create_deep_agent`, not directly to a
  raw `StateGraph`. In a `StateGraph`, cross-cutting policies are either expressed as explicit
  graph nodes/edges or ride inside an `Agent` subgraph node.

## Scale seams

The production path for each seam. Lessons run the left column; designs must keep the right
column a swap, not a rewrite.

| Seam | Now | Production |
| :--- | :--- | :--- |
| Identity | `UserContext` passed by the CLI | Authenticated principal from the API, tenant in context |
| Checkpoints | `SqliteSaver`, one process | Postgres checkpointer behind the same interface; per-app databases first (R0) |
| Long-term store | `SqliteStore`, sequential connection | Postgres store; concurrent writers stay single-writer per resource |
| Vector index | Local Chroma, full rebuild | Managed vector store, incremental re-index, hybrid retrieval (R2); graph and vector combined (P8-C2) |
| Model access | Catalog, fallback middleware, tiers | Tier routing and verify-then-escalate (R2, D1), cascades at scale (P9), gateway and routing service (E2) |
| Decisions | LLM tiers with structured output; `decision_model` with Jev from R1 | A decision service: versioned question sets, shadow evaluation, per-tenant thresholds, a local backend for private state (E2) |
| Sandbox | Local shell backend, allow-listed env | Container or remote sandbox, session-scoped workspaces (E1) |
| Approvals | CLI loop over standard HITL requests | Approval service over the run's event stream (E2) |
| Execution | In-process CLI | Agent Server async runs (P14-B3); queue and workers (E3) |
| External calls | Explicit timeouts, one retry layer (`failure_util`) | Circuit-breaking and rate-limit budgets at the platform (E1) |

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
| Hierarchical | Several domains need their own supervisors (P14 or later) |
| Autonomous loop | The path can't be hard-coded, but progress is still verifiable |
