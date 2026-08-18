"""System prompt templates and builders."""

from prompts.builder import build_system_prompt
from prompts.presets import Prompts, fib_prompts
from prompts.template import DEFAULTS, SYSTEM_PROMPT_TEMPLATE

__all__ = [
    "DEFAULTS",
    "SYSTEM_PROMPT_TEMPLATE",
    "Prompts",
    "build_system_prompt",
    "fib_prompts",
]
