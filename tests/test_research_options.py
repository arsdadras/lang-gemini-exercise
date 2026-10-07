"""R1 topic 2: research options, depth budgets, the planner, and the parallel research boundary."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda

from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.graphs.research_graph import build_research_graph
from agentlab.nodes import claim_check_node
from agentlab.nodes.claim_check_node import make_check_node
from agentlab.nodes.research_node import make_plan_node, plan_research
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    DraftClaim,
    Evidence,
    ResearchDraft,
    ResearchPlan,
    Source,
)
from agentlab.subagents.research_subagent import run_research
from agentlab.tools.read_page_tool import (
    READ_PAGE_TOOL_NAME,
    domain_allowed,
    make_read_page_tool,
)
from agentlab.tools.web_search_tool import make_web_search_tool

STANDARD = ResearchOptions(depth="standard")


def planner(*questions: str) -> RunnableLambda:
    return RunnableLambda(lambda _input: ResearchPlan(sub_questions=list(questions)))


def never_called(_input: Any) -> Any:
    raise AssertionError("the planner must not run")


# --- the planner -------------------------------------------------------------------------


def test_quick_depth_researches_the_topic_itself_without_planning() -> None:
    questions, cut = plan_research(
        "topic", ResearchOptions(depth="quick"), plan_chain=RunnableLambda(never_called)
    )

    assert (questions, cut) == (["topic"], [])


def test_the_plan_drops_blanks_and_repeats_without_a_replan() -> None:
    questions, cut = plan_research(
        "topic", STANDARD, plan_chain=planner("A", "  ", "A ", "B", "C")
    )

    assert (questions, cut) == (["A", "B", "C"], [])


def plans(*answers: list[str]) -> tuple[RunnableLambda, list[dict[str, Any]]]:
    """A planner that gives one answer per call, and the inputs it was called with."""
    calls: list[dict[str, Any]] = []

    def answer(inputs: dict[str, Any]) -> ResearchPlan:
        calls.append(inputs)
        return ResearchPlan(sub_questions=answers[len(calls) - 1])

    return RunnableLambda(answer), calls


def test_a_plan_over_the_cap_is_replanned_once_told_what_it_did() -> None:
    chain, calls = plans(["A", "B", "C", "D", "E"], ["A", "B and D", "C"])

    questions, cut = plan_research("topic", STANDARD, plan_chain=chain)

    assert (questions, cut) == (["A", "B and D", "C"], [])
    assert len(calls) == 2
    assert calls[0]["feedback"] == ""
    assert "5 sub-questions, over the limit of 3" in calls[1]["feedback"]
    assert "- E" in calls[1]["feedback"]


def test_a_replan_still_over_the_cap_is_cut_and_returns_what_was_cut() -> None:
    chain, calls = plans(["A", "B", "C", "D"], ["A", "B", "C", "D", "E"])

    questions, cut = plan_research("topic", STANDARD, plan_chain=chain)

    assert questions == ["A", "B", "C"]
    assert len(questions) == DEPTH_BUDGETS["standard"].sub_questions
    assert cut == ["D", "E"]
    assert len(calls) == 2


def test_an_empty_plan_falls_back_to_the_topic() -> None:
    assert plan_research("topic", STANDARD, plan_chain=planner(" ")) == (["topic"], [])


# --- domain filters on both tools --------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "include", "exclude", "allowed"),
    [
        ("https://docs.python.org/3/", ["python.org"], [], True),
        ("https://python.org.evil.com/", ["python.org"], [], False),
        ("https://WWW.Example.com/a", [], ["example.com"], False),
        ("https://a.org/x", [], [], True),
        ("https://a.org/x", ["a.org"], ["a.org"], False),
    ],
)
def test_domain_allowed_matches_hosts_and_subdomains_not_lookalikes(
    url: str, include: list[str], exclude: list[str], allowed: bool
) -> None:
    assert domain_allowed(url, include, exclude) is allowed


def test_reading_a_page_outside_the_allowed_domains_returns_an_error_without_a_call() -> (
    None
):
    tool = make_read_page_tool(include_domains=["a.org"])

    with patch("agentlab.tools.read_page_tool.requests.post") as post:
        result = tool.invoke({"url": "https://b.com/page"})

    assert "outside the domains" in result
    post.assert_not_called()


def test_the_search_tool_carries_the_callers_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")  # built, never called
    tool = make_web_search_tool(
        include_domains=["a.org"],
        exclude_domains=["b.com"],
        time_range="week",
        topic="news",
    )

    assert (tool.include_domains, tool.exclude_domains) == (["a.org"], ["b.com"])
    assert (tool.time_range, tool.topic) == ("week", "news")


# --- the research boundary ---------------------------------------------------------------


def read(url: str, text: str) -> ToolMessage:
    return ToolMessage(
        content=f"{url}\n\n{text}", name=READ_PAGE_TOOL_NAME, tool_call_id=url
    )


def finished(url: str, *claims: str) -> dict[str, Any]:
    """A sub-question run that read ``url`` and drafted ``claims`` citing it."""
    draft = ResearchDraft(
        topic="t",
        summary=f"about {url}",
        claims=[
            DraftClaim(text=text, evidence=[Evidence(url=url, passage="p")])
            for text in claims
        ],
        sources=[Source(title=url, url=url)],
    )
    return {"messages": [read(url, "page text")], "structured_response": draft}


class ByQuestion:
    """An agent stand-in: each question gets its own final state, or raises its error."""

    def __init__(self, outcomes: dict[str, Any]) -> None:
        self.outcomes = outcomes
        self.asked: list[str] = []

    def invoke(self, payload: Any, config: Any = None) -> Any:
        message: HumanMessage = payload["messages"][0]
        self.asked.append(message.content)
        outcome = self.outcomes[message.content]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def supports_everything(_page: str, questions: dict[str, Any], **_: Any) -> Any:
    choice = SimpleNamespace(choice="supports", probabilities={"supports": 0.95})
    return SimpleNamespace(choices={key: choice for key in questions})


def research(agent: ByQuestion, *questions: str) -> Any:
    registry = SimpleNamespace(decide=supports_everything)
    with patch.object(claim_check_node, "decision_model", registry):
        return run_research(agent, "topic", STANDARD, plan_chain=planner(*questions))


def test_each_sub_question_gets_its_own_run_and_claims_are_checked_against_its_pages() -> (
    None
):
    agent = ByQuestion(
        {
            "Q1": finished("https://a.org/1", "a1"),
            "Q2": finished("https://b.org/2", "b1"),
        }
    )

    result = research(agent, "Q1", "Q2")

    assert sorted(agent.asked) == ["Q1", "Q2"]
    assert result.status == "ok"
    assert [c.status for c in result.output.claims] == ["supported", "supported"]
    assert {p.ref for p in result.provenance} == {"https://a.org/1", "https://b.org/2"}


def test_the_claim_cap_keeps_every_sub_question_in_the_report() -> None:
    cap = DEPTH_BUDGETS["standard"].claims
    many = [f"a{i}" for i in range(cap + 1)]
    agent = ByQuestion(
        {
            "Q1": finished("https://a.org/1", *many),
            "Q2": finished("https://b.org/2", "b1", "b2"),
        }
    )

    result = research(agent, "Q1", "Q2")

    texts = [c.text for c in result.output.claims]
    assert len(texts) == cap
    assert {"b1", "b2"} <= set(texts)
    assert result.status == "partial"
    assert (
        f"3 claims over the cap of {cap} were dropped (3 supported)." in result.reason
    )


def test_the_claim_cap_keeps_supported_claims_before_unsupported_ones() -> None:
    cap = DEPTH_BUDGETS["standard"].claims
    weak = [f"weak{i}" for i in range(cap)]
    agent = ByQuestion(
        {
            "Q1": finished("https://a.org/1", *weak),
            "Q2": finished("https://b.org/2", "strong1", "strong2"),
        }
    )

    def supports_strong_only(_page: str, questions: dict[str, Any], **_: Any) -> Any:
        def choice(question: Any) -> Any:
            label = "none" if "weak" in question.instructions else "supports"
            return SimpleNamespace(choice=label, probabilities={label: 0.95})

        return SimpleNamespace(choices={k: choice(q) for k, q in questions.items()})

    registry = SimpleNamespace(decide=supports_strong_only)
    with patch.object(claim_check_node, "decision_model", registry):
        result = run_research(agent, "topic", STANDARD, plan_chain=planner("Q1", "Q2"))

    texts = [c.text for c in result.output.claims]
    assert len(texts) == cap
    assert {"strong1", "strong2"} <= set(texts)
    assert (
        f"2 claims over the cap of {cap} were dropped (2 unsupported)." in result.reason
    )
    assert result.output.confidence == round(2 * 0.7 / cap, 3)


def test_sub_questions_cut_by_the_cap_are_named_in_the_reason() -> None:
    agent = ByQuestion(
        {q: finished(f"https://{q}.org", f"{q}1") for q in ("Q1", "Q2", "Q3")}
    )

    result = research(agent, "Q1", "Q2", "Q3", "Q4")

    assert sorted(agent.asked) == ["Q1", "Q2", "Q3"]
    assert result.status == "partial"
    assert (
        "1 sub-questions over the cap of 3 were not researched: 'Q4'." in result.reason
    )


def test_a_failed_sub_question_leaves_a_partial_report_that_names_it() -> None:
    agent = ByQuestion(
        {"Q1": finished("https://a.org/1", "a1"), "Q2": TimeoutError("read timed out")}
    )

    result = research(agent, "Q1", "Q2")

    assert result.status == "partial"
    assert result.reason.startswith("'Q2': ")
    assert [c.text for c in result.output.claims] == ["a1"]


def test_a_planner_outage_fails_the_envelope() -> None:
    def down(_input: Any) -> Any:
        raise TimeoutError("planner timed out")

    result = run_research(
        ByQuestion({}), "topic", STANDARD, plan_chain=RunnableLambda(down)
    )

    assert result.status == "failed" and result.output is None


# --- the research graph ------------------------------------------------------------------


def test_the_graph_is_plan_then_research_then_check() -> None:
    graph = build_research_graph(ByQuestion({}), plan_chain=planner("Q1"))

    assert set(graph.get_graph().nodes) == {
        "__start__",
        "plan",
        "research",
        "check",
        "__end__",
    }


def test_the_check_runs_once_after_every_parallel_run() -> None:
    pages_asked: list[str] = []

    def count_pages(page: str, questions: dict[str, Any], **_: Any) -> Any:
        pages_asked.append(page)
        return supports_everything(page, questions)

    agent = ByQuestion(
        {
            "Q1": finished("https://a.org/1", "a1"),
            "Q2": finished("https://b.org/2", "b1"),
            "Q3": finished("https://c.org/3", "c1"),
        }
    )
    graph = build_research_graph(
        agent, plan_chain=planner("Q1", "Q2", "Q3"), decide=count_pages
    )

    state = graph.invoke({"topic": "topic", "options": STANDARD})

    assert sorted(agent.asked) == ["Q1", "Q2", "Q3"]
    assert len(pages_asked) == 3  # one request per page, in one check
    assert sorted(c.text for c in state["report"].claims) == ["a1", "b1", "c1"]


def test_without_options_the_plan_node_researches_the_topic_itself() -> None:
    plan = make_plan_node(RunnableLambda(never_called))

    assert plan({"topic": "topic", "options": None}) == {
        "questions": ["topic"],
        "cut": [],
    }


def test_the_check_node_writes_nothing_when_no_run_produced_a_draft() -> None:
    assert make_check_node()({"topic": "topic", "options": STANDARD}) == {}
