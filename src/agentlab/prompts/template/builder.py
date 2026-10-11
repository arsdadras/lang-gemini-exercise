"""System prompt builder.

Assembles the final system prompt string by merging caller-supplied
overrides into :data:`~prompts.template.DEFAULTS` and
rendering :data:`~prompts.template.SYSTEM_PROMPT_TEMPLATE`.
"""

from __future__ import annotations

import re
from typing import Final

from .template import DEFAULTS, SYSTEM_PROMPT_TEMPLATE

_EMPTY_SECTION: Final[re.Pattern[str]] = re.compile(r"<(\w+)>\s*</\1>\n*")


def build_system_prompt(
    *,
    drop_empty_sections: bool = True,
    # --- identity ---
    assistant_name: str = DEFAULTS["assistant_name"],
    role: str = DEFAULTS["role"],
    domain: str = DEFAULTS["domain"],
    mission: str = DEFAULTS["mission"],
    context: str = DEFAULTS["context"],
    # --- user ---
    user_name: str = DEFAULTS["user_name"],
    user_background: str = DEFAULTS["user_background"],
    user_level: str = DEFAULTS["user_level"],
    user_goal: str = DEFAULTS["user_goal"],
    # --- language / style ---
    language_extra: str = DEFAULTS["language_extra"],
    tone: str = DEFAULTS["tone"],
    default_verbosity: str = DEFAULTS["default_verbosity"],
    style_extra: str = DEFAULTS["style_extra"],
    teaching_style: str = DEFAULTS["teaching_style"],
    # --- output ---
    output_format: str = DEFAULTS["output_format"],
    code_style: str = DEFAULTS["code_style"],
    # --- behaviour ---
    tools: str = DEFAULTS["tools"],
    constraints: str = DEFAULTS["constraints"],
    forbidden: str = DEFAULTS["forbidden"],
    clarification_policy: str = DEFAULTS["clarification_policy"],
    examples: str = DEFAULTS["examples"],
    success_criteria: str = DEFAULTS["success_criteria"],
    extra_rules: str = DEFAULTS["extra_rules"],
) -> str:
    """Render the system prompt, filling only the variables you care about.

    Args:
        drop_empty_sections: Remove XML sections whose content resolved to ``""``.
        assistant_name: Name shown in ``<identity>``. Default: ``"Assistant"``.
        role: One-line role description.
        domain: Primary technical domain(s).
        mission: What the assistant is here to do.
        context: Operating context / environment notes.
        user_name: How to address the user.
        user_background: User's background description.
        user_level: Expertise level (e.g. ``"advanced"``).
        user_goal: What the user is ultimately trying to achieve.
        language_extra: Extra rules appended to ``<language_policy>``.
        tone: Reply tone descriptor.
        default_verbosity: Verbosity when no mode code is present.
        style_extra: Extra rules appended to ``<style>``.
        teaching_style: Extra bullet appended inside T-mode rules.
        output_format: Instructions for output shape.
        code_style: Code conventions (language version, linting rules, etc.).
        tools: Tool-use instructions.
        constraints: Hard constraints the assistant must respect.
        forbidden: Things the assistant must never do.
        clarification_policy: When/how to ask clarifying questions.
        examples: Few-shot examples to inject.
        success_criteria: What a successful reply looks like.
        extra_rules: Catch-all for anything not covered above.
    """
    overrides = {
        "assistant_name": assistant_name,
        "role": role,
        "domain": domain,
        "mission": mission,
        "context": context,
        "user_name": user_name,
        "user_background": user_background,
        "user_level": user_level,
        "user_goal": user_goal,
        "language_extra": language_extra,
        "tone": tone,
        "default_verbosity": default_verbosity,
        "style_extra": style_extra,
        "teaching_style": teaching_style,
        "output_format": output_format,
        "code_style": code_style,
        "tools": tools,
        "constraints": constraints,
        "forbidden": forbidden,
        "clarification_policy": clarification_policy,
        "examples": examples,
        "success_criteria": success_criteria,
        "extra_rules": extra_rules,
    }
    prompt = SYSTEM_PROMPT_TEMPLATE.format(**overrides)
    if drop_empty_sections:
        prompt = _EMPTY_SECTION.sub("", prompt)
    return prompt
