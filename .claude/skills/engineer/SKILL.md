---
name: engineer
description: Open an engineer session (the role that implements, tests, debugs, and verifies the code and repo tooling the lead decides). Invoked by the user only.
disable-model-invocation: true
---

This session is an **Engineer** session of the agentlab repository.

1. Engineer sessions run in the engineer's worktree (the session hook prints its path, the
   sibling folder `lce-engineer`). If the hook says this checkout plays another role or none,
   move the session there first: in the desktop app call the `change_directory` tool with that
   path (use absolute paths until the move takes effect); in a terminal, ask the user to start
   claude in that folder.
2. Read `offices/engineer/README.md` (the charter) and `offices/engineer/STATE.md`, then act on
   the inbox the hook listed (or run `python scripts/inbox.py engineer --fetch`).
3. Follow the charter. The principles and the protocol loaded by `CLAUDE.md` apply as always.

If the user wrote a request after the command, handle it after steps 1-3. End the session with
`/handoff`.
