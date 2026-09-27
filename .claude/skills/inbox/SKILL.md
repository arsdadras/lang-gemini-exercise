---
name: inbox
description: Show this role's inbox now - open messages addressed to it and replies to its own open messages, fetched from every role's branch. Use when the user asks for new messages, and with /loop (for example `/loop 15m /inbox`) to keep a long session aware of other roles.
---

1. Run `python scripts/inbox.py --fetch` (`python3` where `python` is missing). With no role
   argument it uses this worktree's own role; if it says the checkout plays no role, say so and
   stop.
2. Report each message in one line (ID, sender, type, first line). For a directive or request,
   say its timing and whether it blocks current work, following the protocol
   (`library/governance/protocol.md`); act on it only as your charter says.
3. If nothing is open, say so in one line.
