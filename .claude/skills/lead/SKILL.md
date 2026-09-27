---
name: lead
description: Open a lead session (the project-lead role for direction, curriculum and roadmap, architecture, technology, governance, and git). Invoked by the user only.
disable-model-invocation: true
---

This session is a **Lead** session of the agentlab repository.

1. Lead sessions run in the lead worktree (the session hook prints its path, the
   sibling folder `lce-lead`). If the hook says this checkout plays another role or none, move
   the session there first: in the desktop app call the `change_directory` tool with that path
   (use absolute paths until the move takes effect); in a terminal, ask the user to start
   claude in that folder.
2. Read `offices/lead/README.md` (the charter) and `offices/lead/STATE.md`, then act on the inbox the
   hook listed (or run `python scripts/inbox.py lead --fetch`).
3. Follow the charter. The principles and the protocol loaded by `CLAUDE.md` apply as always.

If the user wrote a request after the command, handle it after steps 1-3. End the session with
`/handoff`.
