"""The decision-model seam: records, failures, the wire request, and the key by name."""

import json
from typing import Any

import httpx2
import pytest
from langchain_core.messages import HumanMessage
from langchain_typesafe import (
    Choice,
    ClassifierResponse,
    Noul,
    Score,
    TypeSafeClassifier,
)

from agentlab.models.decision_model import (
    DecisionRecord,
    DecisionRegistry,
    build_backend,
    state_hash,
)
from agentlab.utils.failure_util import failure_kind
from tests.fakes import scripted_decider

WIRE_ANSWERS = {
    "relevant": {"type": "noul", "noul": 0.97},
    "kind": {
        "type": "choice",
        "choice": "geo",
        "probabilities": {"geo": 0.9, "other": 0.1},
        "confidence": 0.8,
    },
    "tone": {
        "type": "score",
        "score": 1.25,
        "legend": {"0": "calm", "1": "civil", "2": "angry"},
        "probabilities": {"0": 0.2, "1": 0.55, "2": 0.25},
        "confidence": 0.5,
    },
}
QUESTIONS: dict[str, Any] = {
    "relevant": Noul(instructions="Does it answer a question?"),
    "kind": Choice(
        instructions="What kind?", criteria={"geo": "Places", "other": "Else"}
    ),
    "tone": Score(instructions="How angry?", criteria=["calm", "civil", "angry"]),
}


def wire_response(**overrides: Any) -> ClassifierResponse:
    body = {
        "model": "jev-1.13.0",
        "answers": WIRE_ANSWERS,
        "usage": {"input_tokens": 1000, "output_tokens": 49},
    } | overrides
    return ClassifierResponse.model_validate(body)


def registry(*responses: Any) -> tuple[DecisionRegistry, list[DecisionRecord]]:
    records: list[DecisionRecord] = []
    ticks = iter([10.0, 10.25])
    return (
        DecisionRegistry(
            backend_builder=lambda: scripted_decider(*responses),
            sink=records.append,
            clock=lambda: next(ticks),
        ),
        records,
    )


def test_a_decision_is_recorded_with_its_version_hash_probabilities_latency_and_cost() -> (
    None
):
    decisions, records = registry(wire_response())

    response = decisions.decide(
        "Paris is the capital.", QUESTIONS, question_set="demo@1"
    )

    assert response.nouls["relevant"].noul == 0.97
    [record] = records
    assert record.question_set == "demo@1"
    assert record.state_sha256 == state_hash("Paris is the capital.")
    assert record.served_model == "jev-1.13.0"
    assert record.latency_ms == 250
    assert record.input_tokens == 1000
    assert record.cost_usd == pytest.approx(1000 * 0.042 / 1_000_000)
    assert record.path == "decider"
    assert record.error is None
    assert record.answers["relevant"] == {"type": "noul", "noul": 0.97}
    assert record.answers["kind"]["choice"] == "geo"
    assert record.answers["tone"]["probabilities"] == {"0": 0.2, "1": 0.55, "2": 0.25}


def test_the_state_itself_never_reaches_the_record() -> None:
    decisions, records = registry(wire_response())

    decisions.decide("secret passport 1234", QUESTIONS, question_set="demo@1")

    assert "1234" not in records[0].model_dump_json()


def test_a_failed_decision_is_recorded_and_reraised() -> None:
    boom = TimeoutError("slow")
    decisions, records = registry(boom)

    with pytest.raises(TimeoutError):
        decisions.decide("x", QUESTIONS, question_set="demo@1")

    [record] = records
    assert record.error == "TimeoutError"
    assert record.answers == {}
    assert record.served_model is None


def test_the_state_hash_ignores_dict_order_and_reads_messages_as_role_and_content() -> (
    None
):
    assert state_hash({"a": 1, "b": 2}) == state_hash({"b": 2, "a": 1})
    assert state_hash([HumanMessage("hi")]) == state_hash(
        [{"role": "human", "content": "hi"}]
    )
    assert state_hash("one") != state_hash("two")


def test_the_backend_is_built_once_and_reused() -> None:
    built: list[int] = []

    def builder() -> Any:
        built.append(1)
        return scripted_decider()

    decisions = DecisionRegistry(backend_builder=builder)
    assert decisions.get() is decisions.get()
    assert built == [1]


def mock_classifier(handler: Any) -> TypeSafeClassifier:
    return TypeSafeClassifier(
        model="jev-1.13.0",
        api_key="test-key",
        base_url="https://decider.test",
        timeout=3,
        client=httpx2.Client(transport=httpx2.MockTransport(handler)),
    )


def test_the_wire_request_carries_the_pinned_model_the_key_and_every_question() -> None:
    seen: dict[str, Any] = {}

    def handler(request: httpx2.Request) -> httpx2.Response:
        seen["url"] = str(request.url)
        seen["auth"] = request.headers["authorization"]
        seen["body"] = json.loads(request.content)
        return httpx2.Response(
            200,
            json={
                "model": "jev-1.13.0",
                "answers": WIRE_ANSWERS,
                "usage": {"input_tokens": 7},
            },
            headers={"x-request-id": "req_1"},
        )

    decisions, records = registry()
    decisions = DecisionRegistry(
        backend_builder=lambda: mock_classifier(handler), sink=records.append
    )

    decisions.decide("Paris is the capital.", QUESTIONS, question_set="demo@1")

    assert seen["url"] == "https://decider.test/v1/systemone"
    assert seen["auth"] == "Bearer test-key"
    assert seen["body"]["model"] == "jev-1.13.0"
    assert seen["body"]["state"] == "Paris is the capital."
    assert set(seen["body"]["questions"]) == {"relevant", "kind", "tone"}
    assert records[0].input_tokens == 7


@pytest.mark.parametrize(
    ("status", "kind"),
    [
        (429, "transient"),
        (500, "transient"),
        (503, "transient"),
        (401, "permanent"),
        (400, "permanent"),
    ],
)
def test_decider_http_errors_classify_like_every_other_external_failure(
    status: int, kind: str
) -> None:
    decisions = DecisionRegistry(
        backend_builder=lambda: mock_classifier(
            lambda _r: httpx2.Response(status, json={})
        ),
        sink=lambda _record: None,
    )

    with pytest.raises(Exception) as caught:
        decisions.decide("x", QUESTIONS, question_set="demo@1")

    assert failure_kind(caught.value) == kind


def test_a_decider_that_never_answers_is_a_transient_failure() -> None:
    def handler(request: httpx2.Request) -> httpx2.Response:
        raise httpx2.ReadTimeout("silent", request=request)

    decisions = DecisionRegistry(
        backend_builder=lambda: mock_classifier(handler), sink=lambda _record: None
    )

    with pytest.raises(Exception) as caught:
        decisions.decide("x", QUESTIONS, question_set="demo@1")

    assert failure_kind(caught.value) == "transient"


def test_the_production_backend_reads_its_key_by_name_when_built(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="TYPESAFE_API_KEY"):
        build_backend()

    monkeypatch.setenv("TYPESAFE_API_KEY", "k")
    assert isinstance(build_backend(), TypeSafeClassifier)
