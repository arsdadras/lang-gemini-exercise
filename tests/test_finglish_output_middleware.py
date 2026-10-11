"""The Finglish output guardrail on a real agent graph; the model and the rewriter are scripted."""

from typing import Any

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables import RunnableLambda

from agentlab.middlewares.finglish_output_middleware import (
    has_perso_arabic,
    make_finglish_output_guard,
)
from agentlab.schemas.output.middlewares_output_schema import FinglishLines
from tests.fakes import ScriptedToolModel

STRENGTH = "تمرین قدرتی"
SLOWLY = "آهسته"
LEAKED_LINE = f"  - 15 daghighe {STRENGTH}  "
REPAIRED_LINE = "- 15 daghighe tamrin-e ghodrati"


def scripted_rewriter(*passes: list[str], calls: list[list[str]]) -> RunnableLambda:
    """Returns the given lines for each pass in turn, recording the lines it was sent."""
    replies = iter(passes)

    def rewrite(inputs: dict[str, Any]) -> FinglishLines:
        calls.append(inputs["lines"].split("\n"))
        return FinglishLines(lines=next(replies))

    return RunnableLambda(rewrite)


def final_text(answer: str, rewriter: RunnableLambda) -> str:
    agent = create_agent(
        model=ScriptedToolModel(messages=iter([AIMessage(content=answer)])),
        tools=[],
        middleware=[make_finglish_output_guard(rewriter)],
    )
    messages = agent.invoke({"messages": [HumanMessage(content="barname bede")]})[
        "messages"
    ]
    assert len(messages) == 2  # the repair replaced the answer instead of appending one
    return str(messages[-1].content)


def test_detector_flags_perso_arabic_but_not_finglish_or_english():
    assert has_perso_arabic(LEAKED_LINE)
    assert not has_perso_arabic(REPAIRED_LINE)
    assert not has_perso_arabic("Use `uv run pytest` before committing.")


def test_only_leaked_lines_are_sent_and_their_indentation_is_kept():
    calls: list[list[str]] = []
    answer = f"### Hafte 1\n{LEAKED_LINE}\n- 20 daghighe piyade-ravi"

    text = final_text(answer, scripted_rewriter([REPAIRED_LINE], calls=calls))

    assert calls == [[LEAKED_LINE]]
    assert (
        text
        == "### Hafte 1\n  - 15 daghighe tamrin-e ghodrati  \n- 20 daghighe piyade-ravi"
    )


def test_a_second_pass_repairs_lines_the_first_pass_missed():
    calls: list[list[str]] = []
    answer = f"{LEAKED_LINE}\n- bedav {SLOWLY}"

    text = final_text(
        answer,
        scripted_rewriter(
            [REPAIRED_LINE, f"- bedav {SLOWLY}"],
            ["- bedav ahesteh"],
            calls=calls,
        ),
    )

    assert calls == [[LEAKED_LINE, f"- bedav {SLOWLY}"], [f"- bedav {SLOWLY}"]]
    assert text == "  - 15 daghighe tamrin-e ghodrati  \n- bedav ahesteh"


def test_lines_still_leaking_after_every_pass_stay_as_they_were():
    answer = f"{LEAKED_LINE}\n- bedav {SLOWLY}"

    text = final_text(
        answer,
        scripted_rewriter([REPAIRED_LINE, SLOWLY], [SLOWLY], calls=[]),
    )

    assert text == f"  - 15 daghighe tamrin-e ghodrati  \n- bedav {SLOWLY}"


def test_clean_answer_never_calls_the_rewriter():
    calls: list[list[str]] = []

    assert final_text(REPAIRED_LINE, scripted_rewriter(calls=calls)) == REPAIRED_LINE
    assert calls == []


def test_a_reply_with_the_wrong_number_of_lines_is_ignored():
    text = final_text(
        LEAKED_LINE,
        scripted_rewriter([REPAIRED_LINE, "extra"], [], calls=[]),
    )

    assert text == LEAKED_LINE


def test_a_malformed_chunk_only_costs_its_own_lines():
    """25 leaked lines go out as chunks of 20 and 5; the 5-line chunk always comes back malformed."""
    sizes: list[int] = []

    def rewrite(inputs: dict[str, Any]) -> FinglishLines:
        lines = inputs["lines"].split("\n")
        sizes.append(len(lines))
        if len(lines) != 20:
            return FinglishLines(lines=[])
        return FinglishLines(
            lines=[line.replace(STRENGTH, "tamrin-e ghodrati") for line in lines],
        )

    answer = "\n".join(f"- rooz {day}: {STRENGTH}" for day in range(1, 26))

    lines = final_text(answer, RunnableLambda(rewrite)).split("\n")

    assert sorted(sizes) == [
        5,
        5,
        20,
    ]  # both chunks in pass one, the 5 leftovers in pass two
    assert not any(has_perso_arabic(line) for line in lines[:20])
    assert all(has_perso_arabic(line) for line in lines[20:])


def test_failing_repair_keeps_the_original():
    def broken(_inputs: dict[str, Any]) -> FinglishLines:
        raise TimeoutError("provider timed out")

    assert final_text(LEAKED_LINE, RunnableLambda(broken)) == LEAKED_LINE
