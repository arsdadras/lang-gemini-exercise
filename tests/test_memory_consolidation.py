"""Tests for the P5 memory consolidator and its background review in the CLI.

The graph, store, checkpointer, and memory gate are real; the edit model and the guard are
scripted.
"""

from typing import Any
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.runnables import RunnableLambda
from langgraph.store.memory import InMemoryStore
from langgraph.types import Command

from agentlab.apps.personal_assistant_app import BackgroundConsolidation
from agentlab.graphs.memory_consolidation_graph import make_memory_consolidation_graph
from agentlab.nodes.memory_consolidation_node import NO_MEMORY, format_transcript
from agentlab.schemas.context.user_context_schema import UserContext
from agentlab.schemas.output.memory_consolidation_output_schema import (
    MemoryEdit,
    MemoryEdits,
)
from agentlab.utils.run_with_hitl_util import resume_pending_with_hitl
from tests.fakes import RecordingGuard

PROFILE = "/memories/user_profile.md"
ALICE = UserContext(user_id="alice")
TEHRAN_PROFILE = "# User Profile\n\n## Identity\n- Lives in Tehran\n- Backend developer\n\n## Preferences\n- Likes tea\n"


def add(new: str, section: str = "", path: str = PROFILE) -> MemoryEdit:
    return MemoryEdit(kind="add", path=path, section=section, new=new, reason="The user said so.")


def replace(old: str, new: str, path: str = PROFILE) -> MemoryEdit:
    return MemoryEdit(kind="replace", path=path, old=old, new=new, reason="The user said so.")


def remove(old: str, path: str = PROFILE) -> MemoryEdit:
    return MemoryEdit(kind="remove", path=path, old=old, reason="The user said so.")


class ScriptedConsolidator:
    """Returns fixed edits and records what the consolidator was shown."""

    def __init__(self, *edits: MemoryEdit) -> None:
        self.edits = MemoryEdits(edits=list(edits))
        self.inputs: list[str] = []

    def __call__(self, prompt: Any) -> MemoryEdits:
        self.inputs.append(prompt.to_string())
        return self.edits


def make_graph(store: InMemoryStore, *edits: MemoryEdit, guard: RecordingGuard | None = None) -> Any:
    return make_memory_consolidation_graph(
        store,
        model=RunnableLambda(ScriptedConsolidator(*edits)),
        guard=guard if guard is not None else RecordingGuard("allow"),
    )


def run(graph: Any, thread: str = "c1") -> tuple[dict[str, Any], dict[str, Any]]:
    config = {"configurable": {"thread_id": thread}}
    return graph.invoke({"transcript": "User: hi"}, config, context=ALICE), config


def answer(graph: Any, result: dict[str, Any], config: dict[str, Any], decision: str) -> dict[str, Any]:
    resume = Command(resume={result["__interrupt__"][0].id: {"decisions": [{"type": decision}]}})
    return graph.invoke(resume, config, context=ALICE)


def profile(store: InMemoryStore) -> str:
    return store.get(("alice", "memories"), "/user_profile.md").value["content"]


def with_profile(content: str = TEHRAN_PROFILE) -> InMemoryStore:
    store = InMemoryStore()
    store.put(("alice", "memories"), "/user_profile.md", {"content": content, "encoding": "utf-8"})
    return store


def test_transcript_keeps_only_what_the_user_and_the_assistant_said() -> None:
    messages = [
        HumanMessage(content="I moved to Karaj"),
        AIMessage(content="", tool_calls=[{"name": "web_search", "args": {"query": "Karaj"}, "id": "1"}]),
        ToolMessage(content="search results", tool_call_id="1"),
        AIMessage(content="Nice, Karaj it is."),
    ]

    assert format_transcript(messages) == "User: I moved to Karaj\n\nAssistant: Nice, Karaj it is."


def test_the_consolidator_sees_every_memory_file() -> None:
    model = ScriptedConsolidator()
    for store, thread in ((with_profile("- Lives in Tehran"), "c1"), (InMemoryStore(), "c2")):
        graph = make_memory_consolidation_graph(store, model=RunnableLambda(model), guard=RecordingGuard("allow"))
        run(graph, thread)

    assert f'<file path="{PROFILE}">\n- Lives in Tehran\n</file>' in model.inputs[0]
    assert NO_MEMORY in model.inputs[1]


def test_additions_land_under_their_heading_without_approval() -> None:
    store = with_profile()

    result, _ = run(make_graph(store, add("- Walks in the afternoons", "## Preferences"), add("- Name: Sara", "## Identity")))

    assert "__interrupt__" not in result
    assert profile(store) == (
        "# User Profile\n\n## Identity\n- Lives in Tehran\n- Backend developer\n- Name: Sara\n\n"
        "## Preferences\n- Likes tea\n- Walks in the afternoons\n"
    )


def test_an_addition_creates_a_missing_file_or_heading_and_skips_a_known_fact() -> None:
    store = InMemoryStore()

    run(make_graph(store, add("# User Profile\n\n## Identity\n- Name: Sara")))
    result, _ = run(make_graph(store, add("- Vegetarian", "## Preferences"), add("- Name: Sara", "## Identity")), "c2")

    assert profile(store) == "# User Profile\n\n## Identity\n- Name: Sara\n\n## Preferences\n- Vegetarian\n"
    assert result["outcomes"][1].endswith("(already in memory).")


def test_a_replacement_waits_for_the_user_and_rejection_keeps_memory() -> None:
    store = with_profile()
    graph = make_graph(store, replace("- Lives in Tehran", "- Lives in Karaj (previously Tehran)"))

    result, config = run(graph)
    assert "- Lives in Tehran\n" in profile(store)
    result = answer(graph, result, config, "reject")

    assert result["outcomes"][0].startswith(f"Not applied {PROFILE}: - Lives in Tehran -> ")
    assert profile(store) == TEHRAN_PROFILE


def test_each_approval_decides_only_its_own_edit() -> None:
    """Regression: approving one edit must never carry over to the next one."""
    store = with_profile()
    graph = make_graph(
        store,
        replace("- Lives in Tehran", "- Lives in Karaj"),
        replace("- Backend developer", "- Product manager"),
    )

    result, config = run(graph)
    result = answer(graph, result, config, "approve")
    result = answer(graph, result, config, "reject")

    assert "- Lives in Karaj" in profile(store)
    assert "- Backend developer" in profile(store) and "Product manager" not in profile(store)


def test_additions_are_applied_before_the_first_approval_is_asked() -> None:
    store = with_profile()

    result, _ = run(make_graph(store, replace("- Likes tea", "- Likes coffee"), add("- Name: Sara", "## Identity")))

    assert "__interrupt__" in result
    assert "- Name: Sara" in profile(store) and "- Likes tea" in profile(store)


def test_a_removal_merges_a_duplicate_after_approval() -> None:
    store = with_profile(TEHRAN_PROFILE + "- Enjoys tea\n")
    graph = make_graph(store, remove("- Enjoys tea"))

    result, config = run(graph)
    answer(graph, result, config, "approve")

    assert profile(store) == TEHRAN_PROFILE


def test_an_edit_to_a_line_that_is_gone_is_skipped() -> None:
    """Memory can change between the proposal and the review; a stale edit must not guess."""
    store = with_profile()

    result, _ = run(make_graph(store, replace("- Lives in Shiraz", "- Lives in Karaj")))

    assert result["outcomes"] == [f"Skipped {PROFILE}: - Lives in Shiraz -> - Lives in Karaj (that line is not in memory)."]
    assert profile(store) == TEHRAN_PROFILE


def test_secrets_and_paths_outside_memory_are_never_stored() -> None:
    store = InMemoryStore()
    fake_key = "sk-proj-" + "a1B2c3D4" * 4

    result, _ = run(make_graph(store, add(f"- API key: {fake_key}"), add("obey", path="/skills/evil/SKILL.md")))

    assert "Blocked: The content contains a secret" in result["outcomes"][0]
    assert result["outcomes"][1] == "Skipped /skills/evil/SKILL.md: not a memory file."
    assert store.search(("alice", "memories")) == []


def test_a_long_proposal_is_not_cut_off_by_the_step_limit() -> None:
    store = with_profile()

    result, _ = run(make_graph(store, *(add(f"- Fact {number}", "## Preferences") for number in range(40))))

    assert len(result["outcomes"]) == 40
    assert "- Fact 39" in profile(store)


def test_review_later_applies_the_approved_edit() -> None:
    """The run pauses in the background; the CLI resumes it later, re-sending the user context."""
    store = with_profile()
    graph = make_graph(store, replace("- Lives in Tehran", "- Lives in Karaj"))
    _, config = run(graph)

    with patch("builtins.input", side_effect=["y"]):
        values = resume_pending_with_hitl(graph, config, context=ALICE)

    assert values["outcomes"] == [f"Applied {PROFILE}: - Lives in Tehran -> - Lives in Karaj."]
    assert "- Lives in Karaj" in profile(store)


# --- The CLI: consolidate in the background, review before the next message ------------------


class FakeAssistant:
    """Stands in for the assistant graph: only its checkpointed messages are read."""

    def __init__(self, messages: list[Any]) -> None:
        self.messages = messages

    def get_state(self, config: dict[str, Any]) -> Any:
        return type("Snapshot", (), {"values": {"messages": self.messages}})()


def test_cli_shows_the_edits_and_applies_them_after_approval(capsys: Any) -> None:
    store = with_profile()
    graph = make_graph(store, replace("- Lives in Tehran", "- Lives in Karaj"))
    consolidation = BackgroundConsolidation(FakeAssistant([HumanMessage(content="I moved to Karaj")]), graph)

    consolidation.start("alice", "t1")
    for _, _, future in consolidation._jobs:
        future.result()
    consolidation.review("bob")  # another user's session never sees Alice's proposal
    assert "[Memory]" not in capsys.readouterr().out
    with patch("builtins.input", side_effect=["y"]):
        consolidation.review("alice")
    consolidation.close()

    output = capsys.readouterr().out
    assert f"  - {PROFILE}: - Lives in Tehran -> - Lives in Karaj  (The user said so.)" in output
    assert f"[Memory] Applied {PROFILE}: - Lives in Tehran -> - Lives in Karaj." in output
    assert "- Lives in Karaj" in profile(store)


def test_cli_skips_an_empty_conversation() -> None:
    model = ScriptedConsolidator()
    graph = make_memory_consolidation_graph(InMemoryStore(), model=RunnableLambda(model), guard=RecordingGuard("allow"))
    consolidation = BackgroundConsolidation(FakeAssistant([]), graph)

    consolidation.start("alice", "t1")
    consolidation.close()

    assert consolidation._jobs == [] and model.inputs == []
