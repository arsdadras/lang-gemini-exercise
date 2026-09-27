"""Lint the repository's Markdown: links, anchors, library front matter and index, outboxes.

Usage:
    uv run python scripts/check_docs.py [PATH_PREFIX ...]

With no prefix every Markdown file git tracks or would track is checked; with prefixes only
files under them. `alireza/` (private) and `archive/` (frozen) are never checked. Exits 1 when
anything is wrong, printing one line per problem.
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIPPED_TOP_DIRS = {"alireza", "archive"}
LIBRARY_FIELDS = ("title", "maintainer", "status", "updated", "summary")
LIBRARY_ROLES = {"lead", "mentor", "research"}
LIBRARY_STATUSES = {"current", "draft", "superseded"}
LIBRARY_UNINDEXED = {"README.md", "LOG.md"}

OFFICE_PREFIX = {"lead": "LD", "mentor": "MN", "research": "RS"}
RECIPIENTS = {"lead", "mentor", "research", "user", "all"}
OPEN_STATUSES = {"open", "closed", "withdrawn"}
REPLY_STATUSES = {"done", "partial", "declined"}

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
MESSAGE_HEADING = re.compile(r"^###\s+(.*)$")
MESSAGE_ID = re.compile(r"^(LD|MN|RS)-\d{3}$")


def markdown_files(root: Path, prefixes: list[str]) -> list[Path]:
    """Markdown files git tracks or would track (untracked but not ignored)."""
    out = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.md"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    files = []
    for line in sorted(set(out.splitlines())):
        rel = Path(line)
        if rel.parts[0] in SKIPPED_TOP_DIRS or not (root / rel).is_file():
            continue
        if prefixes and not any(line.startswith(p.rstrip("/")) for p in prefixes):
            continue
        files.append(root / rel)
    return files


def prose_lines(text: str) -> list[tuple[int, str]]:
    """(line number, line) outside code fences, with inline code removed."""
    lines, in_fence = [], False
    for number, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((number, INLINE_CODE.sub("", line)))
    return lines


def slugify(heading: str) -> str:
    """GitHub's heading anchor: lowercase, punctuation dropped, spaces to hyphens."""
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # keep link text only
    text = text.replace("`", "").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    found: set[str] = set()
    counts: dict[str, int] = {}
    for _, line in prose_lines(path.read_text(encoding="utf-8")):
        match = HEADING.match(line)
        if not match:
            continue
        slug = slugify(match.group(2))
        n = counts.get(slug, 0)
        counts[slug] = n + 1
        found.add(slug if n == 0 else f"{slug}-{n}")
    return found


def check_links(path: Path, root: Path) -> list[str]:
    problems = []
    rel = path.relative_to(root).as_posix()
    for number, line in prose_lines(path.read_text(encoding="utf-8")):
        for target in LINK.findall(line):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue  # http:, https:, mailto:, ...
            file_part, _, anchor = target.partition("#")
            resolved = (path.parent / file_part).resolve() if file_part else path
            where = f"{rel}:{number}"
            if not resolved.exists():
                problems.append(f"{where}: broken link {target}")
                continue
            is_markdown = resolved.is_file() and resolved.suffix == ".md"
            if anchor and is_markdown and anchor not in anchors(resolved):
                problems.append(f"{where}: missing anchor {target}")
    return problems


def front_matter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fields = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def check_library(root: Path) -> list[str]:
    library = root / "library"
    if not library.is_dir():
        return []
    problems = []
    index = library / "README.md"
    index_text = index.read_text(encoding="utf-8") if index.is_file() else ""
    indexed = {
        (library / target.partition("#")[0]).resolve()
        for _, line in prose_lines(index_text)
        for target in LINK.findall(line)
    }
    for path in sorted(library.rglob("*.md")):
        if path.parent == library and path.name in LIBRARY_UNINDEXED:
            continue
        rel = path.relative_to(root).as_posix()
        fields = front_matter(path.read_text(encoding="utf-8"))
        if fields is None:
            problems.append(f"{rel}: missing front matter")
            continue
        for key in LIBRARY_FIELDS:
            if not fields.get(key):
                problems.append(f"{rel}: front matter lacks '{key}'")
        if fields.get("maintainer") and fields["maintainer"] not in LIBRARY_ROLES:
            problems.append(f"{rel}: unknown maintainer '{fields['maintainer']}'")
        if fields.get("status") and fields["status"] not in LIBRARY_STATUSES:
            problems.append(f"{rel}: unknown status '{fields['status']}'")
        if fields.get("updated"):
            try:
                date.fromisoformat(fields["updated"])
            except ValueError:
                problems.append(f"{rel}: 'updated' is not YYYY-MM-DD")
        related = fields.get("related", "").strip("[]")
        for item in filter(None, (r.strip() for r in related.split(","))):
            if not (path.parent / item).exists():
                problems.append(f"{rel}: related path not found: {item}")
        if path.resolve() not in indexed:
            problems.append(f"{rel}: not listed in library/README.md")
    return problems


def parse_heading(heading: str) -> tuple[str, list[str], str, str] | None:
    """`LD-001 | to mentor | directive | open` -> (id, recipients, type, status)."""
    parts = [p.strip() for p in heading.split("|")]
    if len(parts) != 4 or not parts[1].startswith("to "):
        return None
    recipients = [r.strip() for r in parts[1][3:].split(",")]
    return parts[0], recipients, parts[2], parts[3]


def check_outbox(path: Path, root: Path) -> list[str]:
    office = path.parent.name
    prefix = OFFICE_PREFIX.get(office)
    rel = path.relative_to(root).as_posix()
    if prefix is None:
        return [f"{rel}: outbox of unknown office '{office}'"]
    problems, seen = [], set()
    for number, line in prose_lines(path.read_text(encoding="utf-8")):
        match = MESSAGE_HEADING.match(line)
        if not match:
            continue
        where = f"{rel}:{number}"
        parsed = parse_heading(match.group(1))
        if parsed is None:
            problems.append(
                f"{where}: heading is not 'ID | to <role> | <type> | <status>'"
            )
            continue
        msg_id, recipients, kind, status = parsed
        if not MESSAGE_ID.match(msg_id) or not msg_id.startswith(prefix):
            problems.append(
                f"{where}: ID {msg_id} must be {prefix}-### in the {office} outbox"
            )
        if msg_id in seen:
            problems.append(f"{where}: duplicate ID {msg_id}")
        seen.add(msg_id)
        unknown = [r for r in recipients if r not in RECIPIENTS]
        if unknown:
            problems.append(f"{where}: unknown recipient {', '.join(unknown)}")
        if kind.startswith("reply "):
            if not MESSAGE_ID.match(kind[6:].strip()):
                problems.append(f"{where}: reply must name a message ID")
            if status not in REPLY_STATUSES:
                problems.append(
                    f"{where}: reply status must be done, partial, or declined"
                )
        elif kind in {"directive", "request", "notice"}:
            if kind == "directive" and office != "lead":
                problems.append(f"{where}: only the lead sends directives")
            if status not in OPEN_STATUSES:
                problems.append(f"{where}: status must be open, closed, or withdrawn")
        else:
            problems.append(f"{where}: unknown type '{kind}'")
    return problems


def run(root: Path, prefixes: list[str]) -> list[str]:
    problems = []
    for path in markdown_files(root, prefixes):
        problems += check_links(path, root)
    if not prefixes or any(p.startswith("library") for p in prefixes):
        problems += check_library(root)
    for path in sorted((root / "offices").glob("*/OUTBOX.md")):
        rel = path.relative_to(root).as_posix()
        if not prefixes or any(rel.startswith(p.rstrip("/")) for p in prefixes):
            problems += check_outbox(path, root)
    return problems


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    problems = run(ROOT, sys.argv[1:])
    for problem in problems:
        print(problem)
    print(f"check_docs: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
