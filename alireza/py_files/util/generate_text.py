from typing import Any
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import BasePromptTemplate
from .get_text import get_text


def generate_response(
    prompt: BasePromptTemplate,
    model: BaseChatModel,
    inputs: dict[str, Any],
    schema: type[BaseModel] | None = None,
) -> Any:
    """Execute prompt + model chain with optional structured output parsing.

    - If schema is provided: binds schema and returns the parsed Pydantic object.
    - If schema is None: executes as plain text and returns str via get_text.
    """
    if schema is not None:
        structured_llm = model.with_structured_output(schema)
        chain = prompt | structured_llm
        return chain.invoke(inputs)

    chain = prompt | model
    response = chain.invoke(inputs)
    return get_text(response)
