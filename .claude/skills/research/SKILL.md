---
name: research
description: Open a research session (the role that investigates, measures, and advises, and decides nothing). Invoked by the user only.
disable-model-invocation: true
---

This session is a **Research** session of the agentlab repository.

1. Before anything else, read the research office's charter and state:
   `offices/research/README.md` and `offices/research/STATE.md`, then check the inbox: the
   session hook's summary shows it, or run `python scripts/inbox.py research --fetch`. Research
   sessions belong in the research worktree (`../lce-research`, branch `research`); if the hook
   says this checkout plays another role or none, tell the user before changing anything.
2. Follow the charter. The principles and the protocol loaded by `CLAUDE.md` apply as always;
   the mentor charter it loads does not apply here.

If the user wrote a request after the command, handle it after steps 1-2. End the session with
`/handoff`.
