"""Live smoke check of every external integration, run by hand after a dependency upgrade.

Always runs in LLM test mode: each profile routes every tier to one cheap tier, so the check
exercises each provider SDK path (plain chat, structured output, tool binding) without
production-tier spend. Embeddings, web search, and the decision model are called once each.

Usage:
    uv run python scripts/smoke_live.py [--profiles default,strong,strongest] [--env-file PATH]

Exits non-zero when any check fails. Not collected by pytest (ADR-0004: live checks run by hand).
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field

from agentlab.configs.paths_config import PROJECT_ROOT
from agentlab.utils.get_text_util import get_text


class SmokeVerdict(BaseModel):
    """A tiny structured-output schema."""

    word: str = Field(description="The single word you were asked to return.")


@tool
def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b


def _run(label: str, check: Callable[[], str]) -> bool:
    started = time.perf_counter()
    try:
        detail = check()
    except Exception as exc:  # noqa: BLE001 - a smoke check reports every failure
        elapsed = time.perf_counter() - started
        print(f"FAIL {label} ({elapsed:.1f}s): {type(exc).__name__}: {exc}"[:300])
        return False
    elapsed = time.perf_counter() - started
    print(f"ok   {label} ({elapsed:.1f}s): {detail}"[:300])
    return True


def _model_checks(profile: str) -> list[bool]:
    from agentlab.models import llm_model

    os.environ["LLM_TEST_PROFILE"] = profile
    tier = llm_model.resolve_tier("low")
    model = llm_model.get("low")

    def plain() -> str:
        return get_text(model.invoke("Reply with the single word OK."))[:40]

    def structured() -> str:
        chain = llm_model.chain("low", structured=SmokeVerdict)
        return chain.invoke("Return the word OK in the `word` field.").word

    def tools() -> str:
        reply = model.bind_tools([add]).invoke("Use the add tool to add 2 and 3.")
        return str([call["name"] for call in reply.tool_calls])

    prefix = f"[{profile} -> {tier}]"
    return [
        _run(f"{prefix} plain chat", plain),
        _run(f"{prefix} structured output", structured),
        _run(f"{prefix} tool binding", tools),
    ]


def _embeddings() -> str:
    from agentlab.retrieval.index_retrieval import make_embeddings

    vector = make_embeddings().embed_query("smoke")
    return f"{len(vector)} dimensions"


def _search() -> str:
    from langchain_tavily import TavilySearch

    result = TavilySearch(max_results=1).invoke({"query": "LangChain"})
    return f"{len(result.get('results', []))} result(s)"


def _decision() -> str:
    from langchain_typesafe import Noul

    from agentlab.models import decision_model

    response = decision_model.decide(
        "Paris is the capital of France.",
        {"geo": Noul(instructions="Does the text state a fact about a capital city?")},
        question_set="smoke@1",
    )
    return f"{response.model}, p(yes)={response.nouls['geo'].noul:.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--profiles", default="default,strong,strongest")
    parser.add_argument("--env-file", type=Path, default=PROJECT_ROOT / ".env")
    args = parser.parse_args()

    load_dotenv(args.env_file)
    os.environ["LLM_TEST_MODE"] = "true"

    results: list[bool] = []
    for profile in args.profiles.split(","):
        results.extend(_model_checks(profile.strip()))
    results.append(_run("embeddings", _embeddings))
    results.append(_run("web search", _search))
    results.append(_run("decision model", _decision))

    failed = results.count(False)
    print(f"{len(results) - failed}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
