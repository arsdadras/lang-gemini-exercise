"""Pre-built prompt combinations for common use-cases."""

from typing import NamedTuple


class Prompts(NamedTuple):
    """A paired system + human prompt."""

    system: str
    human: str


def make_prompt_pair(system: str, human: str) -> Prompts:
    """Create a validated prompt pair."""
    return Prompts(system=system, human=human)


# ── Fibonacci example ──────────────────────────────────────────────────────

fib_prompts = Prompts(
    system=(
        "You are a coding assistant. When asked to run code, write the "
        "script to a file first, then execute it. Show the output in "
        "your final answer."
    ),
    human=(
        "Write a Python script that prints the first 15 Fibonacci numbers, "
        "save it to fib.py, and run it."
    ),
)
