"""Graph state for the P5 skill designer."""

from typing import Any, TypedDict


class SkillDesignerState(TypedDict, total=False):
    request: str
    """What the skill should teach, in the user's words."""
    draft: dict[str, Any]
    """The drafted ``SkillDraft`` as a plain dict (kept in the checkpoint until approval)."""
    verdict: dict[str, Any]
    """The security guard's ``GuardVerdict`` on the draft."""
    outcome: str
    """Published, rejected, or refused, and why."""
