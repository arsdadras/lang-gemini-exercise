from typing import cast
from langchain.agents.middleware import after_model
from langchain_core.messages import AIMessage, ToolMessage
from prompts import _GROUNDEDNESS_PROMPT
from output_schemas import _GroundednessVerdict
from models import llm_model
from utils.get_text import get_text


@after_model
def response_groundedness(state, runtime):

    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage) or last_message.tool_calls:
        return None
    answer_text = get_text(last_message)

    tool_context = "\n\n".join(
        get_text(m) for m in state["messages"] if isinstance(m, ToolMessage)
    )
    if not tool_context:
        return None

    grader = llm_model.chain("lite", structured=_GroundednessVerdict)
    chain = _GROUNDEDNESS_PROMPT | grader

    verdict = cast(
        _GroundednessVerdict,
        chain.invoke({"context": tool_context, "answer": answer_text}),
    )
    if verdict.binary_score == "yes":
        return None

    disclaimer = AIMessage(
        content=(
            "I found a possible answer, but I couldn't verify it's fully "
            "supported by the retrieved information, so I'm not confident "
            "enough to state it."
        ),
        id=last_message.id,
    )
    return {"messages": [disclaimer]}
