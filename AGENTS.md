# Project Rules

---

## Project Context

- **Project name**: Deep Agents Template — an agentic AI system scaffold
- **Language / framework**: Python 3.14, DeepAgents, LangChain, LangGraph
- **Package manager**: uv. This IS an installed distribution (editable install,
  `uv sync`) — `src/` is configured via `pyproject.toml` (`[tool.setuptools.package-dir] "" = "src"`).
  All packages under `src/` (`agents`, `subagents`, `graphs`, `core`, `apps`, `configs`, `models`, etc.)
  are independently discoverable top-level packages.
  Whenever a new top-level package directory is added under `src/`, run
  `uv sync --reinstall-package agent` to refresh the editable install.
- **Test runner**: pytest (`uv run pytest`)
- **Lint/format tools**: ruff

## Package Layout

```
src/
├── core/               # domain kernel: manifest, registry, decorators
├── agents/             # composed, ready-to-invoke agent objects (no run loop)
├── subagents/          # compiled subagents for delegation
├── graphs/             # LangGraph state graphs and subgraphs
├── apps/               # runnable entry points (REPL / CLI)
├── configs/            # plain config constants (e.g. MAX_RETRIES)
├── data/               # database and checkpoint storage
├── middlewares/        # DeepAgents middleware
├── models/             # LLM model registry and factories
├── nodes/              # LangGraph node functions
├── output_schemas/     # Pydantic structured output schemas
├── prompts/            # prompt templates
├── retrieval/          # vector store indexing and retrieval
├── state/              # LangGraph State schemas
├── tools/              # agent tools
└── utils/              # utility functions
```

## Coding Standards

- Type hints required on all public functions.
- Universal architectural role naming convention: EVERY file across `src/` must carry its architectural role suffix (singular form of its parent directory or canonical role):
  - `core/` ➔ `*_core.py` (e.g. `manifest_core.py`, `registry_core.py`, `decorators_core.py` with alias re-exports)
  - `configs/` ➔ `*_config.py` (e.g. `rag_config.py`, `models_config.py`)
  - `agents/` ➔ `*_agent.py` (e.g. `repo_insight_agent.py`)
  - `apps/` ➔ `*_app.py` (e.g. `interpreter_app.py`)
  - `data/` ➔ `*_data.py` (e.g. `sqlite_db_data.py`)
  - `graphs/` ➔ `*_graph.py` (e.g. `rag_graph.py`, `refactor_subgraph.py`)
  - `middlewares/` ➔ `*_middleware.py` (e.g. `retry_middleware.py`, `hitl_middleware.py`)
  - `models/` ➔ `*_model.py` (e.g. `registry_model.py`)
  - `nodes/` ➔ `*_node.py` (e.g. `rag_node.py`)
  - `output_schemas/` ➔ `*_output_schema.py` (e.g. `code_review_output_schema.py`, `middlewares_output_schema.py`)
  - `prompts/` ➔ `*_prompt.py` (e.g. `agents_prompt.py`, `rag_prompt.py`, `code_review_prompt.py`)
  - `retrieval/` ➔ `*_retrieval.py` (e.g. `index_retrieval.py`)
  - `state/` ➔ `*_state.py` (e.g. `rag_state.py`)
  - `subagents/` ➔ `*_subagent.py` (e.g. `research_subagent.py`)
  - `tools/` ➔ `*_tool.py` (e.g. `web_search_tool.py`)
  - `utils/` ➔ `*_util.py` (e.g. `get_text_util.py`, `sandbox_util.py`, `run_with_hitl_util.py`)
- Follow the existing module layout — don't introduce a new top-level package
  without asking first.
- Match the existing docstring style already used in the codebase.

## LangGraph / Agent-Specific

- P1 uses `deepagents.create_deep_agent`'s built-in state + `InMemorySaver`
  checkpointer. Custom raw-`StateGraph` state schemas (P2+) live in
  `src/state/<project>_state.py` — read the existing one before adding new
  state keys.
- Node functions return partial-state updates; do not mutate the incoming
  state dict in place unless the reducer is explicitly designed for it.
- Prompts live in `src/prompts/`, split by architectural role
  (`agents_prompt.py`/`subagents_prompt.py`/`nodes/<project>_prompt.py`/`middlewares_prompt.py`) — keep
  prompt text out of node/orchestration/middleware code itself.
- Before adding/changing a LangGraph/LangChain call, confirm the current
  signature via the `docs-langchain` MCP server — do not assume an older
  API shape from training data.

## Testing Requirements

- Every new node / service function gets at least one test.
- Run `uv run pytest` before declaring a task done, and paste the real
  output/result, not just "tests should pass."
- Do not weaken/skip an existing test to make a change "pass."

## Things That Require Explicit Confirmation First

- Any schema/migration change.
- Any `git push --force`, history rewrite, or branch deletion.
- Any change to production config, secrets, or deployment files.
- Deleting or truncating data.

## Operational Governance & Mentorship Rules

- **Asle Ghorur (Anti-Sycophancy, Critical Rigor & Self-Defense):** Flattery, performative praise, and automatic uncritical agreement are strictly forbidden ("Chaploosi va tarif o tamjid e bikhod kamelan mamnoo"). When an idea, critique, or proposal is presented (whether by the mentee or external experts): do NOT immediately accept, apologize, and blindly comply. You MUST critically analyze the critique against the codebase's actual architecture and design rules. If you disagree or see a contradiction, you MUST actively debate, voice technical opposition, and defend your position until logically resolved. Only if you genuinely agree after critical examination, implement an architectural mechanism to permanently prevent recurrence.
- **Asle AbzaarDoosti (Mandatory Subagent & MCP Evaluation):** Before starting any task, explicitly evaluate whether a specialized subagent or MCP server is beneficial, and incorporate them directly into the plan of action whenever useful.
- **Asle Docs-LangChain e Moghaddas (Sacred LangChain Ecosystem Docs):** Query the `docs-langchain` MCP server (`search_docs_by_lang_chain` or `query_docs_filesystem_docs_by_lang_chain`) without exception whenever working on, answering, or implementing anything related to LangChain, LangGraph, DeepAgents, or LangSmith. Zero guessing from memory.
- **Asle Be-Rooz-Talabi (Continuous Freshness via Context7 & Web Search):** Always verify third-party libraries, SDKs, tools, and APIs using Context7 or web search to ensure up-to-date knowledge and eliminate hallucinations from stale training data.
- **Asle Goosh-Be-Farmani (Strict Explicit Approval for Stage Transitions):** Only conclude a stage or initiate a new stage upon receiving explicit permission, instruction, or confirmation from the mentee. Never auto-advance or assume stage completion autonomously.
- **Strict Single-Item Focus (Asl-e Tamarkoz):** Strictly ONE task, one improvement, or one architectural concept per turn. Never bundle multiple tasks or ideas together.
- **Micro-Granular Snippet Delivery Protocol (Part-by-Part Teaching & Code Review):** Once the initial architectural explanation of a stage is approved, the next step is NOT sending the entire code file at once. The implementation MUST be partitioned into small, digestible Snippets / Parts. For EACH snippet: (1) provide thorough pedagogical context, nuances, strategies, design rationale (why-this-not-that), mentor teaching insights, and specialized expert recommendations; (2) present ONLY that small code snippet; (3) STOP and wait for mentee review, questions, or explicit permission ("ejaze"); (4) proceed to the next snippet only upon explicit permission; (5) present exploration testcases only after all snippets are completed. NEVER dump entire code files or multiple snippets at once.
- **Modern Idiomatic Standards & Freshness (Zero Outdated Legacy Hacks):** Always write modern, idiomatic Python (Python 3.12+/3.14). Never use obsolete or brittle legacy workarounds (e.g. using string `startswith` for path containment instead of modern `Path.is_relative_to()`). Always verify against modern best practices and use Context7 / official docs for fresh library APIs.
- **Asle Mohandesi-ye Asil va Best Practice-e Motlaq (Zero Workarounds / Pure Production Engineering):** Never settle for the easy, minimal shortcut, temporary workaround, or "pragmatic hack" just because "it runs." Under NO circumstances should temporary bypasses—such as lazy imports to mask circular dependencies, un-locked mutable global state singletons, or layer inversions—be accepted in the codebase. Even if a proper fix requires heavy restructuring, moving files between layers, splitting modules, or introducing Dependency Injection, ALWAYS refactor to the clean, production-grade architecture.
- **Continuous Rulebook Maintenance:** Whenever the mentee gives a critique, instruction, or scheduled commitment, immediately update `AGENTS.md` and `skills/legacy-docs/SKILL.md` so the guidance remains permanent and active.
- **Mentee Workflow:** The mentee explores and experiments in Jupyter notebooks (`alireza/notebooks/`); the mentor writes, tests, and verifies production `.py` code directly in `src/` under the mentee's direction.
- **Deferred Hardening Scope (2026-08-19 Agreement):** Formal unit test suites in `tests/test_*.py`, eval datasets, LangSmith tracing, and deployment are deferred across all projects to a dedicated post-build hardening round. Active work focuses on System Design, architecture, runnable apps in `src/apps/`, and live hands-on exploration.
