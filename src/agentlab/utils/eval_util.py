"""Eval-lite harness for decision points: labeled cases in, a measured report out.

A decision point (route, gate, grade, verify, recall, stop) answers a typed question with one
label. The harness holds it to the standard in ``library/architecture/decision-models.md``,
whatever the backend: a dataset of labeled cases, a decider injected per scenario, and a report
of accuracy per class, unsafe errors, p50 and p95 latency, cost, and coverage at a threshold.

Nothing here calls a model. A scenario passes its own decider (an LLM chain, a decision model,
or plain code), so the same dataset measures every backend and a shadow run is two calls.
"""

import json
import math
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, Field

from agentlab.utils.failure_util import failure_kind, failure_reason


class EvalCase(BaseModel):
    """One labeled decision. ``inputs`` is whatever the decider needs, by name."""

    id: str
    inputs: dict[str, str]
    expected: str
    unsafe_predictions: list[str] = Field(default_factory=list)
    """Wrong labels that are unsafe errors (a guard that allows what it should block, a
    grounding check that passes a fabricated claim), as opposed to merely wrong."""
    finglish: bool = False


class EvalDataset(BaseModel):
    """A named set of cases for one decision point."""

    name: str
    question: str
    labels: list[str]
    source: str = ""
    cases: list[EvalCase]


class Decision(BaseModel):
    """What a decider returns for one case."""

    label: str
    probability: float | None = None
    """The backend's probability or margin for ``label``, when it gives one. A ranking signal,
    not a calibrated number."""
    path: str = ""
    """Which backend or branch answered (``laya``, ``llm:low``, ``rule``, an escalation)."""
    cost: float = 0.0
    """Cost of this call in USD; 0 for code and local models."""


Decider = Callable[[EvalCase], Decision]


class CaseResult(BaseModel):
    """One case's outcome: the decision plus what the harness measured around it."""

    case_id: str
    expected: str
    predicted: str | None
    """``None`` when the decider hit an external failure; ``error`` then says why."""
    probability: float | None = None
    path: str = ""
    latency_s: float
    cost: float = 0.0
    correct: bool
    unsafe: bool
    finglish: bool = False
    error: str | None = None


class ClassStats(BaseModel):
    """Recall for one expected class."""

    support: int
    correct: int
    accuracy: float


class CoverageStats(BaseModel):
    """How much the backend can answer on its own at one threshold."""

    threshold: float
    covered: int
    coverage: float
    accuracy: float | None
    """Accuracy over the covered cases; ``None`` when none are covered."""
    escalated: int
    """Cases below the threshold, or without a probability, that escalate to the next backend."""


class EvalReport(BaseModel):
    """The measured result of one scenario run."""

    dataset: str
    total: int
    accuracy: float
    per_class: dict[str, ClassStats]
    unsafe_errors: int
    unsafe_case_ids: list[str]
    failures: int
    """Cases where the decider hit an external failure; each counts as wrong."""
    finglish_accuracy: float | None
    p50_latency_s: float
    p95_latency_s: float
    total_cost: float
    paths: dict[str, int]
    coverage: CoverageStats | None = None
    results: list[CaseResult]


def load_dataset(path: Path) -> EvalDataset:
    """Load and validate a dataset file; a case whose label isn't declared is an error."""
    dataset = EvalDataset.model_validate(json.loads(path.read_text(encoding="utf-8")))
    declared = set(dataset.labels)
    for case in dataset.cases:
        stray = ({case.expected} | set(case.unsafe_predictions)) - declared
        if stray:
            raise ValueError(
                f"{dataset.name}/{case.id}: labels not declared: {sorted(stray)}"
            )
    return dataset


def percentile(values: list[float], fraction: float) -> float:
    """Nearest-rank percentile (``fraction`` in 0..1); 0.0 for no values."""
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(math.ceil(fraction * len(ordered)), 1) - 1]


def _ratio(part: int, whole: int) -> float:
    return part / whole if whole else 0.0


def evaluate_case(
    case: EvalCase,
    decider: Decider,
    clock: Callable[[], float] = time.perf_counter,
) -> CaseResult:
    """Run the decider on one case.

    An external failure (a timeout, a 5xx) is recorded and counts as wrong; anything else is a
    bug in the decider and raises (see ``utils/failure_util.py``).
    """
    start = clock()
    try:
        decision = decider(case)
    except Exception as error:
        if failure_kind(error) is None:
            raise
        return CaseResult(
            case_id=case.id,
            expected=case.expected,
            predicted=None,
            latency_s=clock() - start,
            correct=False,
            unsafe=False,
            finglish=case.finglish,
            error=failure_reason(error),
        )
    latency = clock() - start
    correct = decision.label == case.expected
    return CaseResult(
        case_id=case.id,
        expected=case.expected,
        predicted=decision.label,
        probability=decision.probability,
        path=decision.path,
        latency_s=latency,
        cost=decision.cost,
        correct=correct,
        unsafe=not correct and decision.label in case.unsafe_predictions,
        finglish=case.finglish,
    )


def run_eval(
    dataset: EvalDataset,
    decider: Decider,
    *,
    threshold: float | None = None,
    clock: Callable[[], float] = time.perf_counter,
) -> EvalReport:
    """Run ``decider`` over every case and measure it.

    ``threshold`` turns on the coverage figures: a case is covered when the decider gave a
    probability at or above it; the rest escalate.
    """
    results = [evaluate_case(case, decider, clock) for case in dataset.cases]
    return build_report(dataset, results, threshold=threshold)


def build_report(
    dataset: EvalDataset,
    results: list[CaseResult],
    *,
    threshold: float | None = None,
) -> EvalReport:
    """Aggregate case results into a report (separate from ``run_eval`` for tests and shadow runs)."""
    per_class = {}
    for label in dataset.labels:
        of_class = [r for r in results if r.expected == label]
        right = sum(r.correct for r in of_class)
        per_class[label] = ClassStats(
            support=len(of_class),
            correct=right,
            accuracy=_ratio(right, len(of_class)),
        )
    finglish = [r for r in results if r.finglish]
    latencies = [r.latency_s for r in results]
    coverage = None
    if threshold is not None:
        covered = [
            r
            for r in results
            if r.probability is not None and r.probability >= threshold
        ]
        coverage = CoverageStats(
            threshold=threshold,
            covered=len(covered),
            coverage=_ratio(len(covered), len(results)),
            accuracy=(sum(r.correct for r in covered) / len(covered))
            if covered
            else None,
            escalated=len(results) - len(covered),
        )
    return EvalReport(
        dataset=dataset.name,
        total=len(results),
        accuracy=_ratio(sum(r.correct for r in results), len(results)),
        per_class=per_class,
        unsafe_errors=sum(r.unsafe for r in results),
        unsafe_case_ids=[r.case_id for r in results if r.unsafe],
        failures=sum(r.error is not None for r in results),
        finglish_accuracy=(
            sum(r.correct for r in finglish) / len(finglish) if finglish else None
        ),
        p50_latency_s=percentile(latencies, 0.50),
        p95_latency_s=percentile(latencies, 0.95),
        total_cost=sum(r.cost for r in results),
        paths=dict(Counter(r.path for r in results if r.path)),
        coverage=coverage,
        results=results,
    )


def format_report(report: EvalReport) -> str:
    """The report as ASCII lines for a console or an evidence record."""
    lines = [
        (
            f"{report.dataset}: accuracy {report.accuracy:.1%} on {report.total} cases"
            f" ({report.failures} decider failures)"
        ),
        "  per class: "
        + ", ".join(
            f"{label} {stats.correct}/{stats.support}"
            for label, stats in report.per_class.items()
        ),
        f"  unsafe errors: {report.unsafe_errors}"
        + (f" ({', '.join(report.unsafe_case_ids)})" if report.unsafe_case_ids else ""),
        f"  latency: p50 {report.p50_latency_s * 1000:.0f} ms, p95 {report.p95_latency_s * 1000:.0f} ms",
        f"  cost: ${report.total_cost:.4f}",
    ]
    if report.finglish_accuracy is not None:
        lines.append(f"  finglish accuracy: {report.finglish_accuracy:.1%}")
    if report.paths:
        lines.append(
            "  paths: " + ", ".join(f"{p} x{n}" for p, n in report.paths.items())
        )
    if report.coverage is not None:
        c = report.coverage
        accuracy = "n/a" if c.accuracy is None else f"{c.accuracy:.1%}"
        lines.append(
            f"  at threshold {c.threshold}: coverage {c.coverage:.1%} ({c.covered} covered,"
            f" {c.escalated} escalate), accuracy on covered {accuracy}"
        )
    return "\n".join(lines)
