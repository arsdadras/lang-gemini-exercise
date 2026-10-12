# ADR-0033: Wave-Particle Duality Across Four Scales, the `workflows/` Layer, and the `Specialist[TInput, TReport]` Contract

- Status: Accepted
- Date: 2026-10-12
- Origin: user and mentor architectural review (resolving `agent`/`graph` and `specialist`/`workflow` inconsistencies)
- Supersedes: the raw-`str` output allowance in [ADR-0026](0026-the-specialist-contract.md) and the scattered `NewType` import workarounds in [ADR-0032](0032-typed-specialist-inputs.md)

## Context

By the end of R1, four structural inconsistencies had accumulated across `src/agentlab/`:

1. **Dual-role confusion between `Agent` and `Graph` (and `Subagent` vs. `Subgraph`):** Both `create_agent` / `create_deep_agent` and `StateGraph.compile()` produce a `CompiledStateGraph`, and both can be embedded inside a parent graph or wrapped behind a tool/subagent. Yet their architectural roles, state shapes, and harness consumption patterns were never formally distinguished.
2. **Inverted dependency direction and scattered `run_*` workflows:** End-to-end project runners (`run_research`, `run_rag`, `run_code_review`, `run_interpreter`) were placed inside `src/agentlab/subagents/*_subagent.py`. Because `AGENTS.md` enforces `agents -> subagents, graphs -> nodes`, putting `run_*` inside `subagents/` prevented `subagents/` from importing `agents/` and forced `NewType` definitions (`Researcher`, `RagGraph`, `CodeReviewGraph`, `Interpreter`) to be scattered across `nodes/`, `graphs/`, and `agents/` ([ADR-0032](0032-typed-specialist-inputs.md)). Worse, `make_researcher_subagent` bypassed `run_research` (the full R1 verification graph) and wrapped the raw `Researcher` agent directly.
3. **Asymmetric output contracts (`*Report` vs. `str` vs. `dict`):** P1 (`ResearchReport`) and P3 (`CodeReviewReport`) returned structured Pydantic reports inside `SpecialistResult[T]`, whereas P2 (`rag_subagent.py`) and P4 (`interpreter_subagent.py`) returned `SpecialistResult[str]`, and P5 (`user_context_tool.py`) returned a raw `dict[str, str]` outside the specialist envelope altogether.
4. **P5's misplaced identity:** P5 (`personal_assistant_agent`) was built as a top-level user-facing assistant that treated long-term memory, SQLite storage, and secret redaction as its private domain, while only exposing a raw dict helper (`load_user_context`) to `lab-brief`. Cross-cutting persistence, memory, and security belong to the repository's shared foundation, while P5 itself must also stand as a composable domain specialist alongside P1-P4.

## Decision

### 1. The Four-Scale Wave-Particle Duality Architecture

Every component in `agentlab` is organized across **four hierarchical scales (Rungs 0-3)**. At Rungs 1, 2, and 3, the architecture exhibits a **Wave-Particle Duality**: both poles share the same underlying runtime substance (`CompiledStateGraph` + `Harness` + `Backend` + `Memory`), but differ in **who owns the control clock** and **how the harness is consumed**:

- **Particle (`Agentic` pole):** A localized, autonomous entity with a single identity and prompt. The **model** owns the step-by-step clock inside a loop.
- **Wave (`Graph-Based` pole):** A topological flow across explicit stations. The **architecture** (code edges or typed `decision_model` routers) owns the clock.

| Scale | Scope | Particle Pole (Autonomous Entity) | Wave Pole (Explicit Topology) |
| :--- | :--- | :--- | :--- |
| **Rung 0: Subatomic Primitives & Cross-Cutting Infrastructure** | Repo-wide foundation (`models/`, `prompts/`, `tools/`, `middlewares/`, `data/`, `utils/`, `schemas/`) | **Shared across both poles:** `LLM / Decision Model (Jev)`, `Prompt`, `Tool (@tool / MCP)`, `AgentMiddleware`, `Memory / Store`, `Backend / Sandbox`, `Security / Redaction`, `UserContext` | **Shared across both poles:** Every Rung-0 primitive is a repo-wide infrastructure service available to any node, agent, or workflow—never the private property of a single project |
| **Rung 1: Atomic / Unit Scale** | Single execution unit (`agents/` vs. `graphs/` + `nodes/`) | **`Agent` (`create_agent` / `create_deep_agent`):** Runs in a **Homogeneous Hot Loop** over a single shared `AgentState` (`messages`). Every turn re-runs the same `AgentMiddleware` stack (`before_model`, `wrap_model_call`, `after_model`, `wrap_tool_call`) and exposes the agent's bound toolset | **`Graph` / `Subgraph` (`StateGraph`):** Advances through **Heterogeneous Stations (`Nodes`)** over a multi-field typed `State`. Each node consumes only the narrow slice of the harness it needs (e.g., one `Jev` decision call, one retriever call, one structured LLM chain, or pure deterministic Python). Note: `StateGraph` does not accept `AgentMiddleware` directly; middleware either lives inside an `Agent` node or is expressed as explicit graph nodes/edges |
| **Rung 2: Domain / Project Scale (P1-P5+)** | One complete domain capability (`workflows/` + `subagents/`) | **`Specialist[TInput, TReport]`:** The domain capability seen from **outside** as a single delegatable unit with a typed input schema, a rich Pydantic `*Report` output, and `as_subagent` / `as_tool` adapters | **`Workflow` (`run_<project>` in `workflows/<project>_workflow.py`):** The domain capability seen from **inside** as an end-to-end operational film script that wires Rung-1 `Graphs` and `Agents`, enforces budgets/gates, and packs `SpecialistResult[TReport]` |
| **Rung 3: Macro / Enterprise Scale (Capstones & Term E)** | Multi-domain orchestration | **`Coordinator` (`agents/coordinators/`):** A `create_deep_agent` supervisor that delegates dynamically to Rung-2 `Specialists` when task decomposition is only knowable at runtime | **`Operation` (`workflows/`):** A macro-workflow (`Control Tower`) that orchestrates multiple Rung-2 `Workflows` / `Specialists` over deterministic or decider-routed branches (e.g., `personal_brief_workflow`, P6, P7, P14) |

At Rung 2, **`Specialist` and `Workflow` are two faces of the same coin**. Every project `P1`-`P5` (and later specialist projects) produces one coin. What varies from project to project is its internal **Wave/Particle density**:
- **P2 (RAG) and P3 (Code Review):** High Wave density (`Graph`-dominant stations, minimal autonomous agent loops).
- **P4 (Interpreter):** High Particle density (`Agent`-dominant loop over a sandboxed shell, thin `Workflow` wrapper for deliverable diffing and report assembly).
- **P1 (Research):** Balanced 50/50 Wave-Particle hybrid (a `StateGraph` that plans, routes sources via `Jev`, fans out via `Send` to a `create_agent` researcher loop with `SourceRouteMiddleware` and `EvidenceStopMiddleware`, and verifies claims in a graph node).
- **P5 (Personal Context & Memory):** Rung-0 memory/store/security infrastructure belongs to the entire repo; P5's domain coin is the `personal_context` `Workflow` / `Specialist` (alongside its interactive `lab-assistant` app).

### 2. New `src/agentlab/workflows/` Package and Clean Dependency Direction

We introduce `src/agentlab/workflows/` (`*_workflow.py`) directly below `apps/` and above `agents/`, `graphs/`, and `subagents/`:

```text
apps -> workflows -> agents (including coordinators/), graphs, subagents -> nodes, middlewares, tools, retrieval -> models, prompts, schemas, data, utils -> configs
```

- `workflows/<project>_workflow.py` owns `run_<project>(...) -> SpecialistResult[<Project>Report]` and the project's `Specialist` descriptor. Because `workflows/` sits above `agents/` and `graphs/`, it can construct or accept default `Agent` and `Graph` instances directly without circular imports or scattered `NewType` workarounds.
- `subagents/<project>_subagent.py` becomes a thin adapter layer that wraps a `Workflow` / `Specialist` as a `CompiledSubAgent` or LangChain `BaseTool` for Rung-3 `Coordinators`.
- In particular, `make_researcher_subagent` wraps `run_research` (`research_workflow.py`) so delegated research runs execute the full R1 multi-source plan-and-verify pipeline rather than bypassing it.

### 3. Unified Rich `*Report` Contracts and Lightweight `Specialist[TInput, TReport]`

- **No raw `str` or `dict` outputs at Rung 2:** Every domain workflow returns `SpecialistResult[TReport]` where `TReport` is a domain-specific Pydantic model in `src/agentlab/schemas/output/*_output_schema.py` with minimal bloat (2-4 high-signal fields):
  - **P1:** `ResearchReport` (existing).
  - **P2:** `RagReport` (`answer: str`, `citations: list[str]`, `retrieval_mode`, `grounding_verdict`).
  - **P3:** `CodeReviewReport` (existing).
  - **P4:** `InterpreterReport` (`answer: str`, `executed_commands: list[str]`, `deliverables: list[str]`).
  - **P5:** `PersonalContextReport` (`profile_summary: str`, `relevant_facts: list[str]`, `active_preferences: dict[str, str]`, `active_skills: list[str]`).
- **Lightweight `Specialist[TInput, TReport]` contract (in `schemas/output/specialist_output_schema.py`):** A flat, frozen Pydantic/dataclass descriptor holding:
  - `name: str` and `description: str`
  - `input_schema: type[TInput]` and `report_schema: type[TReport]`
  - `run: Callable[..., SpecialistResult[TReport]]`
  - `as_subagent(...) -> CompiledSubAgent` and `as_tool(...) -> BaseTool`
  It does **not** wrap `CompiledStateGraph` in a heavy custom OOP class (`BaseAgent`), preserving LangGraph Studio, native streaming, checkpointers, and [ADR-0006](0006-remove-agent-registry.md).

### 4. Phased Implementation Before R2 Teaching

To keep cognitive load clean and avoid mixing architectural refactoring with R2's retrieval curriculum:
- **Phases 1-3 (Standalone Infrastructure & Adaptation Session):** Implement the unified `*Report` schemas and `Specialist[TInput, TReport]` (Phase 1), build `src/agentlab/workflows/` and thin `subagents/` adapters including `make_researcher_subagent` over `run_research` and P5's `personal_context_workflow` (Phase 2), and decouple Rung-0 Memory/Store/Redaction/`UserContext` infrastructure plus research HITL interrupt propagation (Phase 3).
- **Phase 4 (Separate `/mentor` Sessions per Return-Pass Stage):** Teach and execute `R2`, `R3`, `R4`, the `P5` pass, and `R5` in fresh, dedicated `/mentor` sessions from the top-down mountain-peak perspective ("Compressor Balancing Principle": vertical preventative hardening for structurally tall projects `P2`-`P4`, horizontal/practical specialist completion for `P5`).

## Consequences

- **Positive:** Every project `P1`-`P5` shares one symmetrical mental model (`Agent/Graph` at Rung 1, `Specialist/Workflow` at Rung 2, `Coordinator/Operation` at Rung 3). Dependency direction is strictly downward without `NewType` gymnastics across `nodes/` and `subagents/`. Coordinators and macro-workflows receive rich, typed `*Report` objects from every specialist.
- **Negative / Cost:** Adding `src/agentlab/workflows/` adds one top-level package under `src/agentlab/` (recorded here per `AGENTS.md` convention 12) and requires updating callers in `apps/`, `subagents/`, and `tests/` during the dedicated Phases 1-3 session.

## Alternatives considered

- **Keep `run_*` inside `subagents/` and keep `NewType` wrappers (`ADR-0032`):** Rejected. `run_*` is used by CLI apps, eval harnesses, and macro-workflows that are not subagents, and keeping it in `subagents/` inverted the dependency hierarchy between `agents/` and `subagents/`.
- **Wrap every `Agent` and `Graph` in a custom OOP `BaseAgent` class:** Rejected. Hiding `CompiledStateGraph` behind a custom class breaks LangChain/LangGraph native `stream()`, `aget_state()`, `Command(resume=...)`, and LangGraph Studio compatibility. A flat `Specialist[TInput, TReport]` descriptor at Rung 2 gives typed metadata and uniform `run` / `as_subagent` / `as_tool` boundaries while leaving Rung-1 `Agent` and `Graph` objects 100% native.
