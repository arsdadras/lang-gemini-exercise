from dataclasses import dataclass
from typing import Any
from langchain_core.language_models import BaseChatModel
from pydantic import BaseModel


@dataclass
class ChainContext:
    prompt: str
    llm: BaseChatModel
    output_schema: BaseModel | None = None
