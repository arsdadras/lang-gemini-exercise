"""Eval-lite for the Jev model router (``model_route@1``) on its labeled set.

Run by hand against the real decider (ADR-0004), never by pytest:

    uv run python evals/model_route_eval.py [--low-mass 0.8] [--high-mass 0.5]

Each case is one task; the label is the tier the router picks after code combines the answers.
An unsafe error is ``low`` for a task labeled ``medium`` or ``high``. Only the decider is called;
nothing here calls a chat model.
"""

import argparse
import sys
import warnings

from dotenv import load_dotenv

from agentlab.configs import router_config
from agentlab.configs.decision_config import DECISION_USD_PER_MILLION_INPUT_TOKENS
from agentlab.configs.models_config import MODEL_TIERS
from agentlab.configs.paths_config import EVAL_DATASETS_DIR
from agentlab.models import decision_model
from agentlab.models.router_model import build_questions, build_state, tier_from_answers
from agentlab.utils.eval_util import (
    Decision,
    EvalCase,
    format_report,
    load_dataset,
    run_eval,
)


def make_decider(low_mass: float, high_mass: float):
    def decider(case: EvalCase) -> Decision:
        response = decision_model.decide(
            build_state(case.inputs["task"], MODEL_TIERS),
            build_questions(),
            question_set=router_config.QUESTION_SET,
        )
        decision = tier_from_answers(
            response,
            floor=router_config.ROUTED_TIERS[0],
            low_mass=low_mass,
            high_mass=high_mass,
        )
        probability = {
            "low": decision.p_easy,
            "high": decision.p_expert,
        }.get(decision.tier)
        tokens = response.usage.input_tokens or 0
        return Decision(
            label=decision.tier,
            probability=probability,
            path=f"jev:stakes={decision.stakes:.2f}",
            cost=tokens * DECISION_USD_PER_MILLION_INPUT_TOKENS / 1_000_000,
        )

    return decider


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--low-mass", type=float, default=router_config.LOW_MASS)
    parser.add_argument("--high-mass", type=float, default=router_config.HIGH_MASS)
    args = parser.parse_args()

    warnings.filterwarnings("ignore")
    load_dotenv()
    dataset = load_dataset(EVAL_DATASETS_DIR / "model_routes.json")
    report = run_eval(dataset, make_decider(args.low_mass, args.high_mass))
    print(format_report(report))
    for result in report.results:
        if not result.correct:
            print(
                f"  wrong: {result.case_id} {result.expected} -> {result.predicted} "
                f"({result.path})"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
