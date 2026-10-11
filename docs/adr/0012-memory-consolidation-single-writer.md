# ADR-0012: Memory has one writer, a background consolidator that proposes line-level edits

- Status: Accepted
- Date: 2026-09-22

## Context

- **Hot-path writes dropped facts.** A live run of six conversations (2026-09-19) left the
  profile with a conflicting job, a duplicated diet fact, and a stale city and gym goal. Facts
  mentioned in passing ("recommend a restaurant in Karaj, I live here now") were never saved:
  the assistant was busy with the actual request
  (`EV-2026-09-19-hot-path-memory-writes`).
- **The mentee proposed** that the assistant stop writing altogether, and that consolidation
  run in the background with its approvals asked the next time the user is back, instead of
  making the user wait at the end of a conversation.
- **A first build rewrote whole files.** The model returned each changed file in full with a
  list of changes. That breaks three promises: unrelated lines can change silently, the list
  shown to the user is the model's own account rather than the real change, and one rejection
  drops every change in the file.
- **Skipping an `interrupt()` on re-run shifts resume values** (verified by spike, LangGraph
  1.2.11). Resume values are matched to `interrupt()` calls by order within a node. The first
  build skipped files already stored before a pause, so the second question received the
  first answer: a rejected change was stored (`EV-2026-09-22-interrupt-resume-order`).

## Decision

- **The assistant only reads memory.** A `deny` permission on `/memories/**` covers it and its
  general-purpose subagent; the `memory-curation` skill is removed.
- **A consolidator graph is the single writer.** It runs after a conversation ends
  (`/new_thread`, `/user`) in a background thread; the CLI shows its proposal and asks for
  approvals before the user's next message.
- **The model proposes line-level edits; code applies them.** `add` (under a heading),
  `replace`, and `remove` of one exact line. Code finds the line and makes one gated write or
  edit through the B3 gate (ADR-0010), which is unchanged: additions map to additive edits,
  replacements and removals to destructive ones. An edit whose line is gone is skipped.
- **One edit per graph step.** `apply_next_edit` loops on a cursor, so each run holds at most
  one approval and a resumed run asks exactly the question it paused on.
- **Additions run first,** so ordinary facts land even if the user never reviews the rest.
- **The consolidator model is pinned to `claude-sonnet-5`** (medium tier): it resolved an
  implicit diet conflict 3/3 where `gpt-5.6-terra` resolved it 0/3
  (`EV-2026-09-19-consolidator-model-comparison`).

## Consequences

- A fact is available from the next conversation, not the same one; within a conversation,
  the message history already holds it.
- Approvals move from mid-conversation to one review between conversations.
- Line-level edits can't restructure a file; a large reorganization becomes many edits.
- The in-memory store loses unreviewed proposals on exit; durable review needs C1.

## Alternatives considered

- **Keep hot-path writes and add background cleanup:** rejected; two writers, and the
  assistant still multitasks.
- **Whole-file rewrites with a model-written change list:** rejected, see Context.
- **Collect every decision in one interrupt, then write:** rejected; the writes would pass the
  gate again and ask twice, or bypass the single enforcement point of ADR-0010.
- **Wait at the end of the conversation for approvals:** rejected by the mentee on UX grounds.
