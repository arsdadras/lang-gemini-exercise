---
name: handoff
description: Close an agentlab session - rewrite mentor/STATE.md, run the checks, commit, push to main, and print a three-line summary. Use at the end of every session, and before switching machines or sessions.
---

Close this session so the next one can start from files alone
([git policy](../../../library/engineering/git-policy.md)).

1. **State.** Rewrite `mentor/STATE.md`: where teaching stands, what is unfinished, the next
   step, and the build queue. Append to `mentor/LOG.md` when a stage or project closed.
2. **Check.** `uv run pytest -q`, `uv run ruff check src tests scripts`,
   `uv run ruff format --check src tests scripts`, `uv run python scripts/check_docs.py`. Fix
   anything red before going on. Look at `git status --short`: nothing from `alireza/`, no
   secret, no runtime output.
3. **Commit** everything with a conventional subject (`type(scope): summary`) and the model
   attribution trailer the session was given. Unfinished but green work is committed too; say
   in `STATE.md` what is unfinished.
4. **Push to `main`.** `git fetch origin`, then `git merge origin/main` if `main` moved, run
   the tests again if it did, and `git push origin HEAD:main`. Never force-push. If the main
   checkout (`git worktree list`, the entry on `main`) is clean, fast-forward it with
   `git -C <main checkout> merge --ff-only origin/main` so the learner reads the new code there.
5. **Report** three lines: what was done, the commit, what comes next.
