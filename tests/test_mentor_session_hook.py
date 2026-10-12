"""Unit tests for `scripts/mentor_session_hook.py` and `.agents/skills/teach/fa_isolate.py`."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from scripts.mentor_session_hook import (
    ROOT,
    build_orientation_message,
    extract_state_section,
    handle_hook,
    should_inject,
)


def test_should_inject_on_first_invocation_or_mentor_command() -> None:
    assert should_inject({"invocationNum": 1, "userRequest": "salam"}) is True
    assert should_inject({"invocationNum": 2, "userRequest": "salam"}) is False
    assert (
        should_inject({"invocationNum": 3, "userRequest": "/mentor edame bedim"})
        is True
    )
    assert should_inject({}) is True


def test_handle_hook_emits_ephemeral_message_from_state(tmp_path: Path) -> None:
    fake_state = tmp_path / "STATE.md"
    fake_state.write_text(
        "# Mentor State\n\n## Now & Execution Schedule\n\n- Phase 1-3 next.\n\n## Build queue\n\n1. Build workflows.\n",
        encoding="utf-8",
    )
    payload = json.dumps({"invocationNum": 1, "userRequest": "hi"})
    result = handle_hook(payload, state_path=fake_state)
    assert "ephemeralMessage" in result
    msg = result["ephemeralMessage"]
    assert "ADR-0033" in msg
    assert "Asl-e Ghorur" in msg
    assert "Phase 1-3 next." in msg
    assert "1. Build workflows." in msg


def test_handle_hook_stays_quiet_on_later_turns(tmp_path: Path) -> None:
    fake_state = tmp_path / "STATE.md"
    fake_state.write_text("# Mentor State\n", encoding="utf-8")
    payload = json.dumps({"invocationNum": 2, "userRequest": "edame"})
    assert handle_hook(payload, state_path=fake_state) == {}


def test_extract_state_section_stops_at_next_h2() -> None:
    sample = "# Title\n\n## Now\nline 1\nline 2\n\n## Build queue\nitem 1\n"
    assert extract_state_section(sample, "## Now") == "## Now\nline 1\nline 2"


def test_real_repo_state_and_hooks_json_are_valid() -> None:
    hooks_file = ROOT / ".agents" / "hooks.json"
    assert hooks_file.exists()
    hooks_cfg = json.loads(hooks_file.read_text(encoding="utf-8"))
    assert "hooks" in hooks_cfg
    assert "PreInvocation" in hooks_cfg["hooks"]

    msg = build_orientation_message()
    assert "Specialist[TInput, TReport]" in msg
    assert "workflows/" in msg


def test_fa_isolate_wraps_with_rlm_and_warns_on_bullets() -> None:
    fa_path = ROOT / ".agents" / "skills" / "teach" / "fa_isolate.py"
    spec = importlib.util.spec_from_file_location("fa_isolate", fa_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    converted, errors, warnings = module.convert(
        "این تابع <<`run_rag`>> خروجی <<RagReport>> می‌دهد."
    )
    assert not errors
    assert not warnings
    assert converted.startswith("\u200f")
    assert converted.endswith("\u200f")
    assert "\u200f\u2066`run_rag`\u2069\u200f" in converted

    _, _, bullet_warnings = module.convert("- مورد اول با <<Agent>> است.")
    assert any("bullet/numbered list" in w for w in bullet_warnings)
