"""Show a role's inbox: open messages addressed to it, and replies to its own open messages.

Usage:
    uv run python scripts/inbox.py <lead|mentor|research>

Messages live in each office's OUTBOX.md (library/governance/protocol.md). Nothing is
written; the role replies in its own outbox.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROLES = ("lead", "mentor", "research")


@dataclass(frozen=True)
class Message:
    id: str
    sender: str
    recipients: tuple[str, ...]
    kind: str
    status: str
    first_line: str

    @property
    def replies_to(self) -> str | None:
        return self.kind[6:].strip() if self.kind.startswith("reply ") else None


def parse_outbox(path: Path, sender: str) -> list[Message]:
    messages: list[Message] = []
    heading: list[str] | None = None
    body: list[str] = []

    def flush() -> None:
        if heading is None:
            return
        msg_id, to, kind, status = heading
        recipients = tuple(r.strip() for r in to.removeprefix("to ").split(","))
        first = next((line.strip() for line in body if line.strip()), "")
        messages.append(Message(msg_id, sender, recipients, kind, status, first))

    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### "):
            flush()
            parts = [p.strip() for p in line[4:].split("|")]
            heading, body = (parts if len(parts) == 4 else None), []
        elif line.startswith("## "):
            flush()
            heading, body = None, []
        elif heading is not None:
            body.append(line)
    flush()
    return messages


def load(root: Path) -> list[Message]:
    messages = []
    for role in ROLES:
        path = root / "offices" / role / "OUTBOX.md"
        if path.is_file():
            messages += parse_outbox(path, role)
    return messages


def inbox(messages: list[Message], role: str) -> tuple[list[Message], list[Message]]:
    """(open messages to `role` it hasn't replied to, replies to `role`'s open messages)."""
    answered = {m.replies_to for m in messages if m.sender == role and m.replies_to}
    incoming = [
        m
        for m in messages
        if m.sender != role
        and m.status == "open"
        and m.replies_to is None
        and (role in m.recipients or "all" in m.recipients)
        and m.id not in answered
    ]
    own_open = {m.id for m in messages if m.sender == role and m.status == "open"}
    replies = [m for m in messages if m.replies_to in own_open]
    return incoming, replies


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) != 2 or sys.argv[1] not in ROLES:
        print(f"usage: inbox.py <{'|'.join(ROLES)}>")
        return 2
    role = sys.argv[1]
    incoming, replies = inbox(load(ROOT), role)
    print(f"Inbox for {role}: {len(incoming)} open message(s)")
    for m in incoming:
        print(f"  {m.id} from {m.sender} | {m.kind} | {m.first_line}")
    print(f"Replies to verify: {len(replies)}")
    for m in replies:
        print(f"  {m.id} from {m.sender} | {m.kind} | {m.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
