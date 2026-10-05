# agentlab

A hands-on curriculum for building production-track agentic AI systems with
[LangChain](https://python.langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/),
and [DeepAgents](https://github.com/langchain-ai/deepagents). Each project grows a specialist
agent through three phases (domain core -> robust operation -> composable specialist). Two
capstones then compose the specialists into workflows.

## Curriculum

| Project | Focus |
| :--- | :--- |
| P1 Research agent | DeepAgents orchestration, structured cited reports, HITL, subagents |
| P2 RAG agent | Raw StateGraph, corrective retrieval, checkpoints, time travel, CompiledSubAgent |
| P3 Code review and test generation | Subgraphs, sandboxed tests, self-correction, `interrupt()` approval |
| P4 Sandbox interpreter | Shell backend, artifacts, durable sessions, multi-agent coordinator |
| P5 Memory-rich assistant | Per-user durable memory with governed, reviewed writes; governed shared skills; context provider |
| Return pass | P1-P5 brought to one specialist contract, one upgrade each, before P6 |
| P6-P12 | Capstone I, documents (with vision), support ops, analytics, business actions, capstone II (P10 folded into P7) |
| Term E | Production platform: shared runtime, distributed execution, one vertical product |

Plan and order: [`mentor/ROADMAP.md`](mentor/ROADMAP.md). Live teaching status:
[`mentor/STATE.md`](mentor/STATE.md).

## Quickstart

```bash
uv sync
uv run pytest
```

Create a `.env` in the repo root with the keys the apps use:

- `GOOGLE_API_KEY` (also powers the `free` model tier directly, no GapGPT)
- `GAPGPT_API_KEY` and `GAPGPT_BASE_URL` (the `low`/`medium`/`high`/`opensource` model tiers)
- `TAVILY_API_KEY`
- optionally `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LLM_TEST_MODE`, and
  `LLM_TEST_PROFILE` (`default`/`reliable`/`local`, see ADR-0015)
- optionally `OLLAMA_HOST` (defaults to `http://127.0.0.1:11434`) for the `local` model tier —
  needs `ollama serve` running with the model already pulled

Then run any app:

```bash
uv run lab-research          # P1
uv run lab-repo-insight      # P2 (build the index first: uv run python -m agentlab.retrieval.index_retrieval)
uv run lab-code-review examples/buggy_bank_account.py   # P3
uv run lab-interpreter       # P4
uv run lab-coordinator       # P4 multi-agent
uv run lab-assistant         # P5
```

Every app and command, with session modes: [`AGENTS.md`](AGENTS.md#commands).

## Documentation

- [`CLAUDE.md`](CLAUDE.md): the one role (the mentor) and what every session loads
- [`AGENTS.md`](AGENTS.md): layout, conventions, commands, gotchas
- [`library/`](library/README.md): principles, architecture standards, git and dependency
  policies, development environment, pedagogy, technology
- [`mentor/`](mentor/README.md): the charter, state, roadmap, backlog, decisions, risks, and the
  research record
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): where the system stands and where it is going
- [`docs/adr/`](docs/adr/README.md): architecture decisions
- [`docs/design_cards/`](docs/design_cards/README.md): specialist contracts
- [`docs/study_guides/`](docs/study_guides/): write-ups of finished projects
