# Deep Agents Template

An agentic AI system template built on [DeepAgents](https://github.com/deepagents) and [LangChain](https://python.langchain.com/).

## Project Structure

```
src/
├── app.py              # Entry point — assembles and runs the agent
├── models/             # LLM model instances (Gemini, Claude)
├── prompts/            # System prompt templates and builder
├── tools/              # Agent tools (file ops, DB ops)
├── state/              # State schemas and thread management
├── middleware/          # Middleware and hooks (extensible)
├── subagents/          # Sub-agent definitions (extensible)
├── data/               # Static data and content
└── utils/              # Shared utility functions
```

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
