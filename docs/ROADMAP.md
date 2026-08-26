# Project Roadmap — Production-Grade Agentic AI Curriculum

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

**Problem:** User gives a file or PR diff → agent reviews code, suggests refactors, and generates tests.

### Phase A — Baseline
- LangGraph orchestration across review stages
- LangChain file tools (existing `file_ops.py`)
- Structured `ReviewResult` and `TestSuite` Pydantic output

### Phase B — Growth
- HITL interrupt before writing file changes
- Sandbox execution for running generated tests
- Middleware: model fallback and tool retry
- `InMemorySaver` → SQLite checkpointer

### Phase C — Professional
- Reviewer and test-writer as separate compiled LangGraph subgraphs
- Time-travel / replay for debugging bad review decisions
- GitHub MCP tool integration
- Optional DeepAgents coordinator for parallel multi-file delegation

**Frameworks:** LangGraph + LangChain → DeepAgents + CompiledSubAgent at Phase C

---

## P4 — Sandbox / Interpreter Agent

**Problem:** User gives a data or coding task → agent writes and runs code, inspects output, iterates, returns artifacts.

### Phase A — Baseline
- DeepAgents `create_deep_agent` with **Interpreter** backend
- LangChain file and DB tools (existing `file_ops.py`, `db_ops.py`)
- Agent loop: plan → write code → execute → inspect → refine

### Phase B — Growth
- **Sandbox** backend for isolated shell execution and artifact generation
- Memory for recurring analysis context across sessions
- Structured `AnalysisReport` Pydantic output
- HITL approval around shell/package operations

### Phase C — Professional
- Streaming execution events in real time
- LangSmith observability
- Wrap agent as a `CompiledSubAgent` for reuse in P6
- Multi-user namespace isolation

**Frameworks:** DeepAgents + LangChain → LangGraph composition at Phase C

---

## P5 — Memory-Rich Personal Assistant

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

P1 → P2 → P3 → P4 → P5 → P6

Each project reaches a solid baseline first, then grows through its pre-planned path. Phase C of each project feeds directly into P6 as a composable component.
