# Deep Agents Template

A multi-project agentic AI curriculum built on [DeepAgents](https://github.com/deepagents), [LangChain](https://python.langchain.com/), and [LangGraph](https://langchain-ai.github.io/langgraph/). See [`docs/ROADMAP.md`](docs/ROADMAP.md) for the full project list and each project's growth path, and [`docs/MENTOR_HANDOFF.md`](docs/MENTOR_HANDOFF.md) for the current session-to-session status.

## Project Structure

```
core/
├── src/                # Library code — the parts that get composed into agents
│   ├── graphs/          # Raw LangGraph StateGraph assembly (per project)
│   ├── nodes/            # Node functions consumed by graphs/
│   ├── prompts/           # System prompts, split by architectural role
│   │   ├── agents.py       #   top-level agent persona prompts
│   │   ├── subagents.py     #   subagent persona prompts
│   │   ├── rag_nodes.py     #   P2 raw-graph node prompts
│   │   └── middlewares.py   #   middleware prompts
│   ├── output_schemas/     # Pydantic structured-output schemas, same role split
│   ├── subagents/         # SubAgent / CompiledSubAgent definitions
│   ├── middlewares/       # LangChain agent middleware (retry, HITL, guardrails)
│   ├── models/           # LLM model instances
│   ├── tools/            # Agent-callable tools (e.g. web_search)
│   ├── retrieval/        # Document ingestion + vector index (P2)
│   ├── state/            # LangGraph state schemas
│   ├── data/              # Static data/content
│   └── utils/             # Shared helpers
├── configs/             # Plain module-level config constants (e.g. MAX_RETRIES)
├── agents/              # Composed, ready-to-invoke agent objects — no run loop of
│                        # their own; assembled from src/'s model+prompt+tools+etc.
└── apps/                # Runnable entry points — import an agent from agents/ (or
                         # a graph from src/graphs/) and add the actual run loop.

skills/                 # DeepAgents Skill files (SKILL.md + optional helpers)
docs/                   # ROADMAP.md, MENTOR_HANDOFF.md — curriculum/session docs
tests/                  # pytest suite
alireza/                # Personal scratch/practice area — not part of the curriculum proper
```

`configs`, `agents`, `apps`, and everything under `src/` are siblings under `core/`, all
independently importable (see `pyproject.toml`'s `[tool.setuptools.packages.find]`) — moving any
one of them requires updating both that config and any `Path(__file__).resolve().parents[N]`-style
repo-root anchoring in code that depends on its own file depth.

## Setup

```bash
# Install dependencies (also installs this repo itself, editable, so core/{src,apps,agents,configs}
# resolve as top-level imports regardless of caller location)
uv sync

# Build the P2 vector index once, before running anything that queries it
uv run python core/src/retrieval/index.py

# Run an agent
uv run python core/apps/research.py      # P1 — web researcher
uv run python core/apps/rag.py           # P2 — raw RAG graph (debug/dev level)
uv run python core/apps/repo_insight.py  # P2 — full coordinator agent (product level)
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format core/ tests/

# Lint
uv run ruff check core/ tests/

# Refresh the editable install after adding a new top-level package under core/
# (core/src/<new>/, core/configs, core/agents, or core/apps) — see docs/MENTOR_HANDOFF.md
uv sync --reinstall-package agent
```
