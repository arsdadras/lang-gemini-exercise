# AGENTS.md

Repo mechanics for any coding agent. Mentoring rules: `docs/MENTORING.md`.
Current state: `docs/MENTOR_HANDOFF.md`. Curriculum: `docs/ROADMAP.md`.

## Project

- `agentlab`: a production-track agentic AI curriculum (P1-P12) built on LangChain,
  LangGraph, and DeepAgents.
- Python >= 3.12 (developed on 3.14), managed with `uv`. Lint with `ruff`, test with `pytest`.
- Standard src layout: one import package, `src/agentlab`
  ([ADR-0002](docs/adr/0002-single-package-and-composition-root.md)).

## Layout

```
src/agentlab/
  apps/            CLI entry points and composition root (lab-* console scripts)
  agents/          agent factories (make_*_agent), no run loops
  subagents/       subagent specs and CompiledSubAgent adapters
  graphs/          StateGraph assembly (nodes wired to edges)
  nodes/           LangGraph node functions
  middlewares/     agent middleware factories
  tools/           tool factories
  retrieval/       vector index build and retriever
  models/          tier x provider model registry (llm_model)
  prompts/         prompt text by role (agents, subagents, nodes/, middlewares, template/)
  output_schemas/  Pydantic structured-output schemas
  state/           graph state and runtime context schemas
  data/            persistence adapters (SQLite checkpoints)
  utils/           shared helpers (sessions, sandbox, streaming, HITL loop, memory backend)
  configs/         plain constants: paths, model catalog, one module per project
  resources/       packaged non-code files (agent skills)
tests/             pytest suite
docs/              roadmap, handoff, mentoring contract, ADRs, design cards
study_guides/      write-ups of finished projects
examples/          sample inputs (e.g. code to review)
out/               runtime output, gitignored: sandbox/, state/checkpoints.db
alireza/           the mentee's private scratch area: never imported, edited, or read
```

## Dependency direction

`apps -> agents -> subagents, graphs -> nodes, middlewares, tools, retrieval -> models, prompts, output_schemas, state, data, utils -> configs`

Imports point downward only. `subagents` never import `agents`: the caller builds the agent
and injects it.

## Naming

Each module carries its role as a suffix, matching its directory: `<project>_<role>.py`
(`rag_graph.py`, `interpreter_agent.py`, `web_search_tool.py`, `models_config.py`,
`sqlite_db_data.py`, ...). Prompts under `prompts/nodes/` use `*_prompt.py`.

## Conventions

1. **Nothing happens at import time.** Modules define factories and constants. Apps call
   `load_dotenv()` inside `main()` and build the object graph there.
2. **Configuration.** Constants live in `configs/*_config.py`. Filesystem locations come only
   from `configs/paths_config.py`, never from the working directory. Model IDs live only in
   `configs/models_config.py`, and secrets are referenced by environment variable name.
3. **Models.**
   - Agents: `llm_model.get(tier, provider)` plus `make_model_fallback(tier, primary=provider)`
     ([ADR-0007](docs/adr/0007-built-in-model-fallback.md)).
   - Graph nodes and middleware: `llm_model.chain(tier, structured=Schema)`.
   - `LLM_TEST_MODE=true` routes every tier to `TEST_TIER`.
4. **Identity.** Per-user data uses `context_schema=UserContext`, and every call passes
   `context=UserContext(user_id=...)`. `thread_id` stays in `config["configurable"]`
   ([ADR-0003](docs/adr/0003-runtime-context-for-user-identity.md)).
5. **Graph state.** Nodes return partial updates and never mutate incoming state. Per-question
   scratch fields that have no reducer must be reset by the caller.
6. **Message text.** Read `.content` through `get_text(message)`; providers may return
   content blocks.
7. **Security** ([ADR-0005](docs/adr/0005-sandbox-secret-isolation.md)).
   - Shells and subprocesses running generated code get `build_sandbox_env()` only.
   - Agents whose filesystem backend exposes the repo deny `.env` reads.
   - Consequential tools require HITL.
8. **Typed boundaries.** Use Pydantic schemas for structured output and cross-agent contracts,
   and reuse existing schemas instead of passing loose dicts.
9. **Abstractions.** Reach for LangChain and DeepAgents built-ins before custom code. For
   shared abstractions, follow the rule of three: one consumer, keep it local; two, extract
   carefully; three, formalize.
10. **Console output.** Keep CLI output ASCII. Apps call `configure_utf8_stdout()` so model
    text can't crash a cp1252 Windows console.
11. **Top-level packages.** Adding a new package under `src/agentlab/` needs a reason recorded
    in an ADR or the handoff.

## Commands

```bash
uv sync                                         # install (editable) with dev tools
uv run pytest                                   # tests
uv run ruff check src tests                     # lint
uv run lab-research                             # P1 web researcher (approve each search)
uv run lab-rag                                  # P2 raw RAG graph (history / replay <i>)
uv run lab-repo-insight                         # P2 repo coordinator
uv run lab-code-review examples/buggy_bank_account.py   # P3 review pipeline
uv run lab-interpreter                          # P4 sandbox interpreter (approve execute)
uv run lab-coordinator                          # P4 multi-agent coordinator
uv run lab-assistant                            # P5 memory assistant
uv run python -m agentlab.retrieval.index_retrieval     # rebuild the RAG index (paced; minutes)
```

Apps that persist sessions accept a session mode as their first argument: `new`, `secret`,
`resume`, `step[N]`, `list`, or a custom thread name. `lab-code-review` also accepts a file path.

## Testing and verification

Policy: [ADR-0004](docs/adr/0004-testing-and-evaluation-policy.md).

- Deterministic code gets unit tests in the same change.
- Framework boundaries are tested with real framework objects and a scripted fake model
  (see `tests/test_personal_assistant.py`).
- Done means `uv run pytest` and `uv run ruff check src tests` are green, with real output shown.
- Never weaken or skip an existing test to get a change through.
- Verify library APIs before relying on them: the `docs-langchain` MCP server for
  LangChain/LangGraph/DeepAgents/LangSmith, Context7 or web search for other libraries, and the
  installed source under `.venv/Lib/site-packages/` for the pinned version.

## Gotchas (each one bit this repo)

- Generic top-level package names collide with dependencies (`schemas` vs chromadb), hence the
  single `agentlab` namespace.
- LangGraph `Runtime` has no `config`. Identity read from `configurable` inside a backend or
  store factory silently becomes a default.
- `RunnableWithFallbacks` has neither `bind_tools` nor `with_structured_output`. Bind structured
  output to each model *before* `with_fallbacks`. When every fallback fails, it re-raises the
  **primary's** error.
- `HumanInTheLoopMiddleware` matches exact tool names. Its `action_requests` entries are flat:
  `{name, args, description}`.
- `LocalShellBackend(virtual_mode=True)` confines the file tools, not shell commands. On Windows
  the shell needs `PATH` and `SYSTEMROOT` in its environment.
- A checkpointer snapshots graph state, not files on disk: time travel doesn't rewind the sandbox.
- A glob that matches nothing fails silently. Moved paths shrink a corpus without any error.
- `python-dotenv`'s `load_dotenv()` searches upward from the *calling file*, not from the working
  directory.
- Low-tier models sometimes claim a tool action they never took, and delegation reliability
  depends on explicit tool-choice guidance in the system prompt.

## Ask before

Schema or data migrations, `git push --force` or history rewrites, branch deletion, changes to
secrets or deployment config, and deleting or truncating data (tests included).
