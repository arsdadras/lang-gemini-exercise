# Specialist Design Cards

A design card is the contract for one specialist agent. The lead writes it before the
project's Session 0 (or before the specialist's return-pass stage), and the mentor teaches from
it; the mentor proposes changes as request messages to the lead. When the contract changes, the
lead edits the card and notes why ([DEC-006](../../offices/lead/DECISIONS.md)). Progress is
recorded in the mentor's [state](../../offices/mentor/STATE.md), not here.

## Index

| Project | Card |
| :--- | :--- |
| P1-P4 | Planned: written by the lead before R1-R4 respectively (built before design cards existed; `docs/study_guides/` covers P3 and P4) |
| P5 Memory-rich personal assistant | [P5_memory_assistant.md](P5_memory_assistant.md) |

## Template (17 points)

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
16. **Production path:** what changes at production load (concurrent users, tenants, data
    volume, cost, failure rates) and the seam that makes each change a swap, not a rewrite
    ([ARCHITECTURE.md](../../offices/lead/ARCHITECTURE.md#scale-seams) "Scale seams").
17. **Decision points:** every step where a model decides rather than writes, with its options,
    labeled set, which error is unsafe, threshold and escalation, and the backend chosen by
    measurement ([decision-models.md](../../library/engineering/decision-models.md)).
