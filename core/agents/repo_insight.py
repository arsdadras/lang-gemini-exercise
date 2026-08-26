"""P2 repo-insight coordinator agent — answers questions about this repo by
delegating to `rag_subagent` and, when relevant, following the
`retrieval-strategy` skill's RAG-vs-filesystem decision policy.
"""

from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from prompts import build_repo_insight_prompt
from models import llm_model
from subagents import rag_subagent
from middlewares.retry import retry_on_failure

_REPO_ROOT = Path(__file__).resolve().parents[2]

backend = FilesystemBackend(root_dir=_REPO_ROOT)

repo_insight_agent = create_deep_agent(
    model=llm_model.get("lite"),
    system_prompt=build_repo_insight_prompt(),
    checkpointer=InMemorySaver(),
    middleware=[retry_on_failure],
    subagents=[rag_subagent],
    skills=["/skills/"],
    backend=backend,
)
