"""Eval-lite for R1's source router (``research_sources@2``) on its labeled set.

Run by hand against the real decider (ADR-0004):

    uv run python evals/research_sources_eval.py [--threshold 0.6]

Each case is one (sub-question, source) judgment, asked on its own; production batches every
source of every sub-question in one request, which this set does not measure. The label is the
router's decision after code combines the answer: ``skip`` only on a sure ``no``
(``SKIP_THRESHOLD``), ``keep`` otherwise. An unsafe error is ``skip`` for a source the run needed.
"""

import argparse
import sys
import warnings

from dotenv import load_dotenv

from agentlab.configs.decision_config import DECISION_USD_PER_MILLION_INPUT_TOKENS
from agentlab.configs.paths_config import EVAL_DATASETS_DIR
from agentlab.configs.research_config import PROJECT_CORPUS
from agentlab.models import decision_model
from agentlab.nodes.source_route_node import (
    QUESTION_SET,
    SKIP_THRESHOLD,
    _question,
    _state,
)
from agentlab.utils.eval_util import (
    Decision,
    EvalCase,
    format_report,
    load_dataset,
    run_eval,
)


def make_decider(threshold: float):
    def decider(case: EvalCase) -> Decision:
        question = case.inputs["question"]
        response = decision_model.decide(
            _state([question], PROJECT_CORPUS),
            {"q": _question(1, question, case.inputs["source"], PROJECT_CORPUS)},
            question_set=QUESTION_SET,
        )
        answer = response.choices["q"]
        probability = answer.probabilities[answer.choice]
        skip = answer.choice == "no" and probability >= threshold
        tokens = response.usage.input_tokens or 0
        return Decision(
            label="skip" if skip else "keep",
            probability=probability,
            path=f"jev:{answer.choice}",
            cost=tokens * DECISION_USD_PER_MILLION_INPUT_TOKENS / 1_000_000,
        )

    return decider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--threshold", type=float, default=SKIP_THRESHOLD)
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    load_dotenv()
    dataset = load_dataset(EVAL_DATASETS_DIR / "research_sources.json")
    report = run_eval(dataset, make_decider(args.threshold))
    print(format_report(report))
    wrong = [r for r in report.results if not r.correct]
    for result in wrong:
        print(f"  wrong: {result.case_id} -> {result.predicted} ({result.path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
