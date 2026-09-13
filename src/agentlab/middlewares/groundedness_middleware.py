"""Groundedness guardrail: replace a final answer that the tool outputs don't support."""

from typing import Any, cast

from langchain.agents.middleware import AgentState, after_model
from langchain_core.messages import AIMessage, ToolMessage
from langgraph.runtime import Runtime

from agentlab.models import llm_model
from agentlab.prompts.middlewares_prompt import GROUNDEDNESS_PROMPT
from agentlab.schemas.output.middlewares_output_schema import GroundednessVerdict
from agentlab.utils.get_text_util import get_text

_DISCLAIMER = (
    "I found a possible answer, but I couldn't verify it's fully supported by the "
    "retrieved information, so I'm not confident enough to state it."
)


@after_model
def response_groundedness(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """Grade the final answer against every tool output in the conversation.

    Runs only on a true final answer (an ``AIMessage`` with no tool calls) and only
    when tools produced context. An ungrounded answer is replaced in place: the
    disclaimer reuses the message id, so ``add_messages`` updates instead of appending.
    """
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or last_message.tool_calls:
        return None

    tool_context = "\n\n".join(
        get_text(message) for message in state["messages"] if isinstance(message, ToolMessage)
    )
    if not tool_context:
        return None

    grader = GROUNDEDNESS_PROMPT | llm_model.chain("low", structured=GroundednessVerdict)
    verdict = cast(
        GroundednessVerdict,
        grader.invoke({"context": tool_context, "answer": get_text(last_message)}),
    )
    if verdict.binary_score == "yes":
        return None
    return {"messages": [AIMessage(content=_DISCLAIMER, id=last_message.id)]}
