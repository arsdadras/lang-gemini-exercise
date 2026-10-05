"""Eval-lite for R1's claim check: the decider and an LLM tier on the same labeled set.

Run by hand against real backends (ADR-0004), in test mode for the LLM:

    LLM_TEST_MODE=true uv run python evals/claim_check_eval.py [--threshold 0.8]

Prints one report per backend (accuracy per class, unsafe errors, latency, cost, coverage at the
threshold). An unsafe error here is `supports` for a claim the passage does not support: a false
citation. The thresholds in `nodes/claim_check_node.py` are fitted from these numbers.
"""

import argparse
import sys
import warnings

from dotenv import load_dotenv

from agentlab.configs.decision_config import DECISION_USD_PER_MILLION_INPUT_TOKENS
from agentlab.configs.paths_config import EVAL_DATASETS_DIR
from agentlab.models import decision_model, llm_model
from agentlab.nodes.claim_check_node import QUESTION_SET, _question
from agentlab.prompts.nodes.claim_check_prompt import CLAIM_VERDICT_PROMPT
from agentlab.schemas.output.research_output_schema import ClaimVerdict
from agentlab.utils.eval_util import (
    Decision,
    EvalCase,
    format_report,
    load_dataset,
    run_eval,
)


def decider_backend(case: EvalCase) -> Decision:
    """Jev through the seam: one question, the chosen label and its probability."""
    response = decision_model.decide(
        case.inputs["passage"],
        {"claim": _question(case.inputs["claim"])},
        question_set=QUESTION_SET,
    )
    answer = response.choices["claim"]
    tokens = response.usage.input_tokens or 0
    return Decision(
        label=answer.choice,
        probability=answer.probabilities[answer.choice],
        path="jev",
        cost=tokens * DECISION_USD_PER_MILLION_INPUT_TOKENS / 1_000_000,
    )


def llm_backend(case: EvalCase) -> Decision:
    """An LLM tier with structured output, the escalation path."""
    chain = CLAIM_VERDICT_PROMPT | llm_model.chain("low", structured=ClaimVerdict)
    verdict = chain.invoke(
        {"claim": case.inputs["claim"], "page": case.inputs["passage"]}
    )
    return Decision(label=verdict.verdict, path="llm:low")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--threshold", type=float, default=0.8)
    parser.add_argument("--only", choices=["jev", "llm"], default=None)
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    load_dotenv()
    dataset = load_dataset(EVAL_DATASETS_DIR / "claim_check.json")
    backends = {"jev": decider_backend, "llm": llm_backend}
    for name, backend in backends.items():
        if args.only in (None, name):
            print(f"== {name}")
            print(format_report(run_eval(dataset, backend, threshold=args.threshold)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
