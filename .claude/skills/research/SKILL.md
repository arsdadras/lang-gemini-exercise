---
name: research
description: Open a research session (the role that investigates, analyzes, and advises, and decides nothing). Invoked by the user only.
disable-model-invocation: true
---

This session is a **Research** session of the agentlab repository.

1. Research sessions run in the research worktree (the session hook prints its path, the
   sibling folder `lce-research`). If the hook says this checkout plays another role or none, move
   the session there first: in the desktop app call the `change_directory` tool with that path
   (use absolute paths until the move takes effect); in a terminal, ask the user to start
   claude in that folder.
2. Read `offices/research/README.md` (the charter) and `offices/research/STATE.md`, then act on the inbox the
   hook listed (or run `python scripts/inbox.py research --fetch`).
3. Follow the charter. The principles and the protocol loaded by `CLAUDE.md` apply as always.

If the user wrote a request after the command, handle it after steps 1-3. End the session with
`/handoff`.
