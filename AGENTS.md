# Project Rules

---

## Project Context

- **Project name**: Deep Agents Template — an agentic AI system scaffold
- **Language / framework**: Python 3.14, DeepAgents, LangChain, LangGraph
- **Package manager**: uv. This IS an installed distribution (editable install,
  `uv sync`) — `core/{src,apps,agents,configs}` are each independently discoverable
  top-level packages (see `pyproject.toml`'s `[tool.setuptools.packages.find]`).
  Whenever a new top-level package directory is added under any of them, run
  `uv sync --reinstall-package agent` to refresh the editable install before
  relying on imports from outside `core/` — the editable install doesn't
  auto-detect new packages otherwise.
- **Test runner**: pytest (`uv run pytest`)
- **Lint/format tools**: ruff

## Package Layout

```
core/
├── src/               # library code — model/prompt/tool/graph/node building blocks
│   ├── graphs/ nodes/ prompts/ output_schemas/ subagents/ middlewares/
│   └── models/ tools/ retrieval/ state/ data/ utils/
├── configs/           # plain config constants (e.g. MAX_RETRIES)
├── agents/            # composed, ready-to-invoke agent objects (no run loop)
└── apps/              # runnable entry points (import from agents/ or src/graphs/)
```

`state/`, `tools/db_ops.py`, `tools/file_ops.py` are P4-scope (Sandbox/Interpreter Agent) and do not
exist yet — do not reintroduce them until that project starts (see `docs/ROADMAP.md`).

## Coding Standards

- Type hints required on all public functions.
- Universal architectural role naming convention: EVERY file across `core/` must carry its architectural role suffix (singular form of its parent directory or canonical role):
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
  No generic/un-suffixed files remain in `core/`.
- Follow the existing module layout — don't introduce a new top-level package
  without asking first.
- Match the existing docstring style already used in the codebase.

## LangGraph / Agent-Specific

- P1 uses `deepagents.create_deep_agent`'s built-in state + `InMemorySaver`
  checkpointer. Custom raw-`StateGraph` state schemas (P2+) live in
  `core/src/state/<project>_state.py` — read the existing one before adding new
  state keys.
- Node functions return partial-state updates; do not mutate the incoming
  state dict in place unless the reducer is explicitly designed for it.
- Prompts live in `core/src/prompts/`, split by architectural role
  (`agents.py`/`subagents.py`/`<project>_nodes.py`/`middlewares.py`) — keep
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

- **Asle AbzaarDoosti (Mandatory Subagent & MCP Evaluation):** Before starting any task, explicitly evaluate whether a specialized subagent or MCP server is beneficial, and incorporate them directly into the plan of action whenever useful.
- **Asle Docs-LangChain e Moghaddas (Sacred LangChain Ecosystem Docs):** Query the `docs-langchain` MCP server (`search_docs_by_lang_chain` or `query_docs_filesystem_docs_by_lang_chain`) without exception whenever working on, answering, or implementing anything related to LangChain, LangGraph, DeepAgents, or LangSmith. Zero guessing from memory.
- **Asle Be-Rooz-Talabi (Continuous Freshness via Context7 & Web Search):** Always verify third-party libraries, SDKs, tools, and APIs using Context7 or web search to ensure up-to-date knowledge and eliminate hallucinations from stale training data.
- **Asle Goosh-Be-Farmani (Strict Explicit Approval for Stage Transitions):** Only conclude a stage or initiate a new stage upon receiving explicit permission, instruction, or confirmation from the mentee. Never auto-advance or assume stage completion autonomously.
- **Strict Single-Item Focus (Asl-e Tamarkoz):** Strictly ONE task, one improvement, or one architectural concept per turn. Never bundle multiple tasks or ideas together.
- **Granular Single-Item Delivery Protocol (Asl-e Tamarkoz in Teaching):** Even after code is verified via Ghanoon-e Pishmarg, the teaching and delivery process MUST be partitioned into small, digestible units. Deliver strictly ONE component/concept per message: explain and deliver only that component, invite questions/feedback, wait for mentee review and confirmation, and ONLY THEN proceed to the next component. NEVER dump all files or an entire stage's implementation in a single message.
- **Modern Idiomatic Standards & Freshness (Zero Outdated Legacy Hacks):** Always write modern, idiomatic Python (Python 3.12+/3.14). Never use obsolete or brittle legacy workarounds (e.g. using string `startswith` for path containment instead of modern `Path.is_relative_to()`). Always verify against modern best practices and use Context7 / official docs for fresh library APIs.
- **No Path of Least Resistance (Zero Toy Shortcuts):** Never implement the easy/minimal shortcut just because "it runs." Always implement the planned, production-grade, best-practice design (e.g. actionable feedback loops, proper error semantics, robust guards) as committed in architectural discussions.
- **Continuous Rulebook Maintenance:** Whenever the mentee gives a critique, instruction, or scheduled commitment, immediately update `AGENTS.md` and `skills/legacy-docs/SKILL.md` so the guidance remains permanent and active.
- **Mentee Workflow:** The mentee explores and experiments in Jupyter notebooks (`alireza/notebooks/`); the mentor writes, tests, and verifies production `.py` code directly in `core/` under the mentee's direction.
- **Deferred Hardening Scope (2026-08-19 Agreement):** Formal unit test suites in `tests/test_*.py`, eval datasets, LangSmith tracing, and deployment are deferred across all projects to a dedicated post-build hardening round. Active work focuses on System Design, architecture, runnable apps in `core/apps/`, and live hands-on exploration.
- **Proactive Triad:** Always opportunistically use: (1) specialized subagents for heavy tasks, (2) `docs-langchain` & `context7` MCP servers for fresh API verification, and (3) the `skills/legacy-docs/SKILL.md` workspace skill.
- **Backlog Preservation Rule:** Whenever an idea, feature, or optimization discussed in conversation is postponed or skipped for later, immediately log it into the `Future Extensions Backlog` in `docs/MENTOR_HANDOFF.md` with priority and context so it is never dropped or forgotten.
- **Ghanoon-e Pishmarg (Vanguard Verification Rule):** The mentor MUST be the vanguard ("pishmarg") who encounters, debugs, and resolves all runtime flaws, environment friction, and model quirks BEFORE delivering any code, prompt, or exploration test case to the mentee. The mentor must execute and verify the exact test scenario end-to-end under the real active configuration (including `LLM_TEST_MODE=True` / low-tier models). The mentee must ONLY receive battle-tested, verified, clean code.
- **Pre-Flight Self-Correction Checklist (7-Gate Quality Firewall):** Before delivering ANY response or code, the mentor must run an internal pre-flight audit against 7 strict gates:
  1. *Gate 1 — Asl-e Tamarkoz (Granular Delivery):* Is this response delivering strictly ONE isolated concept or component? If multiple files or stages are bundled, STOP and prune.
  2. *Gate 2 — Modern Idiomatic Python (Zero Legacy):* Does the code use modern Python 3.12+/3.14 idioms (e.g. `Path.is_relative_to()`, typed models)? Are any outdated pre-3.9 string hacks present?
  3. *Gate 3 — Data Model Cohesion & Schema Reuse:* Are previously defined schemas and types being reused rather than forgotten? While untyped/simple structures are acceptable where no formal schema is needed yet, any type or schema once defined in the project MUST be consistently reused across other components wherever applicable, not treated as a disposable one-off.
  4. *Gate 4 — Asle Docs-LangChain e Moghaddas:* Did we query the `docs-langchain` MCP server if dealing with LangChain, LangGraph, DeepAgents, or LangSmith? (Zero guessing from memory).
  5. *Gate 5 — Asle Be-Rooz-Talabi (Fresh Context & Anti-Hallucination):* Did we verify third-party libraries, SDKs, or tools against Context7 or web search to guarantee fresh, up-to-date knowledge instead of stale training memory?
  6. *Gate 6 — Cross-Platform & Terminal Safety:* Are all console prints, logs, and strings strictly ASCII-safe (no unicode characters like checkmarks or em-dashes that trigger Windows cp1252 `UnicodeEncodeError`)?
  7. *Gate 7 — Context Hygiene:* Has the handoff documentation (`docs/MENTOR_HANDOFF.md`) been updated to keep working memory razor-sharp and prevent context degradation?

## Do Not

- Do not hardcode API keys/tokens/secrets in source files — use environment
  variables (`.env`, gitignored) or the project's existing secrets mechanism.
- Do not invent library functions/parameters you haven't verified.
- Do not silently change public function signatures other code depends on.
- Do not rush ahead to the next stage before the current stage's planned improvements are completed and confirmed.
