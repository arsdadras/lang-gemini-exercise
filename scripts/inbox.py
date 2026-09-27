"""Show a role's inbox: open messages addressed to it, and replies to its own open messages.

Usage:
    python scripts/inbox.py [lead|mentor|research] [--fetch]   # no role: this checkout's

Messages live in each office's OUTBOX.md (library/governance/protocol.md). Each role writes on
its own branch (ADR-0019), so an outbox is read from `origin/main`, from the sender's branch
`origin/<sender>`, and from this checkout; the newest copy of each message wins. `--fetch`
updates the remote refs first. Nothing is written; the role replies in its own outbox.
Standard library only.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from workspace import MAIN_BRANCH, REMOTE, ROLES, ROOT, detect_role, fetch, show


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
    return parse_text(path.read_text(encoding="utf-8"), sender)


def parse_text(text: str, sender: str) -> list[Message]:
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

    for line in text.splitlines():
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


def outbox_versions(root: Path, sender: str) -> list[str]:
    """Every copy of `sender`'s outbox, oldest first, so a later copy's message wins.

    The sender's own branch is newer than `main`; this checkout's copy is newest only when this
    checkout is the sender's worktree (elsewhere it may lag behind the sender's branch).
    """
    rel = f"offices/{sender}/OUTBOX.md"
    local_path = root / rel
    local = [local_path.read_text(encoding="utf-8")] if local_path.is_file() else []
    remote = [show(f"{REMOTE}/{ref}", rel, root) for ref in (MAIN_BRANCH, sender)]
    remote = [text for text in remote if text is not None]
    return remote + local if detect_role(root) == sender else local + remote


def load(root: Path) -> list[Message]:
    messages: dict[str, Message] = {}
    for sender in ROLES:
        for text in outbox_versions(root, sender):
            for message in parse_text(text, sender):
                messages[message.id] = message
    return list(messages.values())


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
    args = sys.argv[1:]
    do_fetch = "--fetch" in args
    args = [a for a in args if a != "--fetch"]
    role = args[0] if args else detect_role(ROOT)
    if len(args) > 1 or role not in ROLES:
        print(
            f"usage: inbox.py [{'|'.join(ROLES)}] [--fetch] (no role: this checkout's own)"
        )
        return 2
    if do_fetch and not fetch(ROOT):
        print("(fetch failed: remote copies may be stale)")
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
