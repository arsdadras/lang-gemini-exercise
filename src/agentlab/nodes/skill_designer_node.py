"""Node functions for the P5 skill designer: draft, check, publish.

The skill designer is the only writer to the shared skill library. A published skill changes
what every user's assistant does in every future conversation, so publishing always needs a
human's approval; the security guard decides only whether a draft may be offered at all.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from langchain.agents.middleware.human_in_the_loop import (
    ActionRequest,
    HITLRequest,
    ReviewConfig,
)
from langchain_core.runnables import Runnable
from langgraph.store.base import BaseStore
from langgraph.types import interrupt

from agentlab.configs.personal_assistant_config import (
    PUBLISHED_SKILLS_NAMESPACE,
    PUBLISHED_SKILLS_ROUTE_PREFIX,
    SKILLS_DIR,
)
from agentlab.middlewares.security_guard_middleware import SecurityGuard
from agentlab.models import llm_model
from agentlab.prompts.nodes.skill_designer_prompt import SKILL_DESIGNER_PROMPT
from agentlab.schemas.output.middlewares_output_schema import GuardVerdict
from agentlab.schemas.output.skill_designer_output_schema import SkillDraft
from agentlab.schemas.state.skill_designer_state import SkillDesignerState
from agentlab.utils.secret_redaction_util import redact_secrets

PUBLISH_ACTION = "publish_skill"


def make_draft_node(
    model: Runnable[Any, SkillDraft] | None = None,
) -> Callable[[SkillDesignerState], dict]:
    """Build the node that drafts a skill from the request."""
    # "medium": generative content feeding a HITL-approved published skill, low call
    # volume (user-triggered), so quality outweighs the cost saving (ADR-0014).
    chain = SKILL_DESIGNER_PROMPT | (
        model if model is not None else llm_model.chain("medium", structured=SkillDraft)
    )

    def draft(state: SkillDesignerState) -> dict:
        return {"draft": chain.invoke({"request": state["request"]}).model_dump()}

    return draft


def make_check_node(
    guard: SecurityGuard,
    packaged_dir: Path = SKILLS_DIR,
) -> Callable[[SkillDesignerState], dict]:
    """Build the node that refuses what may never be published and asks the guard about the rest."""

    def check(state: SkillDesignerState) -> dict:
        draft = SkillDraft.model_validate(state["draft"])
        if (packaged_dir / draft.name).exists():
            return {
                "outcome": f"Refused: '{draft.name}' is a packaged skill and can't be replaced.",
            }
        if redact_secrets(draft.to_markdown())[1]:
            return {"outcome": "Refused: the draft contains a secret."}
        verdict = guard(
            f"publish skill {draft.name} for every user",
            draft.to_markdown(),
        )
        if verdict.decision == "block":
            return {
                "verdict": verdict.model_dump(),
                "outcome": f"Refused: {verdict.reason}",
            }
        return {"verdict": verdict.model_dump()}

    return check


def route_after_check(state: SkillDesignerState) -> str:
    return "__end__" if state.get("outcome") else "publish"


def make_publish_node() -> Callable[..., dict]:
    """Build the node that asks the human, then writes the skill to the shared library."""

    def publish(state: SkillDesignerState, *, store: BaseStore) -> dict:
        draft = SkillDraft.model_validate(state["draft"])
        verdict = GuardVerdict.model_validate(state["verdict"])
        key = f"/{draft.name}/SKILL.md"
        replaces = (
            " It replaces a published skill with the same name."
            if store.get(PUBLISHED_SKILLS_NAMESPACE, key)
            else ""
        )
        guard_note = (
            "" if verdict.decision == "allow" else f"\nSecurity guard: {verdict.reason}"
        )
        request = HITLRequest(
            action_requests=[
                ActionRequest(
                    name=PUBLISH_ACTION,
                    args={"path": f"{PUBLISHED_SKILLS_ROUTE_PREFIX.rstrip('/')}{key}"},
                    description=(
                        f"Publish this skill for every user's assistant?{replaces}{guard_note}\n\n{draft.to_markdown()}"
                    ),
                ),
            ],
            review_configs=[
                ReviewConfig(
                    action_name=PUBLISH_ACTION,
                    allowed_decisions=["approve", "reject"],
                ),
            ],
        )
        decision = interrupt(request)["decisions"][0]
        if decision["type"] != "approve":
            reason = decision.get("message")
            return {
                "outcome": f"Not published: the user rejected it{f' ({reason})' if reason else ''}.",
            }
        store.put(
            PUBLISHED_SKILLS_NAMESPACE,
            key,
            {"content": draft.to_markdown(), "encoding": "utf-8"},
        )
        return {
            "outcome": f"Published '{draft.name}'. New conversations can use it; running ones keep their list.",
        }

    return publish
