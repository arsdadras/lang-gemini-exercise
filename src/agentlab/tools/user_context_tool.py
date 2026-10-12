"""P5's boundary: ``read_user_context`` returns the specialist envelope; the tool serves agents."""

from langchain.tools import ToolRuntime, tool
from langchain_core.tools import BaseTool
from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import (
    DEFAULT_USER_PROFILE_PATH,
    MEMORIES_ROUTE_PREFIX,
    PUBLISHED_SKILLS_NAMESPACE,
)
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SpecialistResult,
)
from agentlab.utils.memory_backend_util import (
    MEMORIES_NAMESPACE_KIND,
    user_memory_namespace,
)
from agentlab.utils.secret_redaction_util import redact_secrets

USER_CONTEXT_TOOL_NAME = "get_user_context"


def _extract_facts_and_preferences(
    files: dict[str, str],
) -> tuple[list[str], dict[str, str]]:
    facts: list[str] = []
    preferences: dict[str, str] = {}
    for content in files.values():
        for raw_line in content.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            cleaned = line.lstrip("-* ").strip()
            if not cleaned:
                continue
            facts.append(cleaned)
            if ":" in cleaned:
                key, _, value = cleaned.partition(":")
                if key.strip() and value.strip():
                    preferences[key.strip()] = value.strip()
    return facts, preferences


def read_user_context(
    store: BaseStore,
    user_id: str,
) -> SpecialistResult[PersonalContextReport]:
    """The user's memory files and structured context, read-only and with secrets redacted.

    A user without memory is still ``ok``: an empty context is an answer, not a failure.
    """
    clean_user_id = user_id.strip()
    items = sorted(
        store.search((clean_user_id, MEMORIES_NAMESPACE_KIND), limit=100),
        key=lambda item: item.key,
    )
    files = {
        MEMORIES_ROUTE_PREFIX.rstrip("/") + item.key: redact_secrets(
            item.value.get("content", ""),
        )[0]
        for item in items
    }
    profile_summary = files.get(DEFAULT_USER_PROFILE_PATH, "").strip()
    if not profile_summary and files:
        profile_summary = next(iter(files.values()), "").strip()
    facts, preferences = _extract_facts_and_preferences(files)
    published = store.search(PUBLISHED_SKILLS_NAMESPACE, limit=100)
    active_skills = sorted(
        {item.key.strip("/").split("/")[0] for item in published if item.key.strip("/")}
    )
    report = PersonalContextReport(
        profile_summary=profile_summary,
        relevant_facts=facts,
        active_preferences=preferences,
        active_skills=active_skills,
        files=files,
    )
    return SpecialistResult[PersonalContextReport](
        specialist="personal_context",
        status="ok",
        output=report,
        provenance=[Provenance(kind="memory", ref=path) for path in files],
    )


def render_personal_context(report: PersonalContextReport) -> str:
    """Format a ``PersonalContextReport`` as XML ``<file>`` blocks."""
    if not report.files:
        return "No stored context for this user."
    return "\n\n".join(
        f'<file path="{path}">\n{content}\n</file>'
        for path, content in report.files.items()
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
        return read_user_context(runtime.store, user_id).to_text(
            render=render_personal_context
        )

    return get_user_context
