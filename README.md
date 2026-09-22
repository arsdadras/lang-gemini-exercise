# agentlab

A hands-on curriculum for building production-track agentic AI systems with
[LangChain](https://python.langchain.com/), [LangGraph](https://langchain-ai.github.io/langgraph/),
and [DeepAgents](https://github.com/langchain-ai/deepagents). Each project grows a specialist
agent through three phases (domain core -> robust operation -> composable specialist). Two
capstones then compose the specialists into workflows.

## Curriculum

| Project | Focus | Status |
| :--- | :--- | :--- |
| P1 Research agent | DeepAgents orchestration, structured cited reports, HITL, subagents | Done |
| P2 RAG agent | Raw StateGraph, corrective retrieval, checkpoints, time travel, CompiledSubAgent | Done |
| P3 Code review and test generation | Subgraphs, sandboxed tests, self-correction, `interrupt()` approval | Done |
| P4 Sandbox interpreter | Shell backend, artifacts, durable sessions, multi-agent coordinator | Done |
| P5 Memory-rich assistant | Per-user durable memory with governed, reviewed writes; governed shared skills; context provider | Complete; taught again from B4 after R4 |
| Return pass | P1-P5 brought to one specialist contract, one upgrade each, before P6 | Planned |
| P6-P12 | Capstone I, documents (with vision), support ops, analytics, business actions, capstone II (P10 folded into P7) | Planned |

Full plan: [`docs/ROADMAP.md`](docs/ROADMAP.md). Live status:
[`docs/MENTOR_HANDOFF.md`](docs/MENTOR_HANDOFF.md).

## Quickstart

```bash
uv sync
uv run pytest
```

Create a `.env` in the repo root with the keys the apps use:

- `GOOGLE_API_KEY`
- `GAPGPT_API_KEY` and `GAPGPT_BASE_URL`
- `OPENROUTER_API_KEY`
- `TAVILY_API_KEY`
- optionally `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, and `LLM_TEST_MODE`

Then run any app:

```bash
uv run lab-research          # P1
uv run lab-repo-insight      # P2 (build the index first: uv run python -m agentlab.retrieval.index_retrieval)
uv run lab-code-review examples/buggy_bank_account.py   # P3
uv run lab-interpreter       # P4
uv run lab-coordinator       # P4 multi-agent
uv run lab-assistant         # P5
```

## Documentation

- [`AGENTS.md`](AGENTS.md): layout, conventions, commands, gotchas
- [`docs/ROADMAP.md`](docs/ROADMAP.md): curriculum
- [`docs/MENTOR_HANDOFF.md`](docs/MENTOR_HANDOFF.md): current state and backlog
- [`docs/MENTORING.md`](docs/MENTORING.md): how mentoring sessions run
- [`docs/adr/`](docs/adr/): architecture decisions
- [`docs/design_cards/`](docs/design_cards/): specialist contracts
- [`study_guides/`](study_guides/): write-ups of finished projects
