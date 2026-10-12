"""P5 domain workflow & specialist: ``run_personal_context`` and ``PERSONAL_CONTEXT_SPECIALIST``."""

from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import ASSISTANT_STORE_DB_PATH
from agentlab.data.sqlite_db_data import get_sqlite_store
from agentlab.schemas.input.personal_context_input_schema import PersonalContextInput
from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.output.specialist_output_schema import SpecialistResult
from agentlab.tools.user_context_tool import (
    read_user_context,
    render_personal_context,
)
from agentlab.workflows.specialist_workflow import Specialist

DEFAULT_PERSONAL_CONTEXT_DESCRIPTION = (
    "Reads a user's long-term memory profile, facts, preferences, and active skills "
    "with secret redaction."
)


def _default_personal_context_store() -> BaseStore:
    return get_sqlite_store(ASSISTANT_STORE_DB_PATH)


def run_personal_context(
    store: BaseStore,
    user_id: str,
) -> SpecialistResult[PersonalContextReport]:
    """Load ``user_id``'s stored context from ``store`` as a ``SpecialistResult[PersonalContextReport]``."""
    return read_user_context(store, user_id)


PERSONAL_CONTEXT_SPECIALIST = Specialist[PersonalContextInput, PersonalContextReport](
    name="personal_context",
    description=DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
    input_schema=PersonalContextInput,
    report_schema=PersonalContextReport,
    run=run_personal_context,
    render=render_personal_context,
    default_target=_default_personal_context_store,
)
