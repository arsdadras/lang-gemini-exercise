"""The decision-model seam: typed questions about a state, answered with probabilities.

A decision model decides, an LLM writes (ADR-0021). This module is the one place that knows
which decider backs a decision point, the way ``registry_model`` is for chat models: call sites
import ``decision_model`` and never the client library behind it.

- ``get()`` returns the cached backend, a ``Runnable`` from a request (``state`` plus named
  ``questions``) to a ``ClassifierResponse``. Tests inject a scripted backend instead.
- ``decide()`` calls it and writes one ``DecisionRecord`` per decision, a success or a failure:
  the state's hash (never the state), the question set's version, the served snapshot, the
  probabilities, latency, and cost from input tokens.

There is no retry here and no fallback. A decider's failure is an external failure like any
other: the calling node retries it once (``failure_util.TRANSIENT_RETRY``), and a cascade sends
a decider error down the LLM path (``decision-models.md``, "In this repo").
"""

import hashlib
import json
import logging
import os
import time
from collections.abc import Callable
from typing import Any

from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langchain_typesafe import (
    Answer,
    ClassifierRequest,
    ClassifierResponse,
    Question,
    State,
    TypeSafeClassifier,
)
from pydantic import BaseModel

from agentlab.configs.decision_config import (
    DECISION_API_KEY_ENV,
    DECISION_BASE_URL,
    DECISION_MODEL_ID,
    DECISION_USD_PER_MILLION_INPUT_TOKENS,
)
from agentlab.configs.timeouts_config import DECISION_MODEL_TIMEOUT_SECONDS

logger = logging.getLogger("agentlab.decisions")

DecisionBackend = Runnable[ClassifierRequest, ClassifierResponse]


class DecisionRecord(BaseModel):
    """One decision, as the log keeps it. The state itself is never stored, only its hash."""

    question_set: str
    state_sha256: str
    served_model: str | None = None
    request_id: str | None = None
    # Per question: the type and its probabilities (`noul`: p(yes); `choice` and `score`: the
    # distribution plus the selected label or expected score and the confidence).
    answers: dict[str, dict[str, Any]] = {}
    path: str = "decider"
    latency_ms: int
    input_tokens: int | None = None
    cost_usd: float | None = None
    error: str | None = None


def _plain(value: Any) -> Any:
    """A JSON-safe copy of a state, with LangChain messages as role and content."""
    if isinstance(value, BaseMessage):
        return {"role": value.type, "content": _plain(value.content)}
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, list | tuple):
        return [_plain(item) for item in value]
    return value


def state_hash(state: State) -> str:
    """A stable hash of the state: the same state hashes the same, whatever its dict order."""
    text = json.dumps(_plain(state), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _answer_summary(answer: Answer) -> dict[str, Any]:
    if answer.type == "noul":
        return {"type": "noul", "noul": answer.noul}
    if answer.type == "choice":
        return {
            "type": "choice",
            "choice": answer.choice,
            "probabilities": answer.probabilities,
            "confidence": answer.confidence,
        }
    return {
        "type": "score",
        "score": answer.score,
        "probabilities": {str(level): p for level, p in answer.probabilities.items()},
        "confidence": answer.confidence,
    }


def log_record(record: DecisionRecord) -> None:
    """The default sink: one JSON line on the ``agentlab.decisions`` logger."""
    logger.info(record.model_dump_json())


def build_backend() -> DecisionBackend:
    """Build the production decider, reading its key by name at call time (never at import)."""
    api_key = os.getenv(DECISION_API_KEY_ENV)
    if not api_key:
        msg = f"The decision model needs its key in the environment variable {DECISION_API_KEY_ENV}."
        raise ValueError(msg)
    return TypeSafeClassifier(
        model=DECISION_MODEL_ID,
        api_key=api_key,
        base_url=DECISION_BASE_URL,
        timeout=DECISION_MODEL_TIMEOUT_SECONDS,
    )


class DecisionRegistry:
    """Resolve the decider and make decisions with it, recording each one."""

    def __init__(
        self,
        *,
        backend_builder: Callable[[], DecisionBackend] = build_backend,
        sink: Callable[[DecisionRecord], None] = log_record,
        usd_per_million_input_tokens: float = DECISION_USD_PER_MILLION_INPUT_TOKENS,
        clock: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._build = backend_builder
        self._sink = sink
        self._price = usd_per_million_input_tokens
        self._clock = clock
        self._backend: DecisionBackend | None = None

    def get(self) -> DecisionBackend:
        """The cached backend: one long-lived client, so connections are pooled."""
        if self._backend is None:
            self._backend = self._build()
        return self._backend

    def decide(
        self,
        state: State,
        questions: dict[str, Question],
        *,
        question_set: str,
    ) -> ClassifierResponse:
        """Ask ``questions`` about ``state``; record the decision; raise whatever the call raised.

        ``question_set`` names the questions' version (``"claim_check@1"``): a rewording is an
        API change, so it gets a new version and a new run on the labeled set.
        """
        started = self._clock()
        digest = state_hash(state)
        try:
            response = self.get().invoke({"state": state, "questions": questions})
        except Exception as error:
            self._sink(
                DecisionRecord(
                    question_set=question_set,
                    state_sha256=digest,
                    latency_ms=round((self._clock() - started) * 1000),
                    error=type(error).__name__,
                )
            )
            raise
        tokens = response.usage.input_tokens
        self._sink(
            DecisionRecord(
                question_set=question_set,
                state_sha256=digest,
                served_model=response.model,
                request_id=response.request_id,
                answers={
                    name: _answer_summary(answer)
                    for name, answer in response.answers.items()
                },
                latency_ms=round((self._clock() - started) * 1000),
                input_tokens=tokens,
                cost_usd=None if tokens is None else tokens * self._price / 1_000_000,
            )
        )
        return response


decision_model = DecisionRegistry()
