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
├── models/              # LLM model registry and factories
├── nodes/              # LangGraph node functions
├── output_schemas/     # Pydantic structured output schemas
├── prompts/             # prompt templates
├── retrieval/           # vector store indexing and retrieval
├── state/               # LangGraph State schemas
├── tools/                # agent tools
└── utils/                # utility functions
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

**Canonical location: `skills/mentor-governance/SKILL.md`.** Every mentorship/communication/quality-gate rule (Asle Ghorur, Asle AbzaarDoosti, Asle Docs-LangChain e Moghaddas, Asle Be-Rooz-Talabi, Asle Goosh-Be-Farmani, Asle Tamarkoz, Micro-Granular Snippet Delivery, Ghanoon-e Pishmarg, Modern Idiomatic Standards, Asle Mohandesi-ye Asil va Best Practice-e Motlaq, Continuous Rulebook Maintenance, Backlog Preservation, the 15-Point Design Card requirement, Modern 2026 Model Tiers, Mentee Workflow, and the 8-Gate Quality Firewall) lives there, not here — read it before starting any mentoring/implementation session. This section used to restate all of it; that duplication was itself the reason rules drifted out of sync (see `docs/MENTOR_HANDOFF.md`, 2026-09-11 consolidation). If a rule changes, edit `skills/mentor-governance/SKILL.md` only.

**Curriculum shape:** the canonical curriculum definition is `docs/Agentic AI Curriculum Roadmap v2.md` (12 projects, P6/P12 capstones, Term E after P12) — `docs/ROADMAP.md` is the original 6-project draft, kept for history only. For live per-project status, read `docs/MENTOR_HANDOFF.md`'s session log, not a table in any skill/README file.
