---
name: handoff
description: Close an agentlab session - rewrite mentor/STATE.md, run pytest, ruff, mypy, and check_docs, commit, push to main, and print a three-line summary. Use at the end of every session (/handoff).
---

Close this session so the next one can start from files alone
([git policy](../../../library/engineering/git-policy.md)).

1. **State.** Rewrite `mentor/STATE.md`: where the 4-Phase Master Plan and teaching stand, what is
   unfinished, the next session's exact scope, and the build queue. Append to `mentor/LOG.md` when
   a stage or project closed.
2. **Check.** Run all five verification commands and fix anything red before going on:
   - `uv run pytest -q`
   - `uv run ruff check src tests scripts`
   - `uv run ruff format --check src tests scripts`
   - `uv run mypy src/agentlab`
   - `uv run python scripts/check_docs.py`
   Look at `git status --short`: nothing from `alireza/`, no secret, no runtime output.
3. **Commit** everything with a conventional subject (`type(scope): summary`). Unfinished but
   green work is committed too; say in `STATE.md` what is unfinished.
4. **Push to `main`.** `git fetch origin`, then `git merge origin/main` if `main` moved, run
   the tests again if it did, and `git push origin HEAD:main`. Never force-push. If the main
   checkout (`D:\Repos\lang-gemini-exercise` on `main`) is clean and separate from the current
   worktree, fast-forward it with `git -C D:\Repos\lang-gemini-exercise merge --ff-only origin/main`
   so the learner reads the new code there. Never touch `D:\Repos\lang_claude_exercise`.
5. **Report** three lines: what was done (with clickable links to changed files), the commit, and
   what the next session will execute.
