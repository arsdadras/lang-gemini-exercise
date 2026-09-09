"""P2 repo-insight coordinator agent — answers questions about this repo by
delegating to `rag_subagent` and, when relevant, following the
`retrieval-strategy` skill's RAG-vs-filesystem decision policy.
"""

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from langgraph.checkpoint.memory import InMemorySaver

from middlewares.retry_middleware import retry_on_failure
from models import llm_model
from prompts import build_repo_insight_prompt
from subagents import rag_subagent

_REPO_ROOT = Path(__file__).resolve().parents[2]

backend = FilesystemBackend(root_dir=_REPO_ROOT)

repo_insight_agent = create_deep_agent(
    model=llm_model.get("low"),
    system_prompt=build_repo_insight_prompt(),
    checkpointer=InMemorySaver(),
    middleware=[retry_on_failure("low")],
    subagents=[rag_subagent],
    skills=["/skills/"],
    backend=backend,
)
