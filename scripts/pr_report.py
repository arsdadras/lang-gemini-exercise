"""Message and ownership report for GitHub Actions (`.github/workflows/messages.yml`).

    python scripts/pr_report.py --base <sha> --head <sha> --branch <head branch>
    python scripts/pr_report.py --summary

With `--base/--head`, it lists the messages a pull request adds or changes, and every changed
file its branch's role may not write (library/governance/ownership.md). With `--summary`, it
lists the open messages waiting for each role. Output is Markdown for the job summary; ownership
findings are also GitHub warning annotations. It reports and never fails the run: the local
guard prevents, this makes anything that slipped past visible to the lead (ADR-0020).
Standard library only.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import inbox
from workspace import (
    OWNERSHIP_FILE,
    ROLES,
    ROOT,
    git,
    owners,
    parse_ownership,
    role_of_branch,
    show,
)


def outbox_messages(ref: str, root: Path) -> dict[str, inbox.Message]:
    messages: dict[str, inbox.Message] = {}
    for sender in ROLES:
        text = show(ref, f"offices/{sender}/OUTBOX.md", root)
        if text:
            messages.update({m.id: m for m in inbox.parse_text(text, sender)})
    return messages


def message_changes(base: str, head: str, root: Path) -> list[str]:
    before, after = outbox_messages(base, root), outbox_messages(head, root)
    lines = []
    for mid, message in after.items():
        old = before.get(mid)
        to = ", ".join(message.recipients)
        if old is None:
            lines.append(
                f"- **{mid}** new, {message.sender} to {to}, {message.kind}, "
                f"{message.status}: {message.first_line}"
            )
        elif old.status != message.status:
            lines.append(f"- **{mid}** {old.status} -> {message.status}")
    return lines


def ownership_findings(
    base: str, head: str, branch: str, root: Path
) -> list[str] | None:
    """Changed files the branch's role may not write; None when the branch has no role."""
    role = role_of_branch(branch)
    if role is None:
        return None
    rules = parse_ownership(show(head, OWNERSHIP_FILE, root) or "")
    changed = git("diff", "--name-only", f"{base}...{head}", cwd=root).splitlines()
    findings = []
    for rel in changed:
        allowed = owners(rel, rules)
        if "all" not in allowed and role not in allowed:
            findings.append((rel, ", ".join(sorted(allowed))))
    return [f"{rel} (owner: {who})" for rel, who in findings]


def pr_report(base: str, head: str, branch: str, root: Path = ROOT) -> str:
    out = [f"## Messages and ownership: `{branch}`", ""]
    changes = message_changes(base, head, root)
    out.append("### Messages added or changed")
    out += changes or ["- none"]
    out.append("")
    out.append("### Files outside the branch's role")
    findings = ownership_findings(base, head, branch, root)
    if findings is None:
        out.append(f"- `{branch}` is not a role branch; ownership isn't checked.")
    else:
        out += [f"- {finding}" for finding in findings] or ["- none"]
        if os.environ.get("GITHUB_ACTIONS") == "true":
            for finding in findings:
                print(
                    f"::warning title=Outside {branch}'s paths::{finding}",
                    file=sys.stderr,
                )
    return "\n".join(out)


def summary(root: Path = ROOT) -> str:
    messages = inbox.load(root)
    out = ["## Open messages by recipient", ""]
    for role in ROLES:
        incoming, replies = inbox.inbox(messages, role)
        out.append(
            f"### {role}: {len(incoming)} open, {len(replies)} repl(ies) to verify"
        )
        out += [
            f"- **{m.id}** from {m.sender}, {m.kind}: {m.first_line}" for m in incoming
        ]
        out += [f"- **{m.id}** from {m.sender}, {m.kind}" for m in replies]
        out.append("")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base")
    parser.add_argument("--head")
    parser.add_argument("--branch", default="")
    parser.add_argument("--summary", action="store_true")
    args = parser.parse_args(argv)
    if args.summary:
        print(summary())
    elif args.base and args.head:
        print(pr_report(args.base, args.head, args.branch))
    else:
        parser.print_usage()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
