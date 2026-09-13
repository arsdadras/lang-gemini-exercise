# Project Roadmap — Production-Grade Agentic AI Curriculum

> **Superseded by `docs/Agentic AI Curriculum Roadmap v2.md` (2026-09-11).** This file documents the original 6-project (P1–P6) curriculum shape and is kept for history. The curriculum has since expanded to 12 projects (P1–P12) with P6 and P12 as milestone capstones, followed by Term E (post-P12 platformization/scale) — read Roadmap v2 first for the current shape. The P1–P5 phase-by-phase content below is still accurate as *design* reference; for live status, always defer to `docs/MENTOR_HANDOFF.md`'s session log, not the status lines in this file.

In this repository we build multiple distinct agentic AI projects.
Each project has a practical **base level** and a pre-planned **growth path**
toward more advanced and professional implementations.

Frameworks are used **only when the problem requires them** — never forced.

- **LangChain** — models, tools, prompt templates, structured output, middleware, guardrails.
- **LangGraph** — stateful orchestration, routing, subgraphs, checkpointing, HITL, time-travel.
- **DeepAgents** — planning, delegation, memory/skills, interpreter, sandbox, MCP, advanced context. Built on LangGraph; can consume `CompiledSubAgent` (a compiled LangGraph graph exposed as a runnable subagent).
- **LangGraph SDK / LangSmith** — deployment, multi-user threads, streaming at scale, observability.

> **Planning rule:** every project must be complete and useful at the base level. Its upgrade path is defined from day one so it can grow professionally without a rewrite.

---

## Advanced Features Map

These features are not forced into every project on day one. They are mapped below and activated when the project reaches the right maturity.

| Feature | Description | Introduced in |
|---|---|---|
| **Structured output** | Pydantic schemas for reliable downstream consumption | P1-B |
| **Middleware** | Retries, model fallback, guardrails, PII detection, rate limits | P1-B |
| **HITL (Human-in-the-loop)** | Interrupt + approval for sensitive or high-risk actions | P3-B |
| **Persistence / Checkpointing** | Durable execution, resumability, crash recovery | P2-B |
| **Time-travel / Replay / Fork** | Re-run from prior checkpoints for debugging and auditing | P2-B / P3-C |
| **Streaming** | Real-time node/graph/subagent output visibility | P1-B |
| **Memory & Skills** | Long-term facts, preferences, reusable behavior files | P5-A |
| **Interpreter** | In-process, stateful code execution within the agent loop | P4-A |
| **Sandbox** | Isolated shell execution, package installs, artifact generation | P4-B |
| **RAG** | Grounded retrieval over documents, code, and internal knowledge | P2-A |
| **Subgraphs / CompiledSubAgent** | Modular LangGraph graphs composed inside larger systems | P2-C / P3-C |
| **Multi-agent delegation** | Parallel / sequential subagent task dispatch | P3-C / P6-A |
| **MCP tools** | External tool ecosystems via standard interface | P5-C |
| **LangSmith observability** | Tracing, evaluation, and debugging across agents | P2-B |
| **LangGraph SDK deployment** | Multi-user threads, remote client access, production hosting | P6-C |
| **ACP (Agent Client Protocol)** | Standardized inter-agent communication | P6-C |

---

## P1 — Research Agent

**Status (2026-08-19): Phase A ✅ · Phase B ✅ · Phase C 🔶 in progress.**
See `MENTOR_HANDOFF.md` for the detailed session-by-session state and open items — read that file first before resuming work here.

**Problem:** User gives a topic → agent searches the web → returns a structured, cited report.

### Phase A — Baseline ✅
- DeepAgents `create_deep_agent` as orchestrator
- LangChain `TavilySearchResults` tool
- Streaming output to terminal

### Phase B — Growth ✅
- Structured Pydantic schema for report sections (`schemas.research.ResearchReport`)
- Middleware: retries + fallback model (`middleware.retry`), HITL approval (`middleware.hitl`)
- HITL approval before web_search calls, via `HumanInTheLoopMiddleware` + `InMemorySaver` checkpointer
- Memory for recurring research preferences and past topics — **not started, deferred**

### Phase C — Professional 🔶
- ✅ Research subagent per sub-question (`subagents.researcher.researcher_subagent`, structured `ResearchFindings` output) — wired into `app.py`
- ⬜ LangSmith traces and evaluation datasets — `.env` already has `LANGSMITH_*` vars provisioned, just needs wiring + a first traced run
- ⬜ SDK-exposed multi-session service
- ⬜ Optional RAG overlay for local notes or saved corpus

**Frameworks:** DeepAgents + LangChain → LangGraph SDK at Phase C

---

## P2 — RAG Agent

**Problem:** User asks questions over private documents, notes, or code → agent answers with grounded retrieval.

### Phase A — Baseline
- LangGraph `StateGraph`: ingest → retrieve → grade → generate nodes
- Vector retrieval (FAISS or Chroma) + prompt-grounded answering
- Conditional edge: irrelevant docs → fallback/retry

### Phase B — Growth
- Corrective-RAG loop with query rewrite and grading
- `InMemorySaver` checkpointing for resumable multi-turn work
- Streaming node-by-node output
- Time-travel and replay for debugging retrieval mistakes
- LangSmith tracing per node

### Phase C — Professional
- Hybrid retrieval: local vector store + web fallback
- Wrap compiled graph as `CompiledSubAgent` for use inside larger systems
- Skills for domain-specific retrieval behavior
- Middleware guardrails and response validation

**Frameworks:** LangGraph + LangChain → DeepAgents wrapper at Phase C

---

## P3 — Code Review & Test Generation Agent

**Status (2026-09-02): Phase A ✅ · Phase B ✅ · Phase C ✅ COMPLETE.**
See `MENTOR_HANDOFF.md` for full implementation details, architectural patterns, and verified test suite.

**Problem:** User gives a file or PR diff → agent reviews code, suggests refactors, and generates tests.

### Phase A — Baseline ✅
- LangGraph orchestration across review stages
- LangChain file tools (`file_ops.py`)
- Structured `ReviewResult` and `TestSuite` Pydantic output

### Phase B — Growth ✅
- HITL interrupt before writing file changes (`interrupt()` + `Command(resume=...)`)
- Sandbox execution for running generated tests (`run_tests_in_sandbox`)
- Self-correction feedback loop (`fix_tests_node`)
- Middleware: model fallback and tool retry
- Persistent SQLite checkpointer (`SqliteSaver` in `core/src/data/sqlite_db.py`)

### Phase C — Professional ✅
- Reviewer, test-writer, and refactor-gate as separate compiled LangGraph subgraphs
- DeepAgents adapter wrapping parent graph as `CompiledSubAgent` (`code_review_subagent`)
- Time-travel and state history inspection (`inspect_state_history`, `fork_from_checkpoint`)
- High-speed model routing (`gemini-3.5-flash-lite` under 10s runtime)

**Frameworks:** LangGraph + LangChain → DeepAgents + CompiledSubAgent at Phase C

---

## P4 — Sandbox / Interpreter Agent

**Status (2026-09-09): Phase A ✅ · Phase B ✅ · Phase C ✅ COMPLETE.**
See `MENTOR_HANDOFF.md` §"P4 — Sandbox / Interpreter Agent — Phase C Status" for full implementation detail, including the `interpreter_subagent`, the multi-agent `coding_coordinator_agent`, and the enterprise agent registry work.

**Problem:** User gives data, computational, or shell automation tasks → agent plans, executes code/scripts in an isolated workspace, manages artifacts, self-corrects on errors, and returns verified results.

### Phase A — Native Workspace & Execution Engine
- DeepAgents `create_deep_agent` powered by native `LocalShellBackend` / `FilesystemBackend`
- Confinement in anchored `out/sandbox/` workspace (zero repository pollution)
- Native file operations (`ls`, `glob`, `grep`, `read`, `write`, `edit`) and shell execution (`execute`)
- Stateful Python computation loop with automatic output capture and error recovery

### Phase B — Growth & Governance
- Security policies via `FilesystemPermission`
- Human-In-The-Loop (HITL) approval on high-risk shell commands via `interrupt_on={"execute": True}`
- Artifact management and persistent data pipelines (generating CSVs, charts, reports)
- Cross-session persistence via `get_sqlite_checkpointer()`

### Phase C — Professional & Subagent Composition
- Streaming execution events in real time
- LangSmith tracing and run observability
- Wrapping the Sandbox/Interpreter Agent as a `CompiledSubAgent` for modular multi-agent reuse

**Frameworks:** DeepAgents (`LocalShellBackend`, `FilesystemPermission`) + LangGraph (Checkpoints, HITL)


---

## P5 — Memory-Rich Personal Assistant

**Status (2026-09-11): Session 0 approved, Phase A in progress.**
See `docs/design_cards/P5_memory_assistant.md` for the full 15-Point Design Card and `MENTOR_HANDOFF.md` §"P5 — Memory-Rich Personal Assistant (Orientation & Session 0)" for the live session log.

**Problem:** Agent supports ongoing user relationships → remembers facts, preferences, and past tasks across sessions.

### Phase A — Baseline
- DeepAgents `CompositeBackend`: `StateBackend` for conversation + `StoreBackend` for `/memories/`
- Memory file loaded at session start
- Tavily search + file tools

### Phase B — Growth
- Skills library (`/skills/`) for reusable behaviors
- Memory consolidation / summarization subagent
- HITL approval for sensitive memory writes
- Middleware guardrails and PII protection

### Phase C — Professional
- Per-user namespace isolation via `lambda rt: (rt.server_info.assistant_id,)`
- Persistent backing store (SQLite or Postgres)
- MCP tools for controlled external integrations
- Evaluation of memory quality and drift

**Frameworks:** DeepAgents + LangChain → LangGraph SDK at Phase C

---

## P6 — Capstone: Production Multi-Agent System

**Status:** Not started. Per `docs/Agentic AI Curriculum Roadmap v2.md`, P6 is now the *first* of two formal capstones (P6 and P12) rather than the curriculum's final project — read Roadmap v2 §"P6 — Midterm/Final I" before starting.

**Problem:** Combine the strongest capabilities from P1–P5 into a single deployable, observable, multi-user production system.

### Phase A — Integration Baseline
- DeepAgents coordinator at the top level
- Subagents composed from P1–P4 Phase C components as `CompiledSubAgent` instances
- Shared LangChain model/tool layer with GapGPT router + Gemini fallback
- Standardized state schemas, prompt registry, and config

### Phase B — Hardening
- Full LangSmith observability across all agents and subgraphs
- Durable persistence: SQLite → Postgres checkpointer
- Streaming at all levels (node, graph, subagent)
- Retries, model fallback, guardrails, approval flows

### Phase C — Deployment
- `langgraph.json` deployment config for all graphs
- LangGraph SDK client for external access
- Multi-user thread isolation
- ACP (Agent Client Protocol) for standardized inter-agent communication
- Health checks, secrets via env, operational logging

**Frameworks:** Full stack — LangChain + LangGraph + DeepAgents + LangGraph SDK

---

## Framework Selection Guide

| Need | Best fit |
|---|---|
| Models, tools, prompts, structured output, middleware | LangChain |
| Custom state, routing, subgraphs, checkpointing, HITL, time-travel | LangGraph |
| Planning, delegation, memory/skills, interpreter, sandbox, MCP, context management | DeepAgents |
| Deployment, SDK access, multi-user threads | LangGraph SDK |

---

## Build Order

P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8 → P9 → P10 → P11 → P12 → Term E

Each project reaches a solid baseline first, then grows through its pre-planned path. Phase C of each project feeds directly into P6, and later P12, as a composable component. See `docs/Agentic AI Curriculum Roadmap v2.md` for P6–P12 and Term E, not covered by this historical file.
