import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_docs

LIBRARY_ENTRY = """---
title: Entry
maintainer: lead
status: current
updated: 2026-09-26
summary: One sentence.
related: [../README.md]
---

# Entry
"""


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    return tmp_path


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_slugify_matches_github_anchors():
    assert check_docs.slugify("2. Know the context (Asl-e Shenakht)") == (
        "2-know-the-context-asl-e-shenakht"
    )
    assert check_docs.slugify("Return pass (R0-R5)") == "return-pass-r0-r5"
    assert check_docs.slugify("The `uv` tool") == "the-uv-tool"


def test_valid_links_and_anchors_pass(repo):
    write(
        repo, "a.md", "# Top\n\n## Section two\n\n[b](sub/b.md) [self](#section-two)\n"
    )
    write(repo, "sub/b.md", "[back](../a.md#top) [web](https://example.com)\n")
    assert check_docs.run(repo, []) == []


def test_broken_link_and_missing_anchor_are_reported(repo):
    write(repo, "a.md", "[gone](missing.md)\n[bad](b.md#nowhere)\n")
    write(repo, "b.md", "# Only heading\n")
    problems = check_docs.run(repo, [])
    assert problems == [
        "a.md:1: broken link missing.md",
        "a.md:2: missing anchor b.md#nowhere",
    ]


def test_code_is_ignored_and_private_dirs_are_skipped(repo):
    write(repo, "a.md", "```\n[x](missing.md)\n```\nInline `[y](missing.md)` too.\n")
    write(repo, "alireza/notes.md", "[x](missing.md)\n")
    write(repo, "archive/old.md", "[x](missing.md)\n")
    assert check_docs.run(repo, []) == []


def test_duplicate_headings_get_numbered_anchors(repo):
    write(repo, "a.md", "## Step\n\n## Step\n\n[second](#step-1)\n")
    assert check_docs.run(repo, []) == []


def test_path_prefixes_limit_the_check(repo):
    write(repo, "a.md", "[gone](missing.md)\n")
    write(repo, "docs/b.md", "fine\n")
    assert check_docs.run(repo, ["docs"]) == []


def test_library_entry_needs_front_matter_and_index(repo):
    write(repo, "library/README.md", "# Library\n\n[entry](governance/entry.md)\n")
    write(repo, "library/LOG.md", "# Log\n")
    write(repo, "library/governance/entry.md", LIBRARY_ENTRY)
    write(repo, "library/governance/orphan.md", "# No front matter\n")
    write(
        repo,
        "library/governance/bad.md",
        LIBRARY_ENTRY.replace("maintainer: lead", "maintainer: bob").replace(
            "updated: 2026-09-26", "updated: soon"
        ),
    )
    problems = check_docs.check_library(repo)
    assert problems == [
        "library/governance/bad.md: maintainer must be 'lead', found 'bob'",
        "library/governance/bad.md: 'updated' is not YYYY-MM-DD",
        "library/governance/bad.md: not listed in library/README.md",
        "library/governance/orphan.md: missing front matter",
    ]


def test_library_entry_maintained_by_another_role_is_reported(repo):
    write(repo, "library/README.md", "# Library\n\n[entry](governance/entry.md)\n")
    for role in ("engineer", "mentor", "research"):
        write(
            repo,
            "library/governance/entry.md",
            LIBRARY_ENTRY.replace("maintainer: lead", f"maintainer: {role}"),
        )
        assert check_docs.check_library(repo) == [
            f"library/governance/entry.md: maintainer must be 'lead', found '{role}'"
        ]


def test_outbox_grammar(repo):
    write(
        repo,
        "offices/lead/OUTBOX.md",
        "## Open\n\n"
        "### LD-001 | to mentor | directive | open\n\nIssued.\n\n"
        "### LD-002 | to research, user | request | closed\n\n"
        "### LD-001 | to mentor | notice | open\n\n"
        "### MN-003 | to lead | notice | open\n\n"
        "### LD-004 | to boss | notice | pending\n\n"
        "### LD-005 | to mentor | reply MN-001 | open\n\n"
        "### Free-form heading\n",
    )
    write(repo, "offices/mentor/OUTBOX.md", "### MN-001 | to lead | directive | open\n")
    problems = check_docs.run(repo, ["offices"])
    assert problems == [
        "offices/lead/OUTBOX.md:9: duplicate ID LD-001",
        "offices/lead/OUTBOX.md:11: ID MN-003 must be LD-### in the lead outbox",
        "offices/lead/OUTBOX.md:13: unknown recipient boss",
        "offices/lead/OUTBOX.md:13: status must be open, closed, or withdrawn",
        "offices/lead/OUTBOX.md:15: reply status must be done, partial, or declined",
        "offices/lead/OUTBOX.md:17: heading is not 'ID | to <role> | <type> | <status>'",
        "offices/mentor/OUTBOX.md:1: only the lead sends directives",
    ]


def test_engineer_outbox_and_recipient(repo):
    write(
        repo,
        "offices/lead/OUTBOX.md",
        "### LD-001 | to engineer, mentor | directive | open\n",
    )
    write(
        repo,
        "offices/engineer/OUTBOX.md",
        "### EN-001 | to lead | reply LD-001 | done\n\n### LD-002 | to mentor | notice | open\n",
    )
    problems = check_docs.run(repo, ["offices"])
    assert problems == [
        "offices/engineer/OUTBOX.md:3: ID LD-002 must be EN-### in the engineer outbox"
    ]
