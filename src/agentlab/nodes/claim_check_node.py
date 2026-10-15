"""R1's claim check: every claim of a research draft against the documents the agent read.

One decision per (claim, page). Claims that cite the same page are asked together, one request
with a question per claim (``claim_check@1``). The decider answers first; the LLM only sees the
pairs the decider isn't sure about, or every pair when the decider is down, and it decides
them, except that it can never make a claim supported the decider did not label ``supports``.
A claim is ``supported`` only when a page says so,
``contradicted`` when any cited page says the opposite, and ``unsupported`` otherwise: no cited
page read, the page doesn't address it, or the check wasn't sure.

``confidence`` is arithmetic over the table, never a model's guess. The thresholds are provisional
until the labeled set (``evals/datasets/claim_check.json``) has the 200 cases a security-grade
fit needs (``decision-models.md``).

``make_check_node`` is the research graph's last node: it merges the sub-question drafts, checks
them, and caps the report by evidence, so a supported claim never gives way to an unsupported one.
"""

from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from itertools import zip_longest
from typing import Any, Literal

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_typesafe import Choice, ClassifierResponse, Question

from agentlab.configs.research_config import DEPTH_BUDGETS, MAX_PAGE_CHARS
from agentlab.models import decision_model, llm_model
from agentlab.prompts.nodes.claim_check_prompt import CLAIM_VERDICT_PROMPT
from agentlab.schemas.output.research_output_schema import (
    Claim,
    ClaimStatus,
    ClaimVerdict,
    DraftClaim,
    ResearchDraft,
    ResearchReport,
    SourceDocument,
)
from agentlab.schemas.output.specialist_output_schema import Provenance
from agentlab.schemas.state.research_state import ResearchState
from agentlab.utils.failure_util import failure_kind

QUESTION_SET = "claim_check@1"
Verdict = Literal["supports", "contradicts", "none"]
SUPPORTS_THRESHOLD = 0.8
CONTRADICTS_THRESHOLD = 0.6
_STRICTNESS: dict[Verdict, int] = {"supports": 2, "none": 1, "contradicts": 0}
_WINDOW_MARGIN = 1200
_ANCHOR_CHARS = 40

Decide = Callable[..., ClassifierResponse]


def page_window(
    text: str,
    passages: Sequence[str] = (),
    *,
    limit: int = MAX_PAGE_CHARS,
) -> str:
    """Slice ``text`` to at most ``limit`` chars, keeping windows around cited ``passages``.

    When ``text`` fits in ``limit`` (or no passage matches past ``limit``), returns ``text[:limit]``.
    When a joined corpus document or long page exceeds ``limit`` and a cited passage appears later
    in the document, extracts context windows around the matched passages so the claim check reads
    the part of the document the agent actually cited.
    """
    if len(text) <= limit or not passages:
        return text[:limit]
    lowered = text.lower()
    spans: list[tuple[int, int]] = []
    for raw in passages:
        needle = raw.strip()
        if not needle:
            continue
        pos = text.find(needle)
        if pos < 0:
            pos = lowered.find(needle.lower())
        if pos < 0 and len(needle) >= _ANCHOR_CHARS:
            pos = lowered.find(needle[:_ANCHOR_CHARS].lower())
        if pos >= 0:
            spans.append(
                (
                    max(0, pos - _WINDOW_MARGIN),
                    min(len(text), pos + len(needle) + _WINDOW_MARGIN),
                )
            )
    if not spans or all(end <= limit for _, end in spans):
        return text[:limit]
    spans.sort()
    merged: list[tuple[int, int]] = [spans[0]]
    for start, end in spans[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    sep = "\n...\n"
    body = sep.join(text[start:end] for start, end in merged)
    if len(body) >= limit or merged[0][0] == 0:
        return body[:limit]
    head_budget = min(merged[0][0], limit - len(body) - len(sep))
    if head_budget <= 0:
        return body[:limit]
    return f"{text[:head_budget]}{sep}{body}"[:limit]


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


def _llm_verdict(
    verdict_chain: Runnable[Any, ClaimVerdict], claim: str, page: str
) -> Verdict:
    result = verdict_chain.invoke({"claim": claim, "page": page[:MAX_PAGE_CHARS]})
    return result.verdict


def _escalated(decider: Verdict, llm: Verdict) -> Verdict:
    """The LLM's verdict on a pair the decider wasn't sure about, capped by the decider's label.

    An unsure ``supports`` can stay or drop; an unsure ``contradicts`` can stay or drop to
    ``none``. Neither becomes ``supports`` unless the decider said it: the check escalates or
    tightens, it never approves a claim on the LLM's word alone.
    """
    ceiling: Verdict = "supports" if decider == "supports" else "none"
    return min(llm, ceiling, key=_STRICTNESS.__getitem__)


def check_pair_group(
    page: str,
    claims: dict[str, str],
    *,
    decide: Decide,
    verdict_chain: Runnable[Any, ClaimVerdict],
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
            verdict = _escalated(verdict, _llm_verdict(verdict_chain, text, page))
        verdicts[key] = verdict
    return verdicts


def derive_confidence(claims: list[Claim]) -> float:
    """Confidence from the table: a claim scores 1 with two independent supporting documents, 0.7
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


def _checked(
    claim: DraftClaim,
    verdicts: dict[str, Verdict],
    documents: Mapping[str, SourceDocument],
) -> Claim:
    supporting = [url for url, verdict in verdicts.items() if verdict == "supports"]
    return Claim(
        text=claim.text,
        evidence=claim.evidence,
        status=_status(list(verdicts.values())),
        supporting_urls=supporting,
        source_kinds=sorted({documents[url].kind for url in supporting}),
    )


def _default_verdict_chain() -> Runnable[Any, ClaimVerdict]:
    """The LLM escalation, built only when a pair needs it: a sure decider builds no LLM client."""

    def verdict(inputs: dict[str, str]) -> ClaimVerdict:
        chain = CLAIM_VERDICT_PROMPT | llm_model.chain("low", structured=ClaimVerdict)
        return chain.invoke(inputs)

    return RunnableLambda(verdict)


def check_claims(
    draft: ResearchDraft,
    documents: Mapping[str, SourceDocument],
    *,
    decide: Decide | None = None,
    verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
) -> ResearchReport:
    """Check every claim of ``draft`` against ``documents`` (keyed by URL) and build the report.

    Each claim and citation carries the source kind of the documents behind it.
    """
    decide = decide or decision_model.decide
    verdict_chain = verdict_chain or _default_verdict_chain()
    by_page: dict[str, dict[str, str]] = {}
    passages_by_page: dict[str, list[str]] = {}
    for index, claim in enumerate(draft.claims):
        for evidence in claim.evidence:
            if evidence.url in documents:
                by_page.setdefault(evidence.url, {})[str(index)] = claim.text
                if evidence.passage:
                    passages_by_page.setdefault(evidence.url, []).append(
                        evidence.passage
                    )
    verdicts: dict[tuple[str, str], Verdict] = {}
    for url, claims in by_page.items():
        window = page_window(documents[url].text, passages_by_page.get(url, ()))
        group = check_pair_group(
            window, claims, decide=decide, verdict_chain=verdict_chain
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
        checked.append(_checked(claim, own, documents))
    # Provenance is a fact about the run: only documents a tool returned can be cited.
    citations = [c for c in draft.citations if c.url in documents]
    return ResearchReport(
        topic=draft.topic,
        summary=draft.summary,
        claims=checked,
        citations=citations,
        citation_kinds={c.url: documents[c.url].kind for c in citations},
        confidence=derive_confidence(checked),
    )


def unsupported_count(report: ResearchReport) -> int:
    """How many claims of ``report`` no cited page supports (unsupported or contradicted)."""
    return sum(claim.status != "supported" for claim in report.claims)


def _merge(topic: str, drafts: list[ResearchDraft]) -> ResearchDraft:
    """One draft from the sub-question drafts: claims interleaved and deduped, citations deduped.

    Claims are taken round-robin across sub-questions, so when the cap later drops claims of
    equal evidence, one sub-question that returned many can't crowd the others out. Identical
    claims across sub-questions are merged so their combined ``evidence`` lists corroborate one
    another instead of occupying two slots under the cap.
    """
    by_text: dict[str, DraftClaim] = {}
    for round_ in zip_longest(*(draft.claims for draft in drafts)):
        for claim in round_:
            if claim is None:
                continue
            key = " ".join(claim.text.split()).casefold()
            if key not in by_text:
                by_text[key] = claim
            else:
                existing = by_text[key]
                seen_ev = {(e.url, e.passage) for e in existing.evidence}
                extra = [e for e in claim.evidence if (e.url, e.passage) not in seen_ev]
                if extra:
                    by_text[key] = existing.model_copy(
                        update={"evidence": [*existing.evidence, *extra]}
                    )
    citations = {c.url: c for draft in drafts for c in draft.citations}
    summaries = list(
        dict.fromkeys(d.summary.strip() for d in drafts if d.summary.strip())
    )
    return ResearchDraft(
        topic=topic,
        summary=" ".join(summaries),
        claims=list(by_text.values()),
        citations=list(citations.values()),
    )


# Which claims the cap gives up last: evidence first, then the merge's round-robin order.
_CAP_ORDER = {"supported": 0, "unsupported": 1, "contradicted": 2}


def cap_claims(
    report: ResearchReport, max_claims: int
) -> tuple[ResearchReport, list[Claim]]:
    """The report cut to ``max_claims`` claims, supported ones kept first, and the dropped ones.

    The cap runs after the claim check so it drops by evidence, not by position. Confidence is
    derived again from what is kept, so it still describes the table the caller reads; the
    dropped claims go into the problems.
    """
    ranked = sorted(report.claims, key=lambda claim: _CAP_ORDER[claim.status])
    kept_ids = {id(claim) for claim in ranked[:max_claims]}
    kept = [claim for claim in report.claims if id(claim) in kept_ids]
    capped = report.model_copy(
        update={"claims": kept, "confidence": derive_confidence(kept)}
    )
    return capped, ranked[max_claims:]


_cap = cap_claims


def make_check_node(
    *,
    decide: Decide | None = None,
    verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
) -> Callable[..., dict]:
    """Build the node that merges the drafts, checks every claim, and applies the claim cap.

    With no draft (every run failed or waits for approval) it writes nothing: there is no report.
    The cap comes from the options' depth; without options there is none.
    """

    def check(state: ResearchState) -> dict:
        drafts = state.get("drafts", [])
        if not drafts:
            return {}
        report = check_claims(
            _merge(state["topic"], drafts),
            state.get("documents", {}),
            decide=decide,
            verdict_chain=verdict_chain,
        )
        problems: list[str] = []
        options = state.get("options")
        max_claims = None if options is None else DEPTH_BUDGETS[options.depth].claims
        if max_claims is not None and len(report.claims) > max_claims:
            report, dropped = cap_claims(report, max_claims)
            counts = Counter(claim.status for claim in dropped)
            problems.append(
                f"{len(dropped)} claims over the cap of {max_claims} were dropped ("
                + ", ".join(f"{n} {status}" for status, n in sorted(counts.items()))
                + ")."
            )
        unsupported = unsupported_count(report)
        if not report.claims:
            problems.append("The report has no claims.")
        elif unsupported:
            problems.append(
                f"{unsupported} of {len(report.claims)} claims are not supported by the "
                "pages the agent read."
            )
        provenance = [
            Provenance(
                kind=report.citation_kinds.get(citation.url, "web"),
                ref=citation.url,
                title=citation.title,
            )
            for citation in report.citations
        ]
        return {"report": report, "problems": problems, "provenance": provenance}

    return check
