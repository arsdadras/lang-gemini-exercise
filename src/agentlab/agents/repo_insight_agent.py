"""P2 repo-insight coordinator: answers questions about this repository.

Corpus-content questions go to ``rag_subagent``; exact-file questions use the
read-only filesystem tools. The packaged ``retrieval-strategy`` skill describes
when to pick which.
"""

from deepagents import CompiledSubAgent, create_deep_agent
from deepagents.backends import FilesystemBackend
from deepagents.middleware.filesystem import FilesystemPermission
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from agentlab.configs.paths_config import PROJECT_ROOT, SKILLS_RESOURCES_DIR
from agentlab.data.sqlite_db_data import get_sqlite_checkpointer
from agentlab.middlewares.fallback_middleware import make_model_fallback
from agentlab.models import llm_model
from agentlab.prompts.agents_prompt import build_repo_insight_prompt
from agentlab.subagents.rag_subagent import make_rag_subagent

# The backend's virtual root is the repository, so skill paths are repo-relative.
REPO_INSIGHT_SKILLS_PATH = (
    "/"
    + (SKILLS_RESOURCES_DIR / "repo_insight").relative_to(PROJECT_ROOT).as_posix()
    + "/"
)

# The whole repository is visible, so secrets are denied explicitly and the agent
# may not modify anything.
REPO_INSIGHT_PERMISSIONS = [
    FilesystemPermission(operations=["read"], paths=["/.env", "/.env.*"], mode="deny"),
    FilesystemPermission(operations=["write"], paths=["/**"], mode="deny"),
]


def make_repo_insight_agent(
    checkpointer: BaseCheckpointSaver | None = None,
    *,
    tier: str = "low",
    rag_subagent: CompiledSubAgent | None = None,
) -> CompiledStateGraph:
    """Build the repo-insight coordinator (read-only view of the repository)."""
    return create_deep_agent(
        model=llm_model.get(tier),
        system_prompt=build_repo_insight_prompt(),
        checkpointer=checkpointer
        if checkpointer is not None
        else get_sqlite_checkpointer(),
        middleware=[make_model_fallback(tier)],
        subagents=[rag_subagent if rag_subagent is not None else make_rag_subagent()],
        skills=[REPO_INSIGHT_SKILLS_PATH],
        backend=FilesystemBackend(root_dir=PROJECT_ROOT, virtual_mode=True),
        permissions=REPO_INSIGHT_PERMISSIONS,
    )
