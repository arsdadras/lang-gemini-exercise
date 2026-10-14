# AGENTS.md

Repo mechanics for any coding agent. Role and onboarding: [`GEMINI.md`](GEMINI.md),
[`mentor/README.md`](mentor/README.md), and [`library/`](library/README.md). Plan:
[`mentor/ROADMAP.md`](mentor/ROADMAP.md). Live state: [`mentor/STATE.md`](mentor/STATE.md). All
work happens on `main` ([git policy](library/engineering/git-policy.md)).

## Mentor Role & Repository Fork Context (Read First)

- **Isolated Fork:** This repository (`D:\Repos\lang-gemini-exercise`, remote
  `arsdadras/lang-gemini-exercise.git`) was forked on 2026-10-11 as a completely isolated copy of
  `lang_claude_exercise`. Never touch or reference `D:\Repos\lang_claude_exercise`.
- **Gemini is the Sole Mentor:** Up to commit `d697945` (2026-10-11), Claude Code acted as the
  Mentor and authored the historical records in `mentor/`, `library/`, `docs/`, and `.claude/`.
  From this fork onward, **Gemini (Antigravity) is the sole Mentor and Lead Architect**
  ([ADR-0028](docs/adr/0028-one-mentor-one-branch.md)) with full decision-making authority and full
  ownership of the codebase and all files under `mentor/`, `docs/`, and `library/`.
- **Session Start:** Read [`GEMINI.md`](GEMINI.md) and [`mentor/STATE.md`](mentor/STATE.md) first
  in every new session, and keep `mentor/STATE.md` updated as work progresses.

## Project

- `agentlab`: a production-track agentic AI curriculum (P1-P14) built on LangChain,
  LangGraph, and DeepAgents.
- Python >= 3.12 (developed on 3.14), managed with `uv`. Lint with `ruff`, type-check with `mypy`,
  test with `pytest`.
- Standard src layout: one import package, `src/agentlab`
  ([ADR-0002](docs/adr/0002-single-package-and-composition-root.md)).

## Layout

```
src/agentlab/
  apps/            CLI entry points and composition root (lab-* console scripts)
  workflows/       end-to-end domain workflows (`run_*` in `*_workflow.py`) and `Specialist`
                   definitions; sits above `agents/` and `graphs/` (ADR-0033)
  agents/          role agents (make_*_agent): one job, own harness, no run loops;
                   coordinators/ holds deep agents that orchestrate specialists (ADR-0030)
  subagents/       thin adapters turning each `Workflow` / `Specialist` into a subagent or tool
  graphs/          StateGraph assembly (nodes wired to edges)
  nodes/           LangGraph node functions
  middlewares/     agent middleware factories
  tools/           tool factories
  retrieval/       vector index build and retriever
  models/          tier x provider model registry (llm_model), decision models, and the
                   Jev model router (model_router)
  prompts/         prompt text by role (agents, subagents, nodes/, middlewares, template/)
  schemas/         typed contracts by role, not construction method: output/ (Pydantic
                   `*Report` contracts, `SpecialistResult`, `SpecialistName`), input/ (what a caller
                   asks of a specialist, e.g. `ResearchOptions`), state/ (graph-state
                   TypedDicts), context/ (runtime context, e.g. `UserContext`)
  data/            persistence adapters (SQLite checkpoints and Rung-0 store)
  utils/           shared helpers (sessions, sandbox, streaming, HITL loop, memory backend)
  configs/         plain constants: paths, model catalog, one module per project
  resources/       packaged non-code files (agent skills)
tests/             pytest suite
scripts/           repo tooling: docs lint, live smoke, session hook, and their tests
mentor/            the mentor's office: charter, state, log, roadmap, backlog, decisions,
                   risks, the research record, artifacts, sandbox (ignored)
library/           canonical knowledge: principles, architecture, engineering, teaching,
                   technology
archive/           retired documents, frozen
docs/              architecture, ADRs, design cards, and study guides (write-ups of finished
                   projects)
.github/           CI and Dependabot
.agents/           Antigravity workspace customizations: `hooks.json` and `skills/` (`/mentor`,
                   `/reviewer`, `/handoff`, `teach`, `decision-points`, `architecture-duality`)
.claude/           Synchronized skill mirrors for compatibility
examples/          sample inputs (e.g. code to review)
evals/             live eval-lite scenario sets (real models, run by hand, not by pytest)
out/               runtime output, gitignored: sandbox/, state/<app>_checkpoints.db
alireza/           the mentee's private scratch area: never imported, edited, or read
```

## Dependency direction

`apps -> workflows -> agents (including coordinators/), graphs, subagents -> nodes, middlewares, tools, retrieval -> models, prompts, schemas, data, utils -> configs`

Imports point downward only ([ADR-0033](docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)).
`workflows` sit above `agents` and `graphs` and own `run_<project>`. `subagents` wrap `workflows`
as subagent/tool adapters and never import `agents` directly unless injected.

## Naming

Each module carries its role as a suffix, matching its directory: `<project>_<role>.py`
(`research_workflow.py`, `rag_graph.py`, `interpreter_agent.py`, `web_search_tool.py`,
`models_config.py`, `sqlite_db_data.py`, ...). A subdirectory that exists purely to group
multiple files keeps that suffix too: `prompts/nodes/*_prompt.py`,
`schemas/output/*_output_schema.py`, `schemas/state/*_state.py`. `schemas/context/` names each
file for its specific context type (`user_context_schema.py`), since "context" isn't a project
name.

One word, one meaning: a term names the same thing in every file of a project, and two things
never share a name, even across a type, a field, a tool, and a CLI flag. Each project's terms
are listed in its design card (P1: [Terms](docs/design_cards/P1_research_agent.md#terms)).
Shared across projects: a **chunk** is a LangChain `Document` a retriever or search returned; a
**document** is P1's `SourceDocument`; a **deliverable** is a file the P4 interpreter writes to
`deliverables/`; **artifact** means only LangChain's `ToolMessage.artifact`; an **answer** is a
specialist's final text; a **report** is a checked, structured Pydantic final output
(`ResearchReport`, `RagReport`, `CodeReviewReport`, `InterpreterReport`,
`PersonalContextReport`); a **workflow** (`workflows/*_workflow.py`) is the Wave face of a
domain project (`run_<project>`) and a **specialist** (`Specialist[TInput, TReport]`) is its
Particle face ([ADR-0033](docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md));
an edit's operation is its **action** (`MemoryEdit.action`, `SideEffect.action`).

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
   - The model chosen by the task, not by hand: `model_router.chain(task, structured=Schema)` or
     `PROMPT | model_router.runnable(structured=Schema)` (a node) or `model_router.plan(task)`
     (an agent); Jev judges the task, code picks the tier
     ([ADR-0031](docs/adr/0031-jev-model-router-and-test-mode-ladder.md)). It sits beside
     `llm_model`; a call site that names its tier is unchanged.
   - `LLM_TEST_MODE=true` routes every tier to `TEST_TIER` (`LLM_TEST_PROFILE=<name>` picks a
     different one of the named `TEST_MODE_PROFILES`: a ladder `default`, `strong`, `strongest`,
     used one rung at a time; see ADR-0015 and ADR-0031).
   - Decision points (route, gate, grade, verify, recall, stop): the rule and the one standard
     in [decision-models.md](library/architecture/decision-models.md); the `decision_model`
     seam (`models/decision_model.py`) backs them ([ADR-0021](docs/adr/0021-decision-models-as-a-second-model-family.md)).
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
8. **Typed boundaries and the Wave-Particle Duality** ([ADR-0032](docs/adr/0032-typed-specialist-inputs.md),
   [ADR-0033](docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)).
   - Use Pydantic schemas for structured output and cross-agent contracts, and reuse existing
     schemas instead of passing loose dicts.
   - Every domain project (`P1`-`P5`+) exposes a `Workflow` (`run_<project>` in
     `workflows/<project>_workflow.py`) returning `SpecialistResult[TReport]` where `TReport` is
     a structured Pydantic `*Report` (never a raw `str` or `dict`), paired with a lightweight
     `Specialist[TInput, TReport]` descriptor.
   - An injected chain is typed by what it returns (`Runnable[dict[str, Any], OutputT]`).
9. **Abstractions.** Reach for LangChain and DeepAgents built-ins before custom code. For
   shared abstractions, follow the rule of three: one consumer, keep it local; two, extract
   carefully; three, formalize
   ([principles](library/governance/principles.md#3-scale-ready-seams-observed-abstractions)).
10. **Console output.** Keep CLI output ASCII. Apps call `configure_utf8_stdout()` so model
    text can't crash a cp1252 Windows console.
11. **Failures and retries** (`utils/failure_util.py`). One retry layer per call, chosen by
    what the call is:
    - Model calls are never wrapped in another retry: the provider SDK retries (honoring
      `Retry-After`), and the model fallback switches providers.
    - Any other external call (embeddings, web search, an HTTP API) gets exactly one retry
      layer with `retry_on=is_transient`: `TRANSIENT_RETRY` on its graph node, or
      `ToolRetryMiddleware` on an agent's tool.
    - One external dependency per node, so a node's retry never re-runs a model call.
    - A specialist boundary (`run_*`) turns an external failure into a `failed` envelope
      with `failure_reason`; anything `failure_kind` can't classify is a bug and raises.
12. **Top-level packages.** Adding a new package under `src/agentlab/` needs a reason recorded
    in an ADR (`workflows/` recorded in [ADR-0033](docs/adr/0033-wave-particle-duality-and-workflow-specialist-layer.md)).

## Commands

```bash
uv sync                                         # install (editable) with dev tools
uv run pytest                                   # tests
uv run ruff check src tests scripts             # lint
uv run ruff format src tests scripts            # format
uv run mypy src/agentlab                        # static type check
uv run python scripts/check_docs.py             # docs lint: links, anchors, library front matter
uv run python scripts/smoke_live.py             # live smoke of every integration (test mode)
uv run lab-research [--depth DEPTH] [--corpus FILE ...]   # P1 researcher (approve each outbound search)
uv run lab-rag                                  # P2 raw RAG graph (history / replay <i>)
uv run lab-repo-insight                         # P2 repo-insight coordinator
uv run lab-code-review examples/buggy_bank_account.py   # P3 review pipeline
uv run lab-interpreter                          # P4 sandbox interpreter (approve execute)
uv run lab-coordinator                          # P4 multi-agent coordinator
uv run lab-assistant                            # P5 memory assistant (/skill, /undo, /forget)
uv run lab-brief                                # P5 + P1 personalized research brief
uv run python evals/p5_memory_eval.py           # P5 eval-lite against real models (minutes)
uv run python -m agentlab.retrieval.index_retrieval     # rebuild the RAG index (paced; minutes)
```

Apps that persist sessions accept a session mode as their first argument: `new`, `secret`,
`resume`, `step[N]`, `list`, or a custom thread name. `lab-code-review` also accepts a file path.

## Testing and verification

Policy: [ADR-0004](docs/adr/0004-testing-and-evaluation-policy.md).

- Deterministic code gets unit tests in the same change.
- Framework boundaries are tested with real framework objects and a scripted fake model
  (see `tests/test_personal_assistant.py`).
- Done means `uv run pytest`, `uv run ruff check src tests scripts`, and `uv run mypy src/agentlab`
  are green, with real output shown. CI runs the same checks on every push and pull request.
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
- `HumanInTheLoopMiddleware` matches exact tool names; an `InterruptOnConfig` `when` predicate
  narrows it per call (by args). Its `action_requests` entries are flat:
  `{name, args, description}`.
- DeepAgents adds a `general-purpose` subagent to every deep agent; it gets the parent's tools
  but none of its middleware, so it skips approval gates, budgets, and guards. Build deep agents
  only through `utils/deep_agent_util.create_deep_agent`, which turns it off.
- `LocalShellBackend(virtual_mode=True)` confines the file tools, not shell commands. On Windows
  the shell needs `PATH` and `SYSTEMROOT` in its environment.
- A checkpointer snapshots graph state, not files on disk: time travel doesn't rewind the sandbox.
- A glob that matches nothing fails silently. Moved paths shrink a corpus without any error.
- `python-dotenv`'s `load_dotenv()` searches upward from the *calling file*, not from the working
  directory.
- Low-tier models sometimes claim a tool action they never took, and delegation reliability
  depends on explicit tool-choice guidance in the system prompt.
- Never delete or recreate a `.venv` while a session or the IDE may be using it: on Windows a
  held `ruff.exe` made a recreate fail halfway and left it broken. Each checkout has its own
  ([dev environment](library/engineering/dev-environment.md)).

## Ask before

Schema or data migrations, changes to secrets or deployment config, and deleting or truncating
data (tests included). Git follows the [git policy](library/engineering/git-policy.md): force
pushes and history rewrites are never done.
