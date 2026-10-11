"""The eval-lite harness: scripted deciders and a fake clock, so every figure is exact."""

import json
from pathlib import Path

import pytest

from agentlab.configs.paths_config import EVAL_DATASETS_DIR
from agentlab.utils.eval_util import (
    Decision,
    EvalCase,
    EvalDataset,
    format_report,
    load_dataset,
    percentile,
    run_eval,
)


def guard_case(case_id: str, expected: str, *, finglish: bool = False) -> EvalCase:
    unsafe = {"allow": [], "ask": ["allow"], "block": ["allow", "ask"]}[expected]
    return EvalCase(
        id=case_id,
        inputs={"content": case_id},
        expected=expected,
        unsafe_predictions=unsafe,
        finglish=finglish,
    )


DATASET = EvalDataset(
    name="guard",
    question="allow, ask, or block?",
    labels=["allow", "ask", "block"],
    cases=[
        guard_case("a", "allow"),
        guard_case("b", "ask"),
        guard_case("c", "block"),
        guard_case("d", "block", finglish=True),
    ],
)


class FakeClock:
    """Advances by the next scripted latency on every second reading (start, then end)."""

    def __init__(self, *latencies: float) -> None:
        self.latencies = list(latencies)
        self.now = 0.0
        self.reads = 0

    def __call__(self) -> float:
        self.reads += 1
        if self.reads % 2 == 0:
            self.now += self.latencies[self.reads // 2 - 1]
        return self.now


def scripted(answers: dict[str, Decision]):
    return lambda case: answers[case.id]


def test_accuracy_per_class_and_unsafe_errors() -> None:
    decider = scripted(
        {
            "a": Decision(label="allow"),
            "b": Decision(label="allow"),  # ask -> allow: unsafe
            "c": Decision(label="ask"),  # block -> ask: unsafe
            "d": Decision(label="block"),
        }
    )

    report = run_eval(DATASET, decider)

    assert report.accuracy == 0.5
    assert {k: (v.correct, v.support) for k, v in report.per_class.items()} == {
        "allow": (1, 1),
        "ask": (0, 1),
        "block": (1, 2),
    }
    assert report.unsafe_errors == 2
    assert report.unsafe_case_ids == ["b", "c"]
    assert report.finglish_accuracy == 1.0


def test_a_wrong_label_that_is_not_listed_unsafe_is_only_wrong() -> None:
    decider = scripted(
        {
            "a": Decision(label="block"),  # allow -> block: wrong, over-cautious
            "b": Decision(label="ask"),
            "c": Decision(label="block"),
            "d": Decision(label="block"),
        }
    )

    report = run_eval(DATASET, decider)

    assert report.accuracy == 0.75
    assert report.unsafe_errors == 0


def test_a_label_the_dataset_never_declared_counts_as_unsafe() -> None:
    decider = scripted(
        {
            "a": Decision(label="allow"),
            "b": Decision(label="ask"),
            "c": Decision(label="deny"),  # not in the dataset's labels
            "d": Decision(label="Block"),  # case matters: also undeclared
        }
    )

    report = run_eval(DATASET, decider)

    assert report.undeclared_case_ids == ["c", "d"]
    assert report.unsafe_case_ids == ["c", "d"]
    assert report.unsafe_errors == 2
    assert "undeclared labels: 2 (c, d)" in format_report(report)


def test_latency_percentiles_cost_and_paths_come_from_the_run() -> None:
    clock = FakeClock(0.1, 0.2, 0.3, 1.0)
    decider = scripted(
        {
            "a": Decision(label="allow", path="laya", cost=0.0),
            "b": Decision(label="ask", path="laya"),
            "c": Decision(label="block", path="llm:low", cost=0.002),
            "d": Decision(label="block", path="llm:low", cost=0.003),
        }
    )

    report = run_eval(DATASET, decider, clock=clock)

    assert [r.latency_s for r in report.results] == pytest.approx([0.1, 0.2, 0.3, 1.0])
    assert report.p50_latency_s == pytest.approx(0.2)
    assert report.p95_latency_s == pytest.approx(1.0)
    assert report.total_cost == pytest.approx(0.005)
    assert report.paths == {"laya": 2, "llm:low": 2}


def test_coverage_at_a_threshold_counts_confident_answers_and_escalates_the_rest() -> (
    None
):
    decider = scripted(
        {
            "a": Decision(label="allow", probability=0.95),  # covered, right
            "b": Decision(label="allow", probability=0.90),  # covered, wrong
            "c": Decision(label="block", probability=0.40),  # below: escalates
            "d": Decision(label="block"),  # no probability: escalates
        }
    )

    report = run_eval(DATASET, decider, threshold=0.8)

    assert report.coverage is not None
    assert (report.coverage.covered, report.coverage.escalated) == (2, 2)
    assert report.coverage.coverage == 0.5
    assert report.coverage.accuracy == 0.5


def test_coverage_is_absent_without_a_threshold_and_accuracy_none_when_nothing_is_covered() -> (
    None
):
    decider = scripted({c.id: Decision(label=c.expected) for c in DATASET.cases})

    assert run_eval(DATASET, decider).coverage is None
    nothing = run_eval(DATASET, decider, threshold=0.5).coverage
    assert nothing is not None and nothing.covered == 0 and nothing.accuracy is None


def test_an_external_failure_is_recorded_not_propagated() -> None:
    def decider(case: EvalCase) -> Decision:
        if case.id == "b":
            raise TimeoutError("backend timed out")
        return Decision(label=case.expected)

    report = run_eval(DATASET, decider)

    assert report.failures == 1
    assert report.accuracy == 0.75
    failed = report.results[1]
    assert failed.predicted is None
    assert (
        failed.error
        == "An external service was unavailable, even after retries: backend timed out"
    )
    assert report.unsafe_errors == 0


def test_a_bug_in_the_decider_raises() -> None:
    def decider(case: EvalCase) -> Decision:
        raise KeyError("missing input")

    with pytest.raises(KeyError):
        run_eval(DATASET, decider)


def test_percentile_is_nearest_rank() -> None:
    assert percentile([], 0.5) == 0.0
    assert percentile([5.0], 0.95) == 5.0
    assert percentile([4.0, 1.0, 3.0, 2.0], 0.5) == 2.0
    assert percentile([4.0, 1.0, 3.0, 2.0], 0.95) == 4.0


def test_the_report_formats_as_ascii() -> None:
    decider = scripted(
        {c.id: Decision(label=c.expected, probability=0.9) for c in DATASET.cases}
    )

    text = format_report(run_eval(DATASET, decider, threshold=0.8))

    assert text.isascii()
    assert "accuracy 100.0% on 4 cases" in text
    assert "unsafe errors: 0" in text
    assert "coverage 100.0%" in text


def test_load_dataset_rejects_an_undeclared_label(tmp_path: Path) -> None:
    bad = DATASET.model_copy(deep=True)
    bad.cases[0].expected = "maybe"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad.model_dump()), encoding="utf-8")

    with pytest.raises(ValueError, match="labels not declared"):
        load_dataset(path)


@pytest.mark.parametrize(
    "path", sorted(EVAL_DATASETS_DIR.glob("*.json")), ids=lambda p: p.stem
)
def test_every_seed_dataset_loads_with_unique_ids(path: Path) -> None:
    dataset = load_dataset(path)

    assert dataset.cases
    assert len({case.id for case in dataset.cases}) == len(dataset.cases)
    assert dataset.name == path.stem


def test_the_seed_datasets_exist_and_carry_the_guard_and_finglish_flags() -> None:
    names = {p.stem for p in EVAL_DATASETS_DIR.glob("*.json")}
    guard = load_dataset(EVAL_DATASETS_DIR / "guard.json")
    intent = load_dataset(EVAL_DATASETS_DIR / "intent.json")

    assert {"relevance", "grounded", "guard", "intent"} <= names
    block = next(c for c in guard.cases if c.expected == "block")
    assert block.unsafe_predictions == ["allow", "ask"]
    assert [c.finglish for c in intent.cases] == [True, True, False]
