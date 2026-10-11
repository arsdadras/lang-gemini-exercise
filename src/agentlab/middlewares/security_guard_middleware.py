"""Security guard: a classifier model that judges an action's content against a policy.

The guard is one structured-output call, not an agent: no tools and no conversation. It sees
only the action and the content being judged, so nothing else in the chat can argue it into a
softer verdict, and the same action always gets the same inputs. It never raises: any failure
becomes an ``ask`` verdict, so a broken guard adds friction instead of letting content through.
"""

import logging
from collections.abc import Callable
from typing import Any

from langchain_core.runnables import Runnable

from agentlab.models import llm_model
from agentlab.prompts.middlewares_prompt import SECURITY_GUARD_PROMPT
from agentlab.schemas.output.middlewares_output_schema import GuardVerdict

logger = logging.getLogger(__name__)

GUARD_UNAVAILABLE = GuardVerdict(
    decision="ask",
    category="guard_unavailable",
    reason="The security check could not run, so this change needs your approval.",
)

SecurityGuard = Callable[[str, str], GuardVerdict]


def make_security_guard(
    policy: str,
    classifier: Runnable[Any, GuardVerdict] | None = None,
) -> SecurityGuard:
    """Build ``guard(action, content) -> GuardVerdict`` for one policy.

    Args:
        policy: What to allow, ask about, or block (e.g. ``MEMORY_WRITE_POLICY``).
        classifier: Structured-output model returning ``GuardVerdict``; defaults to the
            ``low`` tier with its fallbacks. Kept on a paid tier deliberately: this is a
            security boundary, the ``low`` primary scored 8/8 on the memory-policy cases
            (EV-2026-09-25-laya-zero-shot, a small set), and GapGPT's opensource catalog has no
            verified adversarial-classification track record in this repo (ADR-0014).
    """
    model = (
        classifier
        if classifier is not None
        else llm_model.chain("low", structured=GuardVerdict)
    )
    chain = SECURITY_GUARD_PROMPT.partial(policy=policy) | model

    def guard(action: str, content: str) -> GuardVerdict:
        try:
            verdict = chain.invoke({"action": action, "content": content})
        except Exception:
            logger.warning(
                "Security guard failed; asking the user instead",
                exc_info=True,
            )
            return GUARD_UNAVAILABLE
        return verdict if isinstance(verdict, GuardVerdict) else GUARD_UNAVAILABLE

    return guard
