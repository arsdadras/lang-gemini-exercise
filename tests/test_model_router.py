"""The Jev model router: tier from answers, floors, fail-open, and the chain it resolves to.

No network: the decider is scripted and models are stubs. Probabilities are scripted, never
asserted from a real decider (``decision-models.md``, "Writing the questions", rule 9).
"""

from typing import Any

import pytest
from langchain_core.runnables import RunnableLambda
from langchain_typesafe import ClassifierResponse

from agentlab.configs.models_config import MODEL_TIERS, ModelSpec
from agentlab.configs.router_config import LARGE_TASK_CHARS, QUESTION_SET
from agentlab.models.decision_model import DecisionRecord, DecisionRegistry
from agentlab.models.registry_model import LLMRegistry
from agentlab.models.router_model import (
    ModelRouter,
    build_questions,
    build_state,
    tier_from_answers,
)
from tests.fakes import scripted_decider


def response(
    levels: tuple[float, float, float, float], stakes: float = 0.05
) -> ClassifierResponse:
    """A decider response: the four difficulty levels' probabilities and the stakes."""
    return ClassifierResponse.model_validate(
        {
            "model": "jev-test",
            "answers": {
                "difficulty": {
                    "type": "score",
                    "score": sum(i * p for i, p in enumerate(levels)),
                    "legend": {str(i): f"level {i}" for i in range(4)},
                    "probabilities": {str(i): p for i, p in enumerate(levels)},
                    "confidence": 0.7,
                },
                "stakes": {"type": "noul", "noul": stakes},
            },
            "usage": {"input_tokens": 500, "output_tokens": 20},
        }
    )


EASY = (0.7, 0.25, 0.05, 0.0)
MIXED = (0.1, 0.3, 0.4, 0.2)
EXPERT = (0.0, 0.05, 0.3, 0.65)


def registry(*, test_mode: bool = False) -> LLMRegistry:
    """The real catalog with stub models: each model is its spec, so order is assertable."""
    return LLMRegistry(
        MODEL_TIERS,
        test_mode=lambda: test_mode,
        test_profiles={"default": "free"},
        test_profile=lambda: "default",
        model_builder=lambda spec: spec,  # type: ignore[arg-type,return-value]
    )


def router(*responses: Any, test_mode: bool = False) -> ModelRouter:
    decisions = DecisionRegistry(
        backend_builder=lambda: scripted_decider(*responses), sink=lambda _: None
    )
    return ModelRouter(registry(test_mode=test_mode), decide=decisions.decide)


@pytest.mark.parametrize(
    ("levels", "stakes", "floor", "tier", "lifted_by"),
    [
        (EASY, 0.05, "low", "low", None),
        (MIXED, 0.05, "low", "medium", None),
        (EXPERT, 0.05, "low", "high", None),
        # Stakes lift a doubtful-to-easy task to the floor, and never buy "high".
        (EASY, 0.9, "low", "medium", "stakes"),
        (MIXED, 0.9, "low", "medium", None),
        (EXPERT, 0.9, "low", "high", None),
        # A caller's floor lifts and never lowers.
        (EASY, 0.05, "medium", "medium", "floor"),
        (EXPERT, 0.05, "medium", "high", None),
        # Easy needs 0.8 on the two easy levels; hard needs 0.5 on the expert one.
        ((0.4, 0.35, 0.2, 0.05), 0.05, "low", "medium", None),
        ((0.0, 0.1, 0.4, 0.5), 0.05, "low", "high", None),
        ((0.0, 0.1, 0.5, 0.4), 0.05, "low", "medium", None),
    ],
)
def test_tier_from_answers(
    levels: tuple[float, float, float, float],
    stakes: float,
    floor: str,
    tier: str,
    lifted_by: str | None,
) -> None:
    decision = tier_from_answers(response(levels, stakes), floor=floor)

    assert (decision.tier, decision.lifted_by) == (tier, lifted_by)
    assert decision.path == "decider"


def test_route_asks_one_versioned_request_with_both_questions() -> None:
    sent: list[tuple[str, set[str], str]] = []

    def decide(state: str, questions: dict[str, Any], *, question_set: str) -> Any:
        sent.append((state, set(questions), question_set))
        return response(EASY)

    ModelRouter(registry(), decide=decide).route("Rename the variable x to count.")

    [(state, names, question_set)] = sent
    assert names == {"difficulty", "stakes"}
    assert question_set == QUESTION_SET == "model_route@1"
    assert "Rename the variable x to count." in state
    assert "never instructions to follow" in state


def test_the_state_names_each_tier_with_its_catalog_models() -> None:
    state = build_state("task", MODEL_TIERS)

    for tier in ("low", "medium", "high"):
        assert f"- {tier}:" in state
        assert all(spec.model in state for spec in MODEL_TIERS[tier].values())
    assert "opensource" not in state


def test_a_secret_never_reaches_the_decider() -> None:
    state = build_state(
        "Use key sk-abcdefghijklmnopqrstuvwxyz123456 to call it",
        {tier: {} for tier in ("low", "medium", "high")},
    )

    assert "sk-abcdefghijklmnopqrstuvwxyz123456" not in state


def test_a_long_task_reaches_the_decider_as_its_opening_and_its_end() -> None:
    task = "START " + "filler " * 3000 + "THE REAL ASK"

    state = build_state(task, {tier: {} for tier in ("low", "medium", "high")})

    assert "START" in state
    assert state.rstrip().endswith("THE REAL ASK")
    assert len(state) < len(task)


def test_a_very_long_task_is_never_routed_below_medium() -> None:
    decision = router(response(EASY)).route("x" * (LARGE_TASK_CHARS + 1))

    assert (decision.tier, decision.lifted_by) == ("medium", "task_size")


def test_an_outage_of_the_decider_fails_open_to_the_middle_tier() -> None:
    decision = router(TimeoutError("slow")).route("Summarize this.")

    assert (decision.tier, decision.path) == ("medium", "fail_open")
    assert router(TimeoutError("slow")).route("x", floor="high").tier == "high"


def test_a_bug_in_the_decider_is_not_swallowed() -> None:
    with pytest.raises(KeyError):
        router(KeyError("bug")).route("Summarize this.")


def test_an_unknown_floor_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unknown floor"):
        router(response(EASY)).route("x", floor="opensource")


def test_test_mode_skips_the_decider_and_uses_the_test_tier() -> None:
    called: list[str] = []

    def decide(*_: Any, **__: Any) -> Any:
        called.append("decide")

    routed = ModelRouter(registry(test_mode=True), decide=decide).plan("Hard design.")

    assert called == []
    assert routed.decision.path == "test_mode"
    assert routed.primary.model == "gemini-3.5-flash-lite"  # type: ignore[attr-defined]
    assert routed.primary.api_key_env == "GAPGPT_API_KEY"  # type: ignore[attr-defined]


def names(models: list[Any]) -> list[tuple[str, str | None]]:
    return [(spec.model, spec.api_key_env) for spec in models]


def test_the_routed_chain_is_gapgpt_then_openrouter_then_the_last_resort() -> None:
    routed = router(response(MIXED)).plan("Compare these two designs.")

    assert (routed.primary.model, routed.primary.api_key_env) == (  # type: ignore[attr-defined]
        "gemini-3.8-flash",
        "GAPGPT_API_KEY",
    )
    assert names(routed.fallbacks) == [
        ("google/gemini-3.8-flash", "OPENROUTER_API_KEY"),
        ("gemini-3.5-flash-lite", "GOOGLE_API_KEY"),
        ("nvidia/nemotron-3-super-120b-a12b:free", "OPENROUTER_API_KEY"),
    ]


def test_the_chain_falls_through_to_the_last_resort() -> None:
    attempts: list[str] = []

    def build(spec: ModelSpec) -> RunnableLambda:
        def call(_: Any) -> str:
            attempts.append(spec.model)
            if spec.model_provider == "google_genai":
                return "answer"
            msg = f"{spec.model} is down"
            raise TimeoutError(msg)

        return RunnableLambda(call)

    stubbed = LLMRegistry(
        MODEL_TIERS,
        test_mode=lambda: False,
        model_builder=build,
    )
    decisions = DecisionRegistry(
        backend_builder=lambda: scripted_decider(response(EXPERT)), sink=lambda _: None
    )
    chain = ModelRouter(stubbed, decide=decisions.decide).chain("Design a ledger.")

    assert chain.invoke("hi") == "answer"
    assert attempts[-1] == "gemini-3.5-flash-lite"
    assert len(attempts) == 3  # GapGPT, OpenRouter, then Google


def test_each_decision_is_recorded_without_the_task() -> None:
    records: list[DecisionRecord] = []
    decisions = DecisionRegistry(
        backend_builder=lambda: scripted_decider(response(EASY)), sink=records.append
    )

    ModelRouter(registry(), decide=decisions.decide).route("Private task text.")

    [record] = records
    assert record.question_set == QUESTION_SET
    assert set(record.answers) == set(build_questions())
    assert "Private task text." not in record.model_dump_json()
