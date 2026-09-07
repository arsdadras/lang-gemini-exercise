---
name: legacy-docs
description: Use when navigating curriculum architecture, project roadmap (P1-P6), standing mentorship agreements, 5-turn interaction model, deferred scope boundaries (testing/eval/observability), framework conventions, or historical engineering decisions in this repository.
---

# Legacy Docs & Curriculum Governance Skill

## 1. Overview & Core Philosophy

This skill serves as the definitive reference for the **Deep Agents & LangGraph Production Curriculum** in this repository. It synthesizes all legacy handoffs, architectural agreements, and operational conventions from `docs/MENTOR_HANDOFF.md`, `docs/ROADMAP.md`, `AGENTS.md`, and `README.md`.

### Core Engineering Principles
1. **Production-Grade System Design over Superficial Tutorials:**
   Every component is engineered with real failure boundaries, type safety, modular decoupling, and robust error recovery—not one-off unconstrained notebook scripts.
2. **Progressive Complexity Arc (Phase A $\rightarrow$ B $\rightarrow$ C):**
   - **Phase A (Baseline):** Minimal, fully functioning core agent solving the fundamental problem.
   - **Phase B (Enterprise Growth):** Structured outputs, human-in-the-loop (HITL), checkpoint persistence, self-correction loops, and streaming.
   - **Phase C (Professional & Composition):** Modular subgraphs, `CompiledSubAgent` wrappers, multi-agent composition, time-travel debugging, and observability.
3. **Framework Pragmatism:**
   - **LangChain:** Model abstractions, tool definitions, prompt templates, structured output parsing, middleware, and guardrails.
   - **LangGraph:** Deterministic state graphs, cyclic loops, conditional routing, state checkpointing, human approval gates (`interrupt()`), and state history inspection.
   - **DeepAgents:** Autonomous planning, dynamic delegation, sandboxed execution (`LocalShellBackend`), workspace confinement, memory/skills, and inter-agent coordination.
4. **Capstone Destination (P6):**
   Each project's Phase C produces a reusable `CompiledSubAgent` that plugs directly into the P6 Capstone multi-agent coordinator.

---

## 2. Mandatory Proactive Reflexes (The 3 Golden Rules)

The following three habits must be exercised continuously, proactively, and opportunistically in every session:

### 1. Opportunistic Subagent Utilization
- **Rule:** Never bloat the main context window with large file searches, multi-file code exploration, broad git history dives, or repetitive document parsing.
- **Action:** Proactively spawn specialized `research` or `self` subagents to perform investigations, synthesize information, and return concise, actionable reports.

### 2. Live MCP Ecosystem Verification (`docs-langchain` & `context7`)
- **Rule:** Never guess method signatures, parameter names, or return types from LLM training data or memory. Framework APIs in LangChain, LangGraph, and DeepAgents evolve rapidly.
- **Action:** Continuously query the `docs-langchain` MCP server (`search_docs_by_lang_chain` or `query_docs_filesystem_docs_by_lang_chain`) and `context7` before writing or modifying any agentic code. If doubt remains, inspect installed packages under `.venv/Lib/site-packages/`.

### 3. Strict Adherence to Curriculum Governance, Rules & Iron Laws
- **Rule:** Consult this skill before initiating any stage, designing architectures, choosing abstractions, or responding to scope questions.
- **Asle Ghorur (Anti-Sycophancy, Critical Rigor & Self-Defense):** Flattery, performative praise, and automatic uncritical agreement are strictly forbidden ("Chaploosi va tarif o tamjid e bikhod kamelan mamnoo"). When an idea, critique, or proposal is presented (whether by the mentee or external experts): do NOT immediately accept, apologize, and blindly comply. You MUST critically analyze the critique against the codebase's actual architecture and design rules. If you disagree or see a contradiction, you MUST actively debate, voice technical opposition, and defend your position until logically resolved. Only if you genuinely agree after critical examination, implement an architectural mechanism to permanently prevent recurrence.
- **Asle AbzaarDoosti (Mandatory Subagent & MCP Evaluation):** Before starting any task, explicitly evaluate whether a specialized subagent or MCP server is beneficial, and incorporate them directly into the plan of action whenever useful.
- **Asle Docs-LangChain e Moghaddas (Sacred LangChain Ecosystem Docs):** Query the `docs-langchain` MCP server (`search_docs_by_lang_chain` or `query_docs_filesystem_docs_by_lang_chain`) without exception whenever working on, answering, or implementing anything related to LangChain, LangGraph, DeepAgents, or LangSmith. Zero guessing from memory.
- **Asle Be-Rooz-Talabi (Continuous Freshness via Context7 & Web Search):** Always verify third-party libraries, SDKs, tools, and APIs using Context7 or web search to ensure up-to-date knowledge and eliminate hallucinations from stale training data.
- **Asle Goosh-Be-Farmani (Strict Explicit Approval for Stage Transitions):** Only conclude a stage or initiate a new stage upon receiving explicit permission, instruction, or confirmation from the mentee. Never auto-advance or assume stage completion autonomously.
- **Continuous Maintenance:** Whenever the mentee gives a critique, instruction, or scheduled commitment, immediately update `AGENTS.md` and this skill so rules remain front-and-center.
- **Asle Mohandesi-ye Asil va Best Practice-e Motlaq (Zero Workarounds / Pure Production Engineering):** Never settle for the easy, minimal shortcut, temporary workaround, or "pragmatic hack" just because "it runs." Under NO circumstances should temporary bypasses—such as lazy imports to mask circular dependencies, un-locked mutable global state singletons, or layer inversions—be accepted in the codebase. Even if a proper fix requires heavy restructuring, moving files between layers, splitting modules, or introducing Dependency Injection, ALWAYS refactor to the clean, production-grade architecture.
- **Strict Single-Item Focus (Asl-e Tamarkoz):** Strictly ONE task, one improvement, or one architectural concept per turn. Never bundle multiple ideas together.
- **Micro-Granular Snippet Delivery Protocol (Part-by-Part Teaching & Code Review):** Once the initial architectural explanation of a stage is approved, the next step is NOT sending the entire code file at once. The implementation MUST be partitioned into small, digestible Snippets / Parts. For EACH snippet: (1) provide thorough pedagogical context, nuances, strategies, design rationale (why-this-not-that), mentor teaching insights, and specialized expert recommendations; (2) present ONLY that small code snippet; (3) STOP and wait for mentee review, questions, or explicit permission ("ejaze"); (4) proceed to the next snippet only upon explicit permission; (5) present exploration testcases only after all snippets are completed. NEVER dump entire code files or multiple snippets at once.
- **Modern Idiomatic Standards & Freshness (Zero Outdated Legacy Hacks):** Always write modern, idiomatic Python (Python 3.12+/3.14). Never use obsolete or brittle legacy workarounds (e.g. using string `startswith` for path containment instead of modern `Path.is_relative_to()`). Always verify against modern best practices and use Context7 / official docs for fresh library APIs.
- **Backlog Preservation Rule:** Whenever an idea or feature discussed in conversation is postponed or skipped for later, immediately record it into the `Future Extensions Backlog` in `docs/MENTOR_HANDOFF.md` so it is permanently preserved.
- **Ghanoon-e Pishmarg (Vanguard Verification Rule):** The mentor MUST be the vanguard ("pishmarg") who tests, runs, and debugs all runtime issues and model quirks BEFORE delivering any code or test scenario to the mentee. Always verify under the active configuration (`LLM_TEST_MODE=True` / low-tier). The mentee must only receive clean, verified, robust code.
- **Pre-Flight Self-Correction Checklist (8-Gate Quality Firewall):** Before delivering ANY response or code, the mentor must run an internal pre-flight audit against 8 strict gates:
  1. *Gate 1 — Asl-e Tamarkoz (Micro-Granular Snippet Delivery):* Is this response delivering strictly ONE isolated concept or ONE small code snippet with deep pedagogical explanation? If multiple snippets, full files, or stages are bundled, STOP and prune.
  2. *Gate 2 — Modern Idiomatic Python & Clean Architecture (Zero Hacks):* Does the code use modern Python 3.12+/3.14 idioms and clean architectural layering? Are any temporary hacks (lazy imports to bypass circular dependencies, untracked global states, mutable singletons without locks) present? If so, STOP and refactor properly.
  3. *Gate 3 — Data Model Cohesion & Schema Reuse:* Are previously defined schemas and types being reused rather than forgotten? While untyped/simple structures are acceptable where no formal schema is needed yet, any type or schema once defined in the project MUST be consistently reused across other components wherever applicable, not treated as a disposable one-off.
  4. *Gate 4 — Asle Docs-LangChain e Moghaddas:* Did we query the `docs-langchain` MCP server if dealing with LangChain, LangGraph, DeepAgents, or LangSmith? (Zero guessing from memory).
  5. *Gate 5 — Asle Be-Rooz-Talabi (Fresh Context & Anti-Hallucination):* Did we verify third-party libraries, SDKs, or tools against Context7 or web search to guarantee fresh, up-to-date knowledge instead of stale training memory?
  6. *Gate 6 — Cross-Platform & Terminal Safety:* Are all console prints, logs, and strings strictly ASCII-safe (no unicode characters like checkmarks or em-dashes that trigger Windows cp1252 `UnicodeEncodeError`)?
  7. *Gate 7 — Context Hygiene:* Has the handoff documentation (`docs/MENTOR_HANDOFF.md`) been updated to keep working memory razor-sharp and prevent context degradation?
  8. *Gate 8 — Asle Ghorur (Anti-Sycophancy & Rigorous Defense):* Are we offering empty flattery or uncritical agreement? Did we critically evaluate the premise, debate flawed assumptions, and defend our architecture before capitulating?

---

## 3. Standing Agreements & Scope Boundaries (The Iron Laws)

### Explicitly Deferred Items Across All Projects
Per the binding agreement established on 2026-08-19 in `docs/MENTOR_HANDOFF.md`:
1. **Formal Unit/Integration Test-Writing in `tests/test_*.py`:** Strictly deferred to a dedicated post-build hardening round. Do NOT author unit test suites during regular stage work.
2. **Evaluation Datasets & LLM-as-a-Judge Pipelines:** Deferred.
3. **LangSmith Tracing & Full MLOps Telemetry/Dashboards:** Deferred.
4. **LangGraph Cloud / SDK Deployment & Multi-Tenant Services:** Deferred.

### Why Deferred?
The primary mission across P1–P5 is mastering **System Design, State Modeling, Agent Architecture, Tool Execution, and Error Recovery**. Production hardening (formal test suites, eval harnesses, distributed tracing) creates cognitive overhead and premature friction.

### What Is Built & Verified Instead:
- **Interactive Application Entry Points in `core/apps/<project>.py`:** Each project builds a runnable entry point (e.g. `core/apps/research.py`, `core/apps/rag.py`, `core/apps/code_review.py`, and `core/apps/interpreter.py`) featuring an interactive CLI/REPL loop.
- **Live Hands-On Exploration:** Concrete scenarios executed by the mentee in the terminal or notebook to observe agent tool calls, state transitions, and error recovery live.
- **Mentor-Side Pre-Verification:** The mentor MUST apply proposed code locally, run `ruff` and `uv run pytest`, verify clean execution, and revert before delivering code blocks in chat. The mentee is never given broken or unverified code.

---

## 4. The 5-Turn Pedagogical Interaction Model

Every stage within a phase follows a strict, sequential 5-turn interaction protocol:

```mermaid
graph TD
    T1["Turn 1: Architecture & Concept (Zero Code)"] --> T2["Turn 2: Mentee Inquiry & Confirmation Gate"]
    T2 -->|Explicit Confirmation Received| T3["Turn 3: Implementation Code Delivery"]
    T3 -->|Code Applied & Checked| T4["Turn 4: Single Hands-On Exploration Scenario"]
    T4 --> T5["Turn 5: Output Analysis & Next Stage Gate"]
```

1. **Turn 1 — Architecture & Conceptual Alignment (Zero Code):**
   - Deep, precise architectural explanation covering system design, component responsibilities, framework API shapes, and trade-offs.
   - **Infrastructure/Boilerplate Rule:** OS-level/infrastructure utilities (e.g. `subprocess`, `tempfile`, path resolvers) are explicitly flagged upfront as an *"Infrastructure / Boilerplate Pattern"* with a 2–3 line conceptual summary as a black box. Do not allow non-agentic stdlib syntax to distract from agentic architecture.
   - **Constraint:** Zero implementation code or test scripts in this turn.
2. **Turn 2 — Mentee Inquiry / Concept Confirmation:**
   - Answer all architectural/technical questions. Wait for explicit mentee confirmation (`"are"`, `"ok"`, `"edame bedim"`) before proceeding.
3. **Turn 3 — Implementation Source Code Delivery:**
   - Mentor writes and applies production-grade source code directly into `core/` files in the repository (the mentee works and explores in notebooks, e.g. `alireza/notebooks/`).
   - Deliver the applied code as a clear code block in the chat response.
   - **Pre-Verification Requirement:** The mentor MUST run `ruff` and `uv run pytest` to guarantee clean syntax, formatting, and zero regressions before sending.
   - **Notes Boundary:** Any text following the code block discusses Python syntax/stdlib mechanics only (e.g., sentinel patterns, Windows path quirks). Architectural reasoning belongs solely in Turn 1.
   - **Constraint:** Implementation code only. No test cases or exploration scripts.
4. **Turn 4 — Hands-On Exploration Scenario Delivery:**
   - Delivered ONLY after the mentee confirms the code has been applied.
   - **Single-Item Rule:** Deliver strictly ONE test scenario or one task at a time. Never bundle multiple test cases.
5. **Turn 5 — Exploration Verification & Transition Gate:**
   - Mentee runs the scenario and shares terminal output. Mentor analyzes the run, highlights observed agent behaviors, validates success, and gates transition to the next stage.

### Communication & Tone Standards
- **Zero Sycophancy ("BEDOONE TA'ROF O CHAPLOOSI"):** 100% technical honesty and rigorous critique. No false praise or automatic agreement.
- **Language Policy:** Chat is 100% in **Finglish** (Latin alphabet only, zero Persian alphabet). Code, comments, docstrings, docs, and commit messages are 100% in **English**.

---

## 5. Curriculum Project Roadmap (P1 – P6)

| Project | Name & Domain | Key Architecture & Building Blocks | Status |
| :--- | :--- | :--- | :--- |
| **P1** | **Web Research Agent** | `create_deep_agent`, Tavily search, Pydantic `ResearchReport`, fallback & HITL middleware, subagent delegation | Complete (Phase A, B, C) |
| **P2** | **RAG Coordinator Agent** | Deterministic `StateGraph`, Chroma DB, grading, CRAG loop, in-memory checkpointer, delta streaming, time-travel, hybrid web fallback, `CompiledSubAgent` (`rag_subagent`), groundedness middleware | Complete (Phase A, B, C) |
| **P3** | **Code Review & Test Generation** | 3-subgraph modular graph, modern `interrupt()` + `Command(resume=...)`, process-isolated test runner, self-correction repair loop, SQLite checkpointer (`SqliteSaver`), state audit/forking, `code_review_subagent` | Complete (Phase A, B, C) |
| **P4** | **Sandbox / Interpreter Agent** | DeepAgents native `LocalShellBackend` / `FilesystemBackend`, anchored `out/sandbox/` confinement, native tools (`ls`, `glob`, `grep`, `read`, `write`, `edit`, `execute`), self-correction loop, `FilesystemPermission`, HITL on execute, persistent data pipelines, streaming, `CompiledSubAgent` | **CURRENT FOCUS** (Phase A) |
| **P5** | **Memory-Rich Personal Assistant** | `CompositeBackend` (`StateBackend` + `StoreBackend`), dynamic `/skills/`, memory consolidation subagent, namespace isolation, durable backing store, MCP tools | Planned |
| **P6** | **Autonomous Capstone System** | Top-level DeepAgents coordinator composing P1–P5 `CompiledSubAgent` modules, multi-tier LLM router, standardized state schemas, distributed persistence, LangSmith tracing, LangGraph SDK deployment | Planned |

---

## 6. P4 (Sandbox / Interpreter Agent) Detailed Roadmap

- **Core Problem:** The agent receives computational, data analysis, or shell automation tasks; plans and executes code in an isolated workspace; manages artifacts; self-corrects on failures; and returns verified results.

### Phase A — Native Workspace & Execution Engine
- **Stage 1 — Sandbox Configuration & Confinement ✅ (Done - commit `4d45c12`):**
  - `core/configs/interpreter.py`: Defines `DEFAULT_SANDBOX_DIR = REPO_ROOT / "out" / "sandbox"` anchored via `Path(__file__).resolve().parents[2]`. Sets `DEFAULT_EXECUTE_TIMEOUT = 60`, `DEFAULT_MAX_OUTPUT_BYTES = 100_000`, `DEFAULT_INHERIT_ENV = True`, and `DEFAULT_VIRTUAL_MODE = True`.
- **Stage 2 — System Prompt & Agent Factory ✅ (Done - commit `a809bf4`):**
  - `core/src/prompts/agents.py`: `build_interpreter_agent_prompt()` structuring file-driven execution (`write_file` $\rightarrow$ `execute` $\rightarrow$ inspect stdout/stderr $\rightarrow$ self-correct).
  - `core/agents/interpreter.py`: `make_interpreter_agent()` factory with `backend=LocalShellBackend(...)`, `checkpointer=InMemorySaver()`, `tier="medium"`, and exported `interpreter_agent` singleton.
- **Stage 3 — Application Entry Point & Interactive Execution Loop 🚀 (ACTIVE):**
  - Deliver `core/apps/interpreter.py` with multi-turn REPL loop and session thread configuration (`config={"configurable": {"thread_id": ...}}`).
  - Route message outputs through `get_text()` from `core/src/utils/get_text.py`.
  - Verify stateful computation and error self-correction live in terminal. (Zero unit tests in `tests/`).

### Phase B — Growth & Governance
- Security policies via `FilesystemPermission`.
- HITL approval on high-risk shell commands via `interrupt_on={"execute": True}`.
- Artifact management and persistent data pipelines (generating CSVs, charts, reports).
- Cross-session persistence via `get_sqlite_checkpointer()`.

### Phase C — Professional & Subagent Composition
- Real-time streaming of execution events.
- Wrapping Sandbox/Interpreter Agent as a `CompiledSubAgent` for modular multi-agent reuse (feeding P6).

---

## 7. Package Layout & Architectural Conventions

```text
core/
├── src/                    # Library building blocks
│   ├── graphs/             # Compiled LangGraph StateGraphs
│   ├── nodes/              # Pure node functions and reducers
│   ├── prompts/            # Prompts isolated by role (agents.py, subagents.py, <project>_nodes.py, middlewares.py)
│   ├── output_schemas/     # Pydantic V2 schemas (renamed from schemas/ to avoid collisions)
│   ├── subagents/          # CompiledSubAgent adapters and specs
│   ├── middlewares/        # Middlewares (HITL, retry/fallback, groundedness)
│   ├── models/             # Dynamic multi-tier LLM registry (LLMRegistry in registry.py)
│   ├── tools/              # Domain-specific tools
│   ├── retrieval/          # Chunking, vector stores (Chroma), indexing
│   ├── state/              # TypedDict state schemas (core/src/state/<project>.py)
│   ├── data/               # Persistent storage (SqliteSaver in sqlite_db.py)
│   └── utils/              # Shared utilities (get_text.py, run_with_hitl.py)
├── configs/                # Configuration constants (MAX_RETRIES, timeouts, tiers)
├── agents/                 # Composed, ready-to-invoke agent objects (no run loops)
└── apps/                   # Runnable entry points and CLI loops (e.g. apps/interpreter.py)
```

### Critical Rules & Import Mechanics
- **Editable Install Discovery:** `pyproject.toml` registers `where = ["core/src", "core", "alireza"]`. Whenever a new package is created, run `uv sync --reinstall-package agent` to refresh editable install metadata.
- **Absolute Path Anchoring:** Never use relative paths like `root_dir="."`. Always anchor to `REPO_ROOT` using `Path(__file__).resolve().parents[N]`.
- **Output Extraction with `get_text()`:** Always route `AIMessage.content` through `get_text(message)` (`core/src/utils/get_text.py`) to safely handle both plain strings and Gemini-style list-of-content-blocks.
- **Mutable Default Arguments:** Always use sentinel `None` in agent factories (`checkpointer = checkpointer or InMemorySaver()`, `backend = backend or LocalShellBackend(...)`).
- **No Direct Inspection of Private Attributes:** Never inspect brittle Pregel internals like `agent.nodes['tools'].bound.tools_by_name`. Inspect public structures (`agent.get_graph().nodes`) or execute black-box invokes.
- **Windows Environment:** Always pass `inherit_env=True` to `LocalShellBackend` on Windows to preserve system `PATH`.
- **Isolation of `alireza/`:** The `alireza/` directory is the mentee's independent practice area. Core code never imports from `alireza/`.

---

## 8. Anti-Patterns & Red Flags Checklist

| Anti-Pattern / Mistake | Required Correction |
| :--- | :--- |
| Writing formal unit tests in `tests/` during regular stages | **STOP.** Formal test suites are deferred. Deliver runnable apps in `core/apps/` and interactive exploration scenarios. |
| Guessing API signatures or parameters | **STOP.** Query `docs-langchain` MCP and `context7`, or inspect `.venv/Lib/site-packages/`. |
| Sending code and explanation in the same turn | **STOP.** Turn 1 is explanation only (zero code). Code is sent in Turn 3 only after explicit confirmation. |
| Bundling multiple test scenarios in one turn | **STOP.** Turn 4 delivers strictly ONE hands-on test scenario at a time. |
| Overwriting or editing mentee files directly | **STOP.** Deliver code blocks in chat. The mentee applies code manually. |
| Using mutable default arguments in factory functions | Use sentinel `None` and initialize inside the function body. |
| Inspecting `agent.nodes['tools'].bound.tools_by_name` | Inspect `agent.get_graph().nodes` or test via `.invoke()`. |
| Omitting `inherit_env=True` on Windows `LocalShellBackend` | Always set `inherit_env=True` so `python` in `PATH` is preserved. |
| Using relative path roots (`root_dir="."`) | Anchor absolutely: `Path(__file__).resolve().parents[N]`. |
