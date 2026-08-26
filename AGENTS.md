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

## Do Not

- Do not hardcode API keys/tokens/secrets in source files — use environment
  variables (`.env`, gitignored) or the project's existing secrets mechanism.
- Do not invent library functions/parameters you haven't verified.
- Do not silently change public function signatures other code depends on.
