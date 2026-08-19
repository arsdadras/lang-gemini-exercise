# Deep Agents Template

A multi-project agentic AI curriculum built on [DeepAgents](https://github.com/deepagents), [LangChain](https://python.langchain.com/), and [LangGraph](https://langchain-ai.github.io/langgraph/). See `ROADMAP.md` for the full project list and each project's growth path, and `MENTOR_HANDOFF.md` for the current session-to-session status.

## Project Structure

```
src/
├── app.py          # P1 entry point — assembles and runs the research agent
├── models/         # LLM model instances (Gemini via Google, GapGPT-routed OpenAI-compatible fallback)
├── prompts/        # System prompt template/builder + per-agent prompt functions
├── tools/          # Agent-callable tools — currently just web_search (Tavily)
├── middleware/     # Pipeline middleware (retry/fallback, HITL approval)
├── subagents/      # Sub-agent definitions
├── schemas/        # Pydantic structured-output schemas
├── data/           # Static data/content (placeholder, unused by P1)
└── utils/          # Shared helpers
```

`state/`, `tools/db_ops.py`, and `tools/file_ops.py` are **not part of P1** — they belong to later
projects on the roadmap (P4 Sandbox/Interpreter Agent) and will be reintroduced when that project starts.

## Setup

```bash
# Install dependencies
uv sync

# Run the agent
uv run python src/app.py
```

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format src/ tests/

# Lint
uv run ruff check src/ tests/
```
