"""Finglish output guardrail: repair Perso-Arabic script in the assistant's final answer.

A prompt rule alone doesn't hold in long replies, so code checks the rule and a model repairs
it. Only the lines that leak are sent for repair, in chunks that run concurrently: rewriting a
whole long answer makes the rewriter leak new words of its own, a line it doesn't see can't be
damaged, and a malformed reply only costs its own chunk. A repaired line is kept only if it
comes back clean, with its original indentation. This is output quality, not security, so it
fails open: lines a pass can't repair stay as they were, and a warning is logged.
"""

import logging
import re
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, after_model
from langchain_core.messages import AIMessage
from langchain_core.runnables import Runnable
from langgraph.runtime import Runtime

from agentlab.models import llm_model
from agentlab.prompts.middlewares_prompt import FINGLISH_REWRITE_PROMPT
from agentlab.schemas.output.middlewares_output_schema import FinglishLines
from agentlab.utils.get_text_util import get_text

logger = logging.getLogger(__name__)

# Arabic, Arabic Supplement, Arabic Extended-A, and both Arabic Presentation Forms blocks.
_PERSO_ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
_MAX_PASSES = 2
_CHUNK_LINES = 20


def has_perso_arabic(text: str) -> bool:
    return _PERSO_ARABIC.search(text) is not None


def _keep_edges(original: str, repaired: str) -> str:
    """The repaired text with the original line's leading and trailing whitespace (markdown depends on it)."""
    stripped = original.strip()
    if not stripped:
        return original
    start = original.index(stripped)
    return original[:start] + repaired.strip() + original[start + len(stripped) :]


def _accept(lines: list[str], reply: Any) -> list[str]:
    """Each line replaced by its repair when the repair is clean; the whole chunk kept if the reply is malformed."""
    if not isinstance(reply, FinglishLines) or len(reply.lines) != len(lines):
        return lines
    return [
        _keep_edges(old, new) if new.strip() and not has_perso_arabic(new) else old
        for old, new in zip(lines, reply.lines, strict=True)
    ]


def make_finglish_output_guard(
    rewriter: Runnable[Any, FinglishLines] | None = None,
) -> AgentMiddleware:
    """Middleware that repairs the lines of a final answer that contain Perso-Arabic script.

    Args:
        rewriter: Runnable taking ``{"lines": ...}`` and returning ``FinglishLines``; defaults
            to the rewrite prompt on the ``opensource`` tier (cheap: this is a pure formatting
            repair that fails open, not a quality or safety gate).
    """
    chain = (
        rewriter
        if rewriter is not None
        else FINGLISH_REWRITE_PROMPT
        | llm_model.chain("opensource", structured=FinglishLines)
    )

    @after_model
    def finglish_output(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        """Runs only on a final answer (no tool calls) that actually leaks the script.

        The repaired answer reuses the message id, so ``add_messages`` replaces the leaked
        answer in the thread instead of appending, and later turns don't imitate it.
        """
        last_message = state["messages"][-1]
        if not isinstance(last_message, AIMessage) or last_message.tool_calls:
            return None
        text = get_text(last_message)
        lines = text.split("\n")
        for _ in range(_MAX_PASSES):
            leaked = [
                index for index, line in enumerate(lines) if has_perso_arabic(line)
            ]
            if not leaked:
                break
            chunks = [
                leaked[start : start + _CHUNK_LINES]
                for start in range(0, len(leaked), _CHUNK_LINES)
            ]
            replies = chain.batch(
                [
                    {"lines": "\n".join(lines[index] for index in chunk)}
                    for chunk in chunks
                ],
                return_exceptions=True,
            )
            for chunk, reply in zip(chunks, replies, strict=True):
                if isinstance(reply, Exception):
                    logger.warning("Finglish repair call failed: %s", reply)
                    continue
                for index, line in zip(
                    chunk,
                    _accept([lines[index] for index in chunk], reply),
                    strict=True,
                ):
                    lines[index] = line

        repaired_text = "\n".join(lines)
        if repaired_text == text:
            return None
        if still_leaking := sum(has_perso_arabic(line) for line in lines):
            logger.warning(
                "Finglish repair left %d line(s) with Perso-Arabic script",
                still_leaking,
            )
        return {
            "messages": [last_message.model_copy(update={"content": repaired_text})],
        }

    return finglish_output
