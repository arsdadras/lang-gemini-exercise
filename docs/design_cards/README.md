# Specialist Design Cards

A design card is the contract for one specialist agent. It is written at the project's
Session 0, before any implementation code. When the contract changes, edit the card and note
why. Progress is recorded in `docs/MENTOR_HANDOFF.md`, not here.

## Index

| Project | Card |
| :--- | :--- |
| P1-P4 | None (built before design cards existed; see `study_guides/` for P3 and P4) |
| P5 Memory-rich personal assistant | [P5_memory_assistant.md](P5_memory_assistant.md) |

## Template (15 points)

1. **User job:** the concrete problem it solves.
2. **Role boundary:** what it owns, and what it refuses or delegates.
3. **Environment:** the external state it can observe.
4. **Tools:** each tool and why tools aren't merged.
5. **Input:** typed input, config, and runtime context.
6. **Output:** typed final output.
7. **State:** transient, durable, and shared.
8. **Side effects:** what it changes outside the graph.
9. **Risk:** which actions need approval.
10. **Failure contract:** which errors can occur and how they surface.
11. **Verification:** how success is checked (tests, eval scenarios).
12. **Composition boundary:** how another workflow calls it.
13. **Cost and latency:** model tiers.
14. **Privacy boundary:** what it may read, store, or transmit.
15. **Phase C output:** the reusable artifact it hands to later projects.
