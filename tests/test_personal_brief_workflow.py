"""Tests for Rung-3 personal brief workflow (P5 user context + P1 researcher)."""

from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from langchain_core.messages import HumanMessage, ToolMessage
from langgraph.store.memory import InMemoryStore

from agentlab.nodes import claim_check_node
from agentlab.schemas.output.research_output_schema import (
    Citation,
    DraftClaim,
    Evidence,
    ResearchDraft,
    ResearchReport,
    SourceDocument,
)
from agentlab.tools.user_context_tool import USER_CONTEXT_TOOL_NAME
from agentlab.workflows.personal_brief_workflow import (
    brief_request,
    make_brief_researcher_agent,
    run_personal_brief,
)


def test_brief_request_prompt_format() -> None:
    req = brief_request("AI safety benchmarks")
    assert "AI safety benchmarks" in req
    assert USER_CONTEXT_TOOL_NAME in req
    assert "First call get_user_context" in req


def test_make_brief_researcher_agent_compiles(monkeypatch: Any) -> None:
    store = InMemoryStore()
    monkeypatch.setenv("TAVILY_API_KEY", "tvly-test")
    agent = make_brief_researcher_agent(store)
    assert agent is not None


def test_run_personal_brief_end_to_end() -> None:
    store = InMemoryStore()
    store.put(
        ("alice", "memories"),
        "/profile.md",
        {"content": "- Prefers concise summaries\n- Focuses on enterprise"},
    )

    page_url = "https://example.com/safety"
    draft = ResearchDraft(
        topic="AI Safety",
        summary="Tailored for enterprise: AI safety overview.",
        claims=[
            DraftClaim(
                text="Enterprise adoption requires safety guards.",
                evidence=[Evidence(url=page_url, passage="safety guards")],
            )
        ],
        citations=[Citation(title="Doc", url=page_url)],
    )

    # Fake agent returning a completed research state with verified draft
    class FakeBriefAgent:
        def __init__(self) -> None:
            self._values = {
                "messages": [
                    HumanMessage("request"),
                    ToolMessage(
                        content=f"{page_url}\n\nsafety guards",
                        name="read_page",
                        tool_call_id="call_read",
                        artifact=[
                            SourceDocument(
                                url=page_url,
                                title="Doc",
                                kind="web",
                                text="safety guards",
                            )
                        ],
                    ),
                ],
                "structured_response": draft,
            }

        def get_state(self, config: Any) -> Any:
            return SimpleNamespace(values=self._values)

    fake_agent = FakeBriefAgent()

    def supports_all(_page: str, questions: dict[str, Any], **_: Any) -> Any:
        return SimpleNamespace(
            choices={
                k: SimpleNamespace(
                    choice="supports",
                    probabilities={"supports": 0.95},
                )
                for k in questions
            }
        )

    with (
        patch(
            "agentlab.workflows.personal_brief_workflow.make_brief_researcher_agent",
            return_value=fake_agent,
        ),
        patch(
            "agentlab.workflows.personal_brief_workflow.stream_with_hitl",
            return_value={"interrupts": []},
        ),
        patch.object(
            claim_check_node,
            "decision_model",
            SimpleNamespace(decide=supports_all),
        ),
    ):
        report = run_personal_brief(store, "alice", "AI Safety")

    assert report is not None
    assert isinstance(report, ResearchReport)
    assert "enterprise" in report.summary.lower()
    assert len(report.claims) == 1
    assert report.claims[0].status == "supported"
