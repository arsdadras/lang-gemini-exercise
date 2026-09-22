"""Graph state for the P5 memory consolidator."""

import operator
from typing import Annotated, Any, TypedDict


class MemoryConsolidationState(TypedDict, total=False):
    transcript: str
    """The finished conversation, as plain text (see ``format_transcript``)."""
    edits: list[dict[str, Any]]
    """Proposed ``MemoryEdit``s as plain dicts, kept in the checkpoint until the user reviews."""
    cursor: int
    """Index of the next edit to apply."""
    outcomes: Annotated[list[str], operator.add]
    """One line per edit: applied, skipped, blocked, or rejected."""
