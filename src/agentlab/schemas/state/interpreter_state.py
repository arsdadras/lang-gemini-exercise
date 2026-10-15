"""Graph state for the P4 interpreter workflow graph."""

import operator
from typing import Annotated, NotRequired, TypedDict

from agentlab.schemas.output.interpreter_output_schema import InterpreterReport
from agentlab.schemas.output.specialist_output_schema import (
    Provenance,
    SideEffect,
    SpecialistResult,
)


class InterpreterState(TypedDict):
    """Overall state for the interpreter graph."""

    task: str
    report: NotRequired[InterpreterReport | None]
    problems: NotRequired[Annotated[list[str], operator.add]]
    provenance: NotRequired[Annotated[list[Provenance], operator.add]]
    side_effects: NotRequired[Annotated[list[SideEffect], operator.add]]
    result: NotRequired[SpecialistResult[InterpreterReport]]
