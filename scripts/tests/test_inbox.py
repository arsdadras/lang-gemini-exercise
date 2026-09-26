import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import inbox


def write_outbox(root: Path, role: str, text: str) -> None:
    path = root / "offices" / role / "OUTBOX.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_parse_reads_headings_and_first_body_line(tmp_path):
    write_outbox(
        tmp_path,
        "lead",
        "# Lead Outbox\n\n## Open\n\n"
        "### LD-001 | to mentor, research | directive | open\n\nIssued 2026-09-26.\n\n"
        "## Closed\n\n- DIR-001: done.\n",
    )
    [message] = inbox.load(tmp_path)
    assert message.id == "LD-001"
    assert message.sender == "lead"
    assert message.recipients == ("mentor", "research")
    assert message.kind == "directive"
    assert message.first_line == "Issued 2026-09-26."


def test_inbox_lists_unanswered_open_messages_and_replies_to_verify(tmp_path):
    write_outbox(
        tmp_path,
        "lead",
        "### LD-001 | to mentor | directive | open\n"
        "### LD-002 | to mentor | notice | closed\n"
        "### LD-003 | to all | notice | open\n"
        "### LD-004 | to research | request | open\n"
        "### LD-005 | to mentor | request | open\n",
    )
    write_outbox(
        tmp_path,
        "mentor",
        "### MN-001 | to lead | reply LD-005 | done\n### MN-002 | to lead | request | open\n",
    )
    messages = inbox.load(tmp_path)

    incoming, replies = inbox.inbox(messages, "mentor")
    assert [m.id for m in incoming] == ["LD-001", "LD-003"]
    assert replies == []

    incoming, replies = inbox.inbox(messages, "lead")
    assert [m.id for m in incoming] == ["MN-002"]
    assert [m.id for m in replies] == ["MN-001"]
