"""R1's claim check: statuses come from pages, confidence from the table, the LLM only lowers."""

from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langchain_typesafe import ClassifierResponse

from agentlab.models.decision_model import DecisionRegistry
from agentlab.nodes import claim_check_node
from agentlab.nodes.claim_check_node import (
    CONTRADICTS_THRESHOLD,
    SUPPORTS_THRESHOLD,
    check_claims,
    derive_confidence,
    unsupported_count,
)
from agentlab.schemas.output.research_output_schema import (
    Claim,
    ClaimVerdict,
    DraftClaim,
    Evidence,
    ResearchDraft,
    Source,
)
from agentlab.subagents.research_subagent import run_research
from agentlab.tools.read_page_tool import READ_PAGE_TOOL_NAME
from agentlab.tools.research_source_tool import documents_read
from tests.fakes import scripted_decider
from tests.test_specialist_contract import Returns, rejected

PAGE_A = "https://a.example/page"
PAGE_B = "https://b.example/page"


def answer(**verdicts: tuple[str, float]) -> ClassifierResponse:
    """A decider response: per claim index (``c0``, ``c1``), the chosen label and probability."""
    answers: dict[str, Any] = {}
    for key, (label, probability) in verdicts.items():
        rest = (1 - probability) / 2
        probabilities = {"supports": rest, "contradicts": rest, "none": rest}
        probabilities[label] = probability
        answers[key.removeprefix("c")] = {
            "type": "choice",
            "choice": label,
            "probabilities": probabilities,
            "confidence": probability,
        }
    return ClassifierResponse.model_validate(
        {"model": "jev-1.13.0", "answers": answers, "usage": {"input_tokens": 100}}
    )


def registry(*responses: Any) -> DecisionRegistry:
    return DecisionRegistry(
        backend_builder=lambda: scripted_decider(*responses), sink=lambda _r: None
    )


def decider(*responses: Any) -> Any:
    return registry(*responses).decide


def llm(*verdicts: str) -> RunnableLambda:
    queue = list(verdicts)
    return RunnableLambda(lambda _input: ClaimVerdict(verdict=queue.pop(0)))  # type: ignore[arg-type]


def draft(*claims: tuple[str, str]) -> ResearchDraft:
    return ResearchDraft(
        topic="t",
        summary="s",
        claims=[
            DraftClaim(text=text, evidence=[Evidence(url=url, passage="p")])
            for text, url in claims
        ],
        sources=[Source(title="A", url=PAGE_A)],
    )


def test_a_claim_the_page_states_is_supported_and_one_it_only_mentions_is_not() -> None:
    report = check_claims(
        draft(("X is 5", PAGE_A), ("Y is 7", PAGE_A)),
        {PAGE_A: "X is 5."},
        decide=decider(answer(c0=("supports", 0.95), c1=("none", 0.9))),
        verdict_chain=llm(),
    )

    assert [c.status for c in report.claims] == ["supported", "unsupported"]
    assert report.claims[0].supporting_urls == [PAGE_A]
    assert unsupported_count(report) == 1


def test_a_source_the_agent_never_read_is_dropped_from_the_report() -> None:
    cited = draft(("X is 5", PAGE_A))
    cited.sources.append(Source(title="B", url=PAGE_B))

    report = check_claims(
        cited,
        {PAGE_A: "X is 5."},
        decide=decider(answer(c0=("supports", 0.95))),
        verdict_chain=llm(),
    )

    assert [source.url for source in report.sources] == [PAGE_A]


def test_a_page_that_says_the_opposite_contradicts_the_claim() -> None:
    report = check_claims(
        draft(("X is 5", PAGE_A)),
        {PAGE_A: "X is 9."},
        decide=decider(answer(c0=("contradicts", 0.9))),
        verdict_chain=llm(),
    )

    assert report.claims[0].status == "contradicted"
    assert report.confidence == 0


def test_claims_citing_one_page_are_asked_in_one_request() -> None:
    seen: list[dict[str, Any]] = []

    def backend(request: dict[str, Any]) -> ClassifierResponse:
        seen.append(request)
        return answer(c0=("supports", 0.9), c1=("supports", 0.9))

    check_claims(
        draft(("A", PAGE_A), ("B", PAGE_A)),
        {PAGE_A: "page"},
        decide=DecisionRegistry(
            backend_builder=lambda: RunnableLambda(backend), sink=lambda _r: None
        ).decide,
        verdict_chain=llm(),
    )

    assert len(seen) == 1 and set(seen[0]["questions"]) == {"0", "1"}


def test_a_claim_whose_page_was_never_read_is_unsupported_and_asks_nothing() -> None:
    report = check_claims(
        draft(("X", PAGE_B)),
        {PAGE_A: "other page"},
        decide=decider(),
        verdict_chain=llm(),
    )

    assert report.claims[0].status == "unsupported"


def test_an_unsure_supports_goes_to_the_llm_which_can_lower_it_but_not_raise_it() -> (
    None
):
    unsure = SUPPORTS_THRESHOLD - 0.2
    lowered = check_claims(
        draft(("X", PAGE_A)),
        {PAGE_A: "page"},
        decide=decider(answer(c0=("supports", unsure))),
        verdict_chain=llm("none"),
    )
    kept = check_claims(
        draft(("X", PAGE_A)),
        {PAGE_A: "page"},
        decide=decider(answer(c0=("supports", unsure))),
        verdict_chain=llm("supports"),
    )
    not_raised = check_claims(
        draft(("X", PAGE_A)),
        {PAGE_A: "page"},
        decide=decider(answer(c0=("contradicts", CONTRADICTS_THRESHOLD - 0.2))),
        verdict_chain=llm("supports"),
    )

    assert lowered.claims[0].status == "unsupported"
    assert kept.claims[0].status == "supported"
    assert not_raised.claims[0].status == "contradicted"


def test_a_sure_decider_never_asks_the_llm() -> None:
    check_claims(
        draft(("X", PAGE_A)),
        {PAGE_A: "page"},
        decide=decider(answer(c0=("supports", 0.95))),
        verdict_chain=RunnableLambda(lambda _i: pytest.fail("the LLM was asked")),
    )


def test_a_decider_outage_takes_the_llm_path_for_every_pair() -> None:
    report = check_claims(
        draft(("A", PAGE_A), ("B", PAGE_A)),
        {PAGE_A: "page"},
        decide=decider(rejected(503)),
        verdict_chain=llm("supports", "none"),
    )

    assert [c.status for c in report.claims] == ["supported", "unsupported"]


def test_a_decider_bug_is_not_swallowed() -> None:
    with pytest.raises(KeyError):
        check_claims(
            draft(("A", PAGE_A)),
            {PAGE_A: "page"},
            decide=decider(KeyError("bug")),
            verdict_chain=llm(),
        )


def table(*statuses: str, urls: int = 1) -> list[Claim]:
    return [
        Claim(
            text="c",
            evidence=[],
            status=status,  # type: ignore[arg-type]
            supporting_urls=[f"u{i}" for i in range(urls)]
            if status == "supported"
            else [],
        )
        for status in statuses
    ]


def test_confidence_comes_from_the_table_and_rewards_agreeing_pages() -> None:
    assert derive_confidence([]) == 0
    assert derive_confidence(table("unsupported", "contradicted")) == 0
    assert derive_confidence(table("supported")) == pytest.approx(0.7)
    assert derive_confidence(table("supported", urls=2)) == 1.0
    assert derive_confidence(table("supported", "unsupported")) == pytest.approx(0.35)


def read(url: str, text: str, kind: str = "web") -> ToolMessage:
    """A source tool's result: the text the model reads and the document as its artifact."""
    return ToolMessage(
        content=f"{url}\n\n{text}",
        name=READ_PAGE_TOOL_NAME,
        tool_call_id=url,
        artifact=[{"url": url, "title": "", "kind": kind, "text": text}],
    )


def test_documents_read_takes_every_source_tools_artifact_and_skips_failures() -> None:
    messages = [
        AIMessage(content=""),
        read(PAGE_A, "The text."),
        read(PAGE_B, "A paper.", kind="academic"),
        ToolMessage(
            content="Could not read",
            name=READ_PAGE_TOOL_NAME,
            tool_call_id="2",
            status="error",
        ),
        # Search snippets carry no artifact: the model saw them, but they are not evidence.
        ToolMessage(content="snippets", name="web_search", tool_call_id="3"),
    ]

    documents = documents_read(messages)

    assert {url: (d.kind, d.text) for url, d in documents.items()} == {
        PAGE_A: ("web", "The text."),
        PAGE_B: ("academic", "A paper."),
    }


def run(claims_draft: ResearchDraft, pages: dict[str, str], response: Any) -> Any:
    state = {
        "messages": [read(url, text) for url, text in pages.items()],
        "structured_response": claims_draft,
    }
    with patch.object(claim_check_node, "decision_model", registry(response)):
        return run_research(Returns(state), "topic")


def test_a_report_whose_claims_are_all_supported_is_ok_with_sources() -> None:
    result = run(
        draft(("X is 5", PAGE_A)),
        {PAGE_A: "X is 5."},
        answer(c0=("supports", 0.95)),
    )

    assert result.status == "ok" and result.reason == ""
    assert result.output.claims[0].status == "supported"
    assert result.provenance[0].ref == PAGE_A


def test_a_report_with_an_unsupported_claim_is_partial_and_says_how_many() -> None:
    result = run(
        draft(("X is 5", PAGE_A), ("Z", PAGE_A)),
        {PAGE_A: "X is 5."},
        answer(c0=("supports", 0.95), c1=("none", 0.9)),
    )

    assert result.status == "partial"
    assert (
        result.reason == "1 of 2 claims are not supported by the pages the agent read."
    )
    assert result.output is not None


def test_a_report_without_claims_is_partial() -> None:
    result = run(draft(), {}, None)

    assert result.status == "partial" and result.reason == "The report has no claims."


def test_a_check_that_hits_an_outage_fails_the_envelope_instead_of_crashing() -> None:
    state = {
        "messages": [read(PAGE_A, "X")],
        "structured_response": draft(("X", PAGE_A)),
    }

    def boom(*_args: Any, **_kwargs: Any) -> Any:
        raise rejected(503)

    with patch.object(claim_check_node, "check_pair_group", boom):
        result = run_research(Returns(state), "topic")

    assert result.status == "failed" and "unavailable" in result.reason
