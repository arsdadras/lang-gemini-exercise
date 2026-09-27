---
name: lead
description: Open a lead session (the project-lead role for direction, curriculum and roadmap, architecture, technology, governance, and git). Invoked by the user only.
disable-model-invocation: true
---

This session is a **Lead** session of the agentlab repository.

1. Before anything else, read `offices/lead/README.md` (the lead's charter) and
   `offices/lead/STATE.md` (its current state), then run
   `uv run python scripts/inbox.py lead`.
2. Follow the charter: its session protocol, decision process, and report format. The
   principles and the protocol loaded by `CLAUDE.md` apply as always; the mentor charter it
   loads does not apply here.

If the user wrote a request after the command, handle it after steps 1-2.
