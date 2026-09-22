"""P5 as a context provider: a read-only tool other agents call for the user's stored context."""

from langchain.tools import ToolRuntime, tool
from langchain_core.tools import BaseTool

from agentlab.configs.personal_assistant_config import MEMORIES_ROUTE_PREFIX
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.utils.memory_backend_util import user_memory_namespace
from agentlab.utils.secret_redaction_util import redact_secrets

USER_CONTEXT_TOOL_NAME = "get_user_context"
NO_USER_CONTEXT = "No stored context for this user."


def make_user_context_tool() -> BaseTool:
    """Build the tool. The calling agent needs the P5 store and ``context=UserContext(...)``.

    It returns the user's memory files (profile and goals) as they are stored, read-only and
    with secrets redacted. What the caller may pass on is the caller's business: an agent that
    sends text outward (to the web, to another service) should also redact personal data from
    tool results, e.g. with ``PIIMiddleware(..., apply_to_tool_results=True)``.
    """

    @tool(USER_CONTEXT_TOOL_NAME)
    def get_user_context(runtime: ToolRuntime[UserContext]) -> str:
        """Get the user's stored profile and goals: preferences, constraints, and plans to tailor your work to."""
        items = runtime.store.search(user_memory_namespace(runtime), limit=100)
        files = [
            f'<file path="{MEMORIES_ROUTE_PREFIX.rstrip("/")}{item.key}">\n{item.value.get("content", "")}\n</file>'
            for item in sorted(items, key=lambda item: item.key)
        ]
        return redact_secrets("\n\n".join(files))[0] if files else NO_USER_CONTEXT

    return get_user_context
