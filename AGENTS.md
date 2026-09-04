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
- Follow the existing module layout — don't introduce a new top-level package
  without asking first.
- Match the existing docstring style already used in the codebase.

## LangGraph / Agent-Specific

- P1 uses `deepagents.create_deep_agent`'s built-in state + `InMemorySaver`
  checkpointer. Custom raw-`StateGraph` state schemas (P2+) live in
  `core/src/state/<project>.py` — read the existing one before adding new
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

- **Strict Single-Item Focus (Asl-e Tamarkoz):** Strictly ONE task, one improvement, or one architectural concept per turn. Never bundle multiple tasks or ideas together.
- **No Path of Least Resistance (Zero Toy Shortcuts):** Never implement the easy/minimal shortcut just because "it runs." Always implement the planned, production-grade, best-practice design (e.g. actionable feedback loops, proper error semantics, robust guards) as committed in architectural discussions.
- **Continuous Rulebook Maintenance:** Whenever the mentee gives a critique, instruction, or scheduled commitment, immediately update `AGENTS.md` and `skills/legacy-docs/SKILL.md` so the guidance remains permanent and active.
- **Mentee Workflow:** The mentee explores and experiments in Jupyter notebooks (`alireza/notebooks/`); the mentor writes, tests, and verifies production `.py` code directly in `core/` under the mentee's direction.
- **Deferred Hardening Scope (2026-08-19 Agreement):** Formal unit test suites in `tests/test_*.py`, eval datasets, LangSmith tracing, and deployment are deferred across all projects to a dedicated post-build hardening round. Active work focuses on System Design, architecture, runnable apps in `core/apps/`, and live hands-on exploration.
- **Proactive Triad:** Always opportunistically use: (1) specialized subagents for heavy tasks, (2) `docs-langchain` & `context7` MCP servers for fresh API verification, and (3) the `skills/legacy-docs/SKILL.md` workspace skill.
- **Backlog Preservation Rule:** Whenever an idea, feature, or optimization discussed in conversation is postponed or skipped for later, immediately log it into the `Future Extensions Backlog` in `docs/MENTOR_HANDOFF.md` with priority and context so it is never dropped or forgotten.
- **Ghanoon-e Pishmarg (Vanguard Verification Rule):** The mentor MUST be the vanguard ("pishmarg") who encounters, debugs, and resolves all runtime flaws, environment friction, and model quirks BEFORE delivering any code, prompt, or exploration test case to the mentee. The mentor must execute and verify the exact test scenario end-to-end under the real active configuration (including `LLM_TEST_MODE=True` / low-tier models). The mentee must ONLY receive battle-tested, verified, clean code.

## Do Not

- Do not hardcode API keys/tokens/secrets in source files — use environment
  variables (`.env`, gitignored) or the project's existing secrets mechanism.
- Do not invent library functions/parameters you haven't verified.
- Do not silently change public function signatures other code depends on.
- Do not rush ahead to the next stage before the current stage's planned improvements are completed and confirmed.
