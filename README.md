# Deep Agents Template — Production-Grade Agentic AI Scaffold

An enterprise-ready, modular engineering scaffold and progressive curriculum for autonomous agentic AI systems, built on [DeepAgents](https://github.com/deepagents), [LangGraph](https://langchain-ai.github.io/langgraph/), and [LangChain](https://python.langchain.com/).

---

## 🏛️ Curriculum & Architecture Roadmap

This repository demonstrates the progressive evolution of agentic architectures from isolated single-purpose agents to production-grade, stateful, multi-agent cooperative systems.

| Project | Name & Domain | Key Architectural Patterns | Status |
| :--- | :--- | :--- | :---: |
| **P1** | **Web Research Agent** | DeepAgents orchestrator, structured citations, multi-tier fallback cascade, streaming output | ✅ **Complete** |
| **P2** | **RAG Coordinator Agent** | LangGraph StateGraph, vector indexing, document grading, corrective retrieval, subagent delegation | ✅ **Complete** |
| **P3** | **Code Review & Test Gen** | 3-subgraph parent graph, process-isolated sandbox runner, cyclic test fixer loop, modern HITL (`interrupt()` + `Command(resume=...)`), SQLite checkpointing, time-travel history replay | ✅ **Complete** |
| **P4** | **Sandbox / Interpreter Agent** | DeepAgents native `LocalShellBackend`, anchored filesystem confinement (`out/sandbox`), execution safety, shell HITL governance, `CompiledSubAgent` composition | 🚀 **In Progress** |
| **P5** | **Memory-Rich Assistant** | `CompositeBackend` (`StateBackend` + `StoreBackend`), persistent cross-session facts, dynamic skill loading | 📋 *Planned* |
| **P6** | **Autonomous Capstone** | Hierarchical multi-agent coordinator, LangGraph SDK deployment, inter-agent delegation | 📋 *Planned* |

See [`docs/ROADMAP.md`](docs/ROADMAP.md) for full phase-by-phase specifications and [`docs/MENTOR_HANDOFF.md`](docs/MENTOR_HANDOFF.md) for operational engineering logs.

---

## 📂 Repository Layout

The codebase follows a strictly decoupled, modular layered layout:

```text
core/
├── src/                    # Reusable library building blocks
│   ├── graphs/             # Compiled LangGraph StateGraphs (P2, P3)
│   ├── nodes/              # Pure node functions and reducers
│   ├── prompts/            # System prompts isolated by architectural role
│   ├── output_schemas/     # Strongly-typed Pydantic V2 schemas
│   ├── subagents/          # CompiledSubAgent adapters and subagent specs
│   ├── middlewares/        # Agent middleware (HITL gates, model fallbacks)
│   ├── models/             # Dynamic multi-tier LLM registry & cascade routing
│   ├── tools/              # Domain-specific tools (search, REPL, filesystem)
│   ├── retrieval/          # Document chunking, vector stores, and indices
│   ├── state/              # TypedDict schemas for LangGraph states
│   ├── data/               # Persistent storage engines (SQLite checkpointers)
│   └── utils/              # Shared security, sandboxing, and time-travel utilities
├── configs/                # Pure constant configuration values (timeouts, tiers)
├── agents/                 # Pre-assembled, ready-to-invoke agent definitions
└── apps/                   # Runnable application entry points and CLI loops

docs/                       # Official, active curriculum roadmap and handoff documentation
archive/                    # Historical archives and early design documentation
tests/                      # Comprehensive pytest verification suite
alireza/                    # Mentee interactive exploration and notebook playground
out/                        # Sandboxed execution artifacts (gitignored)
```

---

## ⚡ Key Engineering Standards & Production Patterns

- **Dynamic Model Cascade (`core/src/models/registry.py`):**  
  Multi-tier provider routing (`high`, `medium`, `low`) with automatic fallback chains across Gemini, OpenAI, and Anthropic. Includes an instant-response `LLM_TEST_MODE` routing all calls to ultra-fast tiers (`gemini-3.5-flash-lite`) during local testing.
- **Modern Human-In-The-Loop (HITL):**  
  Zero legacy workarounds. Implements first-class LangGraph `interrupt()` and `Command(resume=...)` gates for sensitive actions (code refactoring, shell execution, external side effects).
- **Time-Travel & Checkpointing (`core/src/data/sqlite_db.py`):**  
  Thread-safe, durable SQLite checkpointers (`checkpoints.db`) enabling session persistence, state audit inspection (`inspect_state_history`), and execution branch forking (`fork_from_checkpoint`).
- **Sandboxed Workspace Confinement (`core/src/utils/resolve_safe_path.py`):**  
  Deterministic project-root anchoring preventing path traversal attacks (`../`), ensuring all agent-generated files are strictly confined to `out/sandbox/`.
- **Zero-Ta'rof Rigorous Testing:**  
  Every agent, tool, and reducer is accompanied by unit tests. All changes must pass `uv run ruff check` and `uv run pytest` before completion.

---

## 🚀 Quickstart & Developer Workflow

### 1. Environment Setup

```bash
# Clone repository and install pinned dependencies via uv
uv sync

# Ensure .env is populated with required API keys (Gemini, OpenRouter/GapGPT, Tavily, LangSmith)
cp .env.example .env  # If creating a fresh environment
```

### 2. Running Agents & Applications

```bash
# Run P1 Web Research Agent
uv run python core/apps/research.py

# Run P2 RAG Insight Coordinator
uv run python core/apps/repo_insight.py

# Run P3 Code Review Application
uv run python alireza/code_review_app.py
```

### 3. Verification & Code Quality

```bash
# Run the entire test suite
uv run pytest -v

# Run fast linter and import checker
uv run ruff check core/ tests/

# Format code according to repository standards
uv run ruff format core/ tests/
```

---

## 📜 Documentation & History

- **Active Roadmap:** [`docs/ROADMAP.md`](docs/ROADMAP.md)
- **Active Operational Log:** [`docs/MENTOR_HANDOFF.md`](docs/MENTOR_HANDOFF.md)
- **P3 Master Architectural Study Guide:** [`study_guides/p3_code_review/MASTER_GUIDE.md`](study_guides/p3_code_review/MASTER_GUIDE.md)
- **Historical Archive:** [`archive/claude_initial_docs/`](archive/claude_initial_docs/)
