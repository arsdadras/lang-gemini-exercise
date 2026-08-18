# Project Roadmap — Agentic AI Curriculum

A progressive curriculum for building production-grade agentic AI systems using the LangChain ecosystem with a **problem-first** approach. Frameworks are used **only when the project actually needs them**.

- **LangChain** for tools, models, prompts, middleware, structured output, and guardrails.
- **LangGraph** for custom state, routing, subgraphs, persistence, interrupts, and time-travel.
- **DeepAgents** for planning, delegation, memory/skills, interpreter, sandbox, MCP tools, and advanced context management.

> Design rule: every project starts simple, but its expansion path is planned in advance so it can evolve into a professional system without a rewrite.

---

## Cross-cutting advanced features

These are not forced into every project on day one. They are mapped in advance and enabled when the project reaches the right maturity level.

- **Structured output** with schemas for reliable downstream consumption.
- **Middleware** for retries, model fallback, tool selection, guardrails, PII detection, and rate limits.
- **Human-in-the-loop** for approval gates on sensitive actions.
- **Persistence and checkpointing** for resumability and durable execution.
- **Time-travel / replay / fork** for debugging and workflow iteration.
- **Streaming** for real-time execution visibility.
- **Memory and skills** for long-term adaptation.
- **Interpreter** for scoped code execution and programmable transformations.
- **Sandbox** for isolated execution, filesystem edits, package installs, and artifact generation.
- **RAG** for grounded retrieval over documents and codebases.
- **MCP tools** for external tool ecosystems when needed.
- **LangSmith observability** for tracing, debugging, and evaluation.
- **Deployment with LangGraph SDK** for multi-user threads and production access.

---

## P1 — Research Agent

**Problem:** User gives a topic, and the agent searches the web and returns a structured, cited report.

### Phase A — baseline
- DeepAgents `create_deep_agent` as the fastest useful orchestrator.
- LangChain Tavily tool for web search.
- Prompted research workflow with streaming output.

### Phase B — growth path
- Structured output schema for report sections.
- Middleware for retries, fallback models, and output guardrails.
- Human approval for expensive or sensitive tool usage.
- Memory for recurring research preferences and prior topics.

### Phase C — professional expansion
- Research subagents for scoped topic decomposition.
- LangSmith traces and evaluation datasets.
- SDK exposure for multi-session usage.
- Optional RAG overlay for local notes and saved research corpus.

**Primary frameworks:** DeepAgents + LangChain  
**Optional advanced expansion:** LangGraph deployment/runtime features when needed.

---

## P2 — RAG Agent

**Problem:** User asks questions over private documents, notes, or code, and the agent answers with grounded retrieval.

### Phase A — baseline
- LangGraph graph with ingest, retrieve, grade, and generate nodes.
- Vector retrieval and prompt-grounded answering.
- Conditional routing for retry / fallback retrieval.

### Phase B — growth path
- Corrective-RAG loop with query rewrite and relevance grading.
- Checkpointing for resumable multi-turn work.
- Streaming node-by-node execution.
- Time-travel for debugging retrieval mistakes.

### Phase C — professional expansion
- Hybrid retrieval: local corpus + web fallback.
- Wrap the compiled graph as a subagent inside a larger system.
- Add skills for domain-specific retrieval behavior.
- Add middleware guardrails and response validation.

**Primary frameworks:** LangGraph + LangChain  
**Optional advanced expansion:** DeepAgents as outer coordinator when multi-agent composition becomes useful.

---

## P3 — Code Review & Test Generation Agent

**Problem:** Agent reviews source files or diffs, suggests refactors, and generates tests.

### Phase A — baseline
- LangGraph parent graph coordinating review and test-generation steps.
- LangChain file and code tools.
- Structured output for findings and suggested tests.

### Phase B — growth path
- Human-in-the-loop before writing changes.
- Sandbox execution for running tests safely.
- Middleware for fallback models and tool retry.
- Persistence for resumable review sessions.

### Phase C — professional expansion
- Specialized reviewer and test-writer subagents.
- GitHub integration for PR/file workflows.
- Replay/time-travel for debugging bad review paths.
- Optional DeepAgents coordinator for task planning across many files.

**Primary frameworks:** LangGraph + LangChain  
**Optional advanced expansion:** DeepAgents for delegation/planning when scale increases.

---

## P4 — Sandbox / Interpreter Agent

**Problem:** Agent writes and runs code, inspects outputs, iterates, and returns artifacts like reports, charts, or files.

### Phase A — baseline
- DeepAgents with interpreter for scoped, programmable code execution.
- Tool-assisted file/data access.
- Iterative loop: plan → run → inspect → refine.

### Phase B — growth path
- Sandbox backend for isolated execution and filesystem operations.
- Artifact generation workflows.
- Memory for recurring analysis context.
- Structured report generation.

### Phase C — professional expansion
- Streaming execution events.
- Human approval around shell/package actions.
- LangSmith observability.
- Wrap as a reusable component in larger systems.

**Primary frameworks:** DeepAgents + LangChain  
**Optional advanced expansion:** LangGraph wrapping/subgraph composition when reused inside broader workflows.

---

## P5 — Memory-Rich Personal Assistant

**Problem:** Agent supports long-running user relationships, remembers facts and preferences, and uses them safely over time.

### Phase A — baseline
- DeepAgents memory files with backend routing.
- Search + simple action tools.
- Clear separation of state vs long-term memory.

### Phase B — growth path
- Skills library for reusable behaviors.
- Memory consolidation and summarization.
- Human approval for sensitive memory writes.
- Middleware guardrails and PII protection.

### Phase C — professional expansion
- Per-user namespacing and multi-thread isolation.
- Persistent backing store.
- Evaluation of memory quality and drift.
- MCP tools for controlled external integrations.

**Primary frameworks:** DeepAgents + LangChain  
**Optional advanced expansion:** LangGraph deployment/runtime for production hosting.

---

## P6 — Production Capstone System

**Problem:** A premium production system combining the strongest capabilities from earlier projects into a single deployable architecture.

### Phase A — integration baseline
- Select and compose the best components from P1–P5.
- Use the simplest orchestration that fits the chosen capabilities.
- Standardize schemas, tracing, config, and model routing.

### Phase B — hardening
- Durable persistence and checkpointing.
- Full observability with LangSmith.
- Streaming, retries, model fallback, and guardrails.
- Approval flows for sensitive operations.

### Phase C — production rollout
- Multi-user thread isolation.
- LangGraph SDK exposure and deployment config.
- Secrets/env strategy, health checks, and operational logging.
- Optional time-travel/replay workflows for support and debugging.

**Primary frameworks:** Hybrid by need.  
This project intentionally uses whichever combination best serves the chosen final architecture.

---

## Framework selection guide

| Need | Best fit |
|---|---|
| Tools, models, prompts, middleware, structured output | LangChain |
| Custom orchestration, state, routing, subgraphs, interrupts, persistence, replay | LangGraph |
| Planning, delegation, memory/skills, interpreter, sandbox, MCP tools, context management | DeepAgents |
| Deployment, SDK access, production threads | LangGraph SDK |

---

## Build order

P1 → P2 → P3 → P4 → P5 → P6

Each project should first reach a solid baseline, then grow through its preplanned advanced path only when it becomes useful. Earlier projects stay intentionally expandable so they can later be upgraded into more professional versions instead of being discarded.
