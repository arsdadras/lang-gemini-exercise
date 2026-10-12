---
name: architecture-duality
description: Guide for designing, refactoring, and teaching components under agentlab's 4-scale Wave-Particle Duality architecture (ADR-0033): Rung 0 primitives/infrastructure, Rung 1 Agent vs Graph, Rung 2 Specialist[TInput, TReport] vs Workflow (workflows/*_workflow.py), and Rung 3 Coordinator vs Operation.
---

# Architecture Duality (`ADR-0033`)

Use this skill whenever designing, refactoring, reviewing, or teaching any `agentlab` component,
workflow, specialist, agent, or graph ([ADR-0033](../../../docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md),
[standards.md](../../../library/architecture/standards.md)).

## 1. The Four Hierarchical Scales (Rungs 0-3)

| Rung | Scale | Particle Pole (Model Owns Clock) | Wave Pole (Architecture Owns Clock) |
| :--- | :--- | :--- | :--- |
| **Rung 0** | **Subatomic Primitives & Repo-Wide Infrastructure** | `LLM / Decision Model (Jev)`, `Prompt`, `Tool (@tool / MCP)`, `AgentMiddleware`, `Memory / Store`, `Backend / Sandbox`, `Security / Redaction`, `UserContext` | Shared across the entire repository; **never** locked inside a single project (e.g., Memory/Store/Redaction are Rung-0 infrastructure, not P5-private) |
| **Rung 1** | **Atomic / Unit Scale** (`agents/` vs. `graphs/` + `nodes/`) | **`Agent` (`create_agent` / `create_deep_agent`):** Homogeneous **Hot Loop** over a single shared `AgentState` (`messages`); every turn runs the same `AgentMiddleware` stack and bound `Tools` | **`Graph` / `Subgraph` (`StateGraph`):** Heterogeneous **Stations (`Nodes`)** over a multi-field typed `State`; each station consumes only the narrow slice of the harness it needs (`Jev`, retriever, structured chain, or pure Python) |
| **Rung 2** | **Domain / Project Scale** (`P1`-`P5`+) | **`Specialist[TInput, TReport]`:** External delegatable face with `name`, `description`, `input_schema`, `report_schema`, `run`, `as_subagent`, and `as_tool` | **`Workflow` (`run_<project>` in `workflows/<project>_workflow.py`):** Internal end-to-end film script wiring `Graphs` and `Agents` and returning `SpecialistResult[TReport]` |
| **Rung 3** | **Macro / Enterprise Scale** (Capstones & Term E) | **`Coordinator` (`agents/coordinators/`):** DeepAgents supervisor delegating dynamically to Rung-2 `Specialists` | **`Operation` (`workflows/`):** Macro-workflow (`Control Tower`) orchestrating multiple Rung-2 `Workflows` / `Specialists` |

## 2. Hard Invariants to Enforce

1. **Strict Downward Dependency Direction:**
   `apps -> workflows -> agents (including coordinators/), graphs, subagents -> nodes, middlewares, tools, retrieval -> models, prompts, schemas, data, utils -> configs`
   - End-to-end `run_<project>` functions live in `src/agentlab/workflows/<project>_workflow.py`,
     never inside `subagents/`.
   - `subagents/<project>_subagent.py` is a thin adapter that wraps a `Workflow` / `Specialist` as
     a `CompiledSubAgent` or `BaseTool`.
   - `make_researcher_subagent` must delegate through `run_research` (`research_workflow.py`) so
     delegated runs execute the full R1 verification graph.
2. **Every Specialist Returns a Rich Pydantic `*Report` (Never `str` or `dict`):**
   - **P1:** `ResearchReport`
   - **P2:** `RagReport` (`answer`, `citations`, `retrieval_mode`, `grounding_verdict`)
   - **P3:** `CodeReviewReport`
   - **P4:** `InterpreterReport` (`answer`, `executed_commands`, `deliverables`)
   - **P5:** `PersonalContextReport` (`profile_summary`, `relevant_facts`, `active_preferences`, `active_skills`)
3. **Flat `Specialist[TInput, TReport]` Descriptor, Not an OOP Wrapper:**
   - Never wrap `CompiledStateGraph` in a custom `BaseAgent` class that hides `.stream()`,
     `.invoke()`, `.get_state()`, or LangGraph Studio compatibility.
   - Use the flat `Specialist[TInput, TReport]` contract in
     `schemas/output/specialist_output_schema.py`.
4. **Precise LangGraph vs. AgentMiddleware Semantics:**
   - `AgentMiddleware` hooks (`before_model`, `wrap_model_call`, `after_model`, `wrap_tool_call`)
     attach to `create_agent` / `create_deep_agent` hot loops, not directly to `StateGraph`.
   - In a `StateGraph`, cross-cutting policies either ride inside an `Agent` subgraph node or are
     modeled as explicit graph nodes/edges/runnable wrappers.
5. **Top-Down Compressor Balancing in Return Pass (`R` Stages):**
   - Always open from the mountain peak: show the Rung-2 `Workflow` film script, `Specialist`
     contract, and Wave/Particle density first.
   - Apply vertical preventative hardening to structurally tall projects (`P2`, `P3`, `P4`) and
     horizontal/practical specialist completion to `P5`.
