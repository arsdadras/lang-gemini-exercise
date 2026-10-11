"""P5's boundary: ``read_user_context`` returns the specialist envelope; the tool serves agents."""

from langchain.tools import ToolRuntime, tool
from langchain_core.tools import BaseTool
from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import MEMORIES_ROUTE_PREFIX
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.utils.memory_backend_util import (
    MEMORIES_NAMESPACE_KIND,
    user_memory_namespace,
)
from agentlab.utils.secret_redaction_util import redact_secrets

PERSONAL_CONTEXT_SPECIALIST = "personal_context"
USER_CONTEXT_TOOL_NAME = "get_user_context"


def read_user_context(
    store: BaseStore,
    user_id: str,
) -> SpecialistResult[dict[str, str]]:
    """The user's memory files, keyed by path, read-only and with secrets redacted.

    A user without memory is still ``ok``: an empty context is an answer, not a failure.
    """
    items = sorted(
        store.search((user_id, MEMORIES_NAMESPACE_KIND), limit=100),
        key=lambda item: item.key,
    )
    files = {
        MEMORIES_ROUTE_PREFIX.rstrip("/") + item.key: redact_secrets(
            item.value.get("content", ""),
        )[0]
        for item in items
    }
    return SpecialistResult[dict[str, str]](
        specialist=PERSONAL_CONTEXT_SPECIALIST,
        status="ok",
        output=files,
        provenance=[Provenance(kind="memory", ref=path) for path in files],
    )


def render_files(files: dict[str, str]) -> str:
    if not files:
        return "No stored context for this user."
    return "\n\n".join(
        f'<file path="{path}">\n{content}\n</file>' for path, content in files.items()
    )


def make_user_context_tool() -> BaseTool:
    """Build the tool. The calling agent needs the P5 store and ``context=UserContext(...)``.

    What the caller may pass on is the caller's business: an agent that sends text outward
    (to the web, to another service) should also redact personal data from tool results,
    e.g. with ``PIIMiddleware(..., apply_to_tool_results=True)``.
    """

    @tool(USER_CONTEXT_TOOL_NAME)
    def get_user_context(runtime: ToolRuntime[UserContext]) -> str:
        """Get the user's stored profile and goals: preferences, constraints, and plans to tailor your work to."""
        user_id = user_memory_namespace(runtime)[0]
        if runtime.store is None:
            msg = "User context tool requires a store on the running agent"
            raise ValueError(msg)
        return read_user_context(runtime.store, user_id).to_text(render=render_files)

    return get_user_context
