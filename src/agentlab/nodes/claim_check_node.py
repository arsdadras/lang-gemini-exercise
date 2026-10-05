"""R1's claim check: every claim of a research draft against the pages the agent read.

One decision per (claim, page). Claims that cite the same page are asked together, one request
with a question per claim (``claim_check@1``). The decider answers first; the LLM only sees the
pairs the decider isn't sure about, or every pair when the decider is down, and it can keep a
verdict or lower it, never raise it. A claim is ``supported`` only when a page says so,
``contradicted`` when any cited page says the opposite, and ``unsupported`` otherwise: no cited
page read, the page doesn't address it, or the check wasn't sure.

``confidence`` is arithmetic over the table, never a model's guess. The thresholds are provisional
until the labeled set (``evals/datasets/claim_check.json``) has the 200 cases a security-grade
fit needs (``decision-models.md``).
"""

from collections.abc import Callable
from typing import Literal

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_typesafe import Choice, ClassifierResponse, Question

from agentlab.configs.research_config import MAX_PAGE_CHARS
from agentlab.models import decision_model, llm_model
from agentlab.prompts.nodes.claim_check_prompt import CLAIM_VERDICT_PROMPT
from agentlab.schemas.output.research_output_schema import (
    Claim,
    ClaimStatus,
    ClaimVerdict,
    DraftClaim,
    ResearchDraft,
    ResearchReport,
)
from agentlab.utils.failure_util import failure_kind

QUESTION_SET = "claim_check@1"
Verdict = Literal["supports", "contradicts", "none"]
SUPPORTS_THRESHOLD = 0.8
CONTRADICTS_THRESHOLD = 0.6
_STRICTNESS: dict[Verdict, int] = {"supports": 2, "none": 1, "contradicts": 0}

Decide = Callable[..., ClassifierResponse]


def _question(claim: str) -> Question:
    return Choice(
        instructions=(
            "Does the source page support this claim? A page that visits, names, or links "
            f"the subject without stating the claim does not support it.\nClaim: {claim}"
        ),
        criteria={
            "supports": "The page states the claim, in the same words or in words and numbers "
            "that mean the same.",
            "contradicts": "The page states the opposite of the claim, or a different value for "
            "the same thing.",
            "none": "The page does not address the claim, or only mentions its subject.",
        },
    )


def _decider_verdict(
    label: str, probabilities: dict[str, float]
) -> tuple[Verdict, bool]:
    """The decider's label as a verdict, and whether it was sure enough to stand alone."""
    probability = probabilities.get(label, 0.0)
    if label == "supports":
        return "supports", probability >= SUPPORTS_THRESHOLD
    if label == "contradicts":
        return "contradicts", probability >= CONTRADICTS_THRESHOLD
    return "none", True


def _llm_verdict(verdict_chain: Runnable, claim: str, page: str) -> Verdict:
    result = verdict_chain.invoke({"claim": claim, "page": page[:MAX_PAGE_CHARS]})
    return result.verdict


def _lowest(first: Verdict, second: Verdict) -> Verdict:
    """The stricter of two verdicts: the LLM can keep or lower the decider's, never raise it."""
    return min(first, second, key=_STRICTNESS.__getitem__)


def check_pair_group(
    page: str,
    claims: dict[str, str],
    *,
    decide: Decide,
    verdict_chain: Runnable,
) -> dict[str, Verdict]:
    """Verdicts for several claims that cite one page. Keys are the claim ids."""
    try:
        response = decide(
            page[:MAX_PAGE_CHARS],
            {key: _question(text) for key, text in claims.items()},
            question_set=QUESTION_SET,
        )
    except Exception as error:
        if failure_kind(error) is None:
            raise
        # A decider outage takes the LLM path for every pair.
        return {
            key: _llm_verdict(verdict_chain, text, page) for key, text in claims.items()
        }
    verdicts: dict[str, Verdict] = {}
    for key, text in claims.items():
        answer = response.choices[key]
        verdict, sure = _decider_verdict(answer.choice, answer.probabilities)
        if not sure:
            verdict = _lowest(verdict, _llm_verdict(verdict_chain, text, page))
        verdicts[key] = verdict
    return verdicts


def derive_confidence(claims: list[Claim]) -> float:
    """Confidence from the table: a claim scores 1 with two independent supporting pages, 0.7
    with one, 0 when unsupported or contradicted; the report's confidence is their mean."""
    if not claims:
        return 0.0
    total = 0.0
    for claim in claims:
        if claim.status != "supported":
            continue
        total += 1.0 if len(set(claim.supporting_urls)) >= 2 else 0.7
    return round(total / len(claims), 3)


def _status(verdicts: list[Verdict]) -> ClaimStatus:
    if "contradicts" in verdicts:
        return "contradicted"
    return "supported" if "supports" in verdicts else "unsupported"


def _checked(claim: DraftClaim, verdicts: dict[str, Verdict]) -> Claim:
    return Claim(
        text=claim.text,
        evidence=claim.evidence,
        status=_status(list(verdicts.values())),
        supporting_urls=[
            url for url, verdict in verdicts.items() if verdict == "supports"
        ],
    )


def _default_verdict_chain() -> Runnable:
    """The LLM escalation, built only when a pair needs it: a sure decider builds no LLM client."""

    def verdict(inputs: dict[str, str]) -> ClaimVerdict:
        chain = CLAIM_VERDICT_PROMPT | llm_model.chain("low", structured=ClaimVerdict)
        return chain.invoke(inputs)

    return RunnableLambda(verdict)


def check_claims(
    draft: ResearchDraft,
    pages: dict[str, str],
    *,
    decide: Decide | None = None,
    verdict_chain: Runnable | None = None,
) -> ResearchReport:
    """Check every claim of ``draft`` against ``pages`` (URL to text) and build the report."""
    decide = decide or decision_model.decide
    verdict_chain = verdict_chain or _default_verdict_chain()
    by_page: dict[str, dict[str, str]] = {}
    for index, claim in enumerate(draft.claims):
        for evidence in claim.evidence:
            if evidence.url in pages:
                by_page.setdefault(evidence.url, {})[str(index)] = claim.text
    verdicts: dict[tuple[str, str], Verdict] = {}
    for url, claims in by_page.items():
        group = check_pair_group(
            pages[url], claims, decide=decide, verdict_chain=verdict_chain
        )
        for key, verdict in group.items():
            verdicts[(key, url)] = verdict

    checked: list[Claim] = []
    for index, claim in enumerate(draft.claims):
        own = {
            url: verdicts[(str(index), url)]
            for url in dict.fromkeys(e.url for e in claim.evidence)
            if (str(index), url) in verdicts
        }
        checked.append(_checked(claim, own))
    return ResearchReport(
        topic=draft.topic,
        summary=draft.summary,
        claims=checked,
        # Provenance is a fact about the run: only pages the agent actually read can be sources.
        sources=[source for source in draft.sources if source.url in pages],
        confidence=derive_confidence(checked),
    )


def unsupported_count(report: ResearchReport) -> int:
    """How many claims of ``report`` no cited page supports (unsupported or contradicted)."""
    return sum(claim.status != "supported" for claim in report.claims)
