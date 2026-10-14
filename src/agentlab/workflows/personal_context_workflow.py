"""P5 domain workflow & specialist: ``run_personal_context`` and ``PERSONAL_CONTEXT_SPECIALIST``."""

from typing import Any

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
from agentlab.workflows.base import Specialist

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


def make_personal_context_specialist(
    engine: BaseStore | None = None,
) -> Specialist[PersonalContextInput, PersonalContextReport]:
    """Create a Personal Context Specialist pre-bound to a store or lazy default."""

    def run_bound(
        task: PersonalContextInput | str | dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> SpecialistResult[PersonalContextReport]:
        resolved_engine = (
            engine if engine is not None else _default_personal_context_store()
        )
        data = task if task is not None else kwargs
        if isinstance(data, PersonalContextInput):
            user_id = data.user_id
        elif isinstance(data, dict):
            user_id = str(data["user_id"])
        else:
            user_id = str(data)
        return run_personal_context(resolved_engine, user_id)

    return Specialist[PersonalContextInput, PersonalContextReport](
        name="personal_context",
        description=DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
        input_schema=PersonalContextInput,
        report_schema=PersonalContextReport,
        run=run_bound,
        render=render_personal_context,
    )


PERSONAL_CONTEXT_SPECIALIST = make_personal_context_specialist()
