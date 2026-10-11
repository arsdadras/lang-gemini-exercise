"""System prompt for worker agents: delegated runs whose reply goes to another agent.

The chat template in :mod:`template` addresses a person: a user profile, Finglish replies,
response modes, a conversational style. A worker's reader is a coordinator, so its prompt
keeps the task, the tools, the output contract, and the honesty rules, and nothing else.
"""

from __future__ import annotations

import re
from typing import Final

WORKER_PROMPT_TEMPLATE: Final[str] = """\
<identity>
You are {name} — {role}.
You are a delegated worker: a coordinator agent gave you this task and will read your reply.
Write in English. Be precise and complete; do not address a human user or add pleasantries.
</identity>

<mission>
{mission}
</mission>

<tools_policy>
{tools}
</tools_policy>

<output_contract>
{output_format}
</output_contract>

<constraints>
{constraints}
</constraints>

<uncertainty_policy>
Separate what you verified from what you infer. If you cannot do something, say so in one
short sentence and say what would resolve it. Never invent an API, a flag, a path, a citation,
or a result; report a failure as a failure.
</uncertainty_policy>"""

_EMPTY_SECTION: Final[re.Pattern[str]] = re.compile(r"<(\w+)>\s*</\1>\n*")


def build_worker_prompt(
    *,
    name: str,
    role: str,
    mission: str,
    tools: str = "",
    output_format: str = "",
    constraints: str = "",
) -> str:
    """Render a worker prompt; sections left empty are dropped."""
    prompt = WORKER_PROMPT_TEMPLATE.format(
        name=name,
        role=role,
        mission=mission,
        tools=tools,
        output_format=output_format,
        constraints=constraints,
    )
    return _EMPTY_SECTION.sub("", prompt)
