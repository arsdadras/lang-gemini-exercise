"""P5 domain workflow & specialist: ``run_personal_context`` and ``PERSONAL_CONTEXT_SPECIALIST_SPEC``."""

from typing import Any, overload

from langgraph.store.base import BaseStore

from agentlab.configs.personal_assistant_config import ASSISTANT_STORE_DB_PATH
from agentlab.data.sqlite_db_data import get_sqlite_store
from agentlab.schemas.input.personal_context_input_schema import PersonalContextInput
from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Specialist,
    SpecialistResult,
)
from agentlab.tools.user_context_tool import (
    PERSONAL_CONTEXT_SPECIALIST,
    read_user_context,
    render_personal_context,
)

DEFAULT_PERSONAL_CONTEXT_DESCRIPTION = (
    "Reads a user's long-term memory profile, facts, preferences, and active skills "
    "with secret redaction."
)


@overload
def run_personal_context(
    user_id: str,
    *,
    store: BaseStore | None = None,
) -> SpecialistResult[PersonalContextReport]: ...


@overload
def run_personal_context(
    store: BaseStore,
    user_id: str,
    /,
) -> SpecialistResult[PersonalContextReport]: ...


def run_personal_context(
    *args: Any, **kwargs: Any
) -> SpecialistResult[PersonalContextReport]:
    """Load ``user_id``'s stored context from ``store`` as a ``SpecialistResult[PersonalContextReport]``.

    Supports both ``run_personal_context(store, user_id)`` and ``run_personal_context(user_id, store=...)``.
    """
    store_or_user_id = args[0] if len(args) >= 1 else None
    pos_user_id = args[1] if len(args) >= 2 else kwargs.get("user_id")
    kw_store: BaseStore | None = kwargs.get("store")

    if isinstance(store_or_user_id, str):
        resolved_user_id = store_or_user_id
        resolved_store = (
            kw_store
            if kw_store is not None
            else get_sqlite_store(ASSISTANT_STORE_DB_PATH)
        )
    elif store_or_user_id is None and isinstance(pos_user_id, str):
        resolved_user_id = pos_user_id
        resolved_store = (
            kw_store
            if kw_store is not None
            else get_sqlite_store(ASSISTANT_STORE_DB_PATH)
        )
    else:
        if not isinstance(pos_user_id, str) or store_or_user_id is None:
            msg = "run_personal_context requires a user_id string"
            raise TypeError(msg)
        resolved_store = store_or_user_id
        resolved_user_id = pos_user_id

    return read_user_context(resolved_store, resolved_user_id)


PERSONAL_CONTEXT_SPECIALIST_SPEC = Specialist[
    PersonalContextInput, PersonalContextReport
](
    name=PERSONAL_CONTEXT_SPECIALIST,
    description=DEFAULT_PERSONAL_CONTEXT_DESCRIPTION,
    input_schema=PersonalContextInput,
    report_schema=PersonalContextReport,
    run=run_personal_context,
    render=render_personal_context,
)
