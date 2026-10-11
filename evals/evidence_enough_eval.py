"""Eval-lite for R1's stop condition (``evidence_enough@1``) on its labeled set.

Run by hand against the real decider (ADR-0004):

    uv run python evals/evidence_enough_eval.py [--threshold 0.8]

Each case is one (sub-question, documents read so far) judgment, asked as the middleware asks
it. The label is the middleware's decision after code combines the answer: ``enough`` only on a
sure ``yes`` (``ENOUGH_THRESHOLD``), ``not_enough`` otherwise. An unsafe error is ``enough`` for
a case whose documents don't answer the sub-question: it ends the search with a thin report.
"""

import argparse
import sys
import warnings

from dotenv import load_dotenv

from agentlab.configs.decision_config import DECISION_USD_PER_MILLION_INPUT_TOKENS
from agentlab.configs.paths_config import EVAL_DATASETS_DIR
from agentlab.middlewares.evidence_stop_middleware import (
    ENOUGH_THRESHOLD,
    QUESTION,
    QUESTION_SET,
    evidence_state,
)
from agentlab.models import decision_model
from agentlab.schemas.output.research_output_schema import SourceDocument
from agentlab.utils.eval_util import (
    Decision,
    EvalCase,
    format_report,
    load_dataset,
    run_eval,
)

SEPARATOR = "\n\n---\n\n"
"""Between the documents of a case: the labeled set keeps each case's documents in one string."""


def make_decider(threshold: float):
    def decider(case: EvalCase) -> Decision:
        documents = [
            SourceDocument(url=url, kind="web", text=text)
            for url, _, text in (
                block.partition("\n")
                for block in case.inputs["documents"].split(SEPARATOR)
            )
        ]
        response = decision_model.decide(
            evidence_state(case.inputs["question"], documents),
            {"q": QUESTION},
            question_set=QUESTION_SET,
        )
        answer = response.choices["q"]
        probability = answer.probabilities[answer.choice]
        enough = answer.choice == "yes" and probability >= threshold
        tokens = response.usage.input_tokens or 0
        return Decision(
            label="enough" if enough else "not_enough",
            probability=probability,
            path=f"jev:{answer.choice}",
            cost=tokens * DECISION_USD_PER_MILLION_INPUT_TOKENS / 1_000_000,
        )

    return decider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--threshold", type=float, default=ENOUGH_THRESHOLD)
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    load_dotenv()
    dataset = load_dataset(EVAL_DATASETS_DIR / "evidence_enough.json")
    report = run_eval(dataset, make_decider(args.threshold))
    print(format_report(report))
    for result in report.results:
        if not result.correct:
            print(f"  wrong: {result.case_id} -> {result.predicted} ({result.path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
