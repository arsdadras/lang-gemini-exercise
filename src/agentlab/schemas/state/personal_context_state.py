"""Graph state for the P5 personal context graph."""

import operator
from typing import Annotated, NotRequired, TypedDict

from agentlab.schemas.output.personal_context_output_schema import (
    PersonalContextReport,
)
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SideEffect,
    SpecialistResult,
)


class PersonalContextState(TypedDict):
    """Overall state for the personal context graph."""

    user_id: str
    report: NotRequired[PersonalContextReport | None]
    problems: NotRequired[Annotated[list[str], operator.add]]
    provenance: NotRequired[Annotated[list[Provenance], operator.add]]
    side_effects: NotRequired[Annotated[list[SideEffect], operator.add]]
    result: NotRequired[SpecialistResult[PersonalContextReport]]
