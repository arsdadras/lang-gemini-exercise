import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_docs

LIBRARY_ENTRY = """---
title: Entry
maintainer: mentor
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
        LIBRARY_ENTRY.replace("maintainer: mentor", "maintainer: bob").replace(
            "updated: 2026-09-26", "updated: soon"
        ),
    )
    problems = check_docs.check_library(repo)
    assert problems == [
        "library/governance/bad.md: maintainer must be 'mentor', found 'bob'",
        "library/governance/bad.md: 'updated' is not YYYY-MM-DD",
        "library/governance/bad.md: not listed in library/README.md",
        "library/governance/orphan.md: missing front matter",
    ]


def test_library_entry_maintained_by_a_retired_role_is_reported(repo):
    write(repo, "library/README.md", "# Library\n\n[entry](governance/entry.md)\n")
    for role in ("lead", "engineer", "research"):
        write(
            repo,
            "library/governance/entry.md",
            LIBRARY_ENTRY.replace("maintainer: mentor", f"maintainer: {role}"),
        )
        assert check_docs.check_library(repo) == [
            f"library/governance/entry.md: maintainer must be 'mentor', found '{role}'"
        ]
