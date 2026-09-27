---
name: research
description: Open a research session (the role that investigates, measures, and advises, and decides nothing). Invoked by the user only.
disable-model-invocation: true
---

This session is a **Research** session of the agentlab repository.

1. Before anything else, read the research office's charter and state: `offices/research/README.md`
   and `offices/research/STATE.md` (until LD-002 moves the office, the charter is
   `docs/research/README.md`, and LD-002 is your first task), then run
   `uv run python scripts/inbox.py research`.
2. Follow the charter. The principles and the protocol loaded by `CLAUDE.md` apply as always;
   the mentor charter it loads does not apply here.

If the user wrote a request after the command, handle it after steps 1-2.
