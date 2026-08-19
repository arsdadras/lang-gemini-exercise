# Project Rules

---

## Project Context

- **Project name**: Deep Agents Template — an agentic AI system scaffold
- **Language / framework**: Python 3.14, DeepAgents, LangChain, LangGraph
- **Package manager**: uv (application project, `package = false` — no installed
  distribution; `src/` is added to `sys.path` via `pythonpath` in pytest and via
  running scripts directly from `src/`)
- **Test runner**: pytest (`uv run pytest`)
- **Lint/format tools**: ruff

## Package Layout

```
src/
├── app.py          # Entry point
├── models/         # LLM instances
├── prompts/        # System prompt templates & builder
├── tools/          # Agent-callable tools
├── middleware/     # Pipeline middleware / hooks
├── subagents/      # Sub-agent definitions
├── schemas/        # Pydantic structured-output schemas
├── data/           # Static content (placeholder)
└── utils/          # Shared helpers
```

`state/`, `tools/db_ops.py`, `tools/file_ops.py` are P4-scope (Sandbox/Interpreter Agent) and do not
exist yet — do not reintroduce them until that project starts (see `ROADMAP.md`).

## Coding Standards

- Type hints required on all public functions.
- Follow the existing module layout — don't introduce a new top-level package
  without asking first.
- Match the existing docstring style already used in the codebase.

## LangGraph / Agent-Specific

- P1 uses `deepagents.create_deep_agent`'s built-in state + `InMemorySaver`
  checkpointer — no custom state schema yet. When a project needs one
  (P2+), put it in `src/state/schemas.py` and read it before adding new
  state keys.
- Node functions return partial-state updates; do not mutate the incoming
  state dict in place unless the reducer is explicitly designed for it.
- Prompts live in `src/prompts/` — keep prompt text out of
  node/orchestration code.
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
