# ADR-0010: One gate inside the memory storage, judging content as well as operation

- Status: Accepted
- Date: 2026-09-17

## Context

- **B2 judged operations, not content** ([ADR-0008](0008-memory-write-governance.md)). Adding a
  fact ran freely, so "I have asthma" or a wifi password was stored without review.
- **Approval and refusal needed different powers.** `HumanInTheLoopMiddleware` can only ask;
  it cannot refuse a call outright. A first design kept HITL for `ask` and added a backend
  check for `block`, which meant two enforcement points and a translation object between the
  tool-call shape and the backend shape. The mentee objected that one enforcement point should
  do both, and a spike confirmed it: a backend that calls `interrupt()` itself pauses the run,
  works for the general-purpose subagent, and needs no CLI change.
- **Custom middleware doesn't reach the general-purpose subagent** (`deepagents/graph.py:776`),
  while the backend is shared by every agent.
- **A resumed run re-runs the tool.** With a model in the decision path, a verdict computed
  before the pause can differ after it. A spike showed a rejected write executing because the
  second verdict was "allow".
- **`PIIMiddleware` protects the model's view, not persistence.** Verified: `apply_to_input`
  leaves the raw text in the input checkpoint, `apply_to_output` never touches tool-call
  arguments, and `block` crashes the run.
- **Rewriting a long answer to fix script leakage made it worse.** The rewriter introduced new
  Perso-Arabic words of its own.

## Decision

- **One gate, inside the memory storage.** `GatedMemoryBackend` applies one `MemoryGate`
  verdict per write, edit, or delete: code rules (destructive changes ask), then secret
  detectors (block), then the security guard on the new content, strictest wins. `ask` pauses
  with a standard `HITLRequest`, `block` returns an error the model reads. The memory
  `interrupt_on` rules from ADR-0008 are removed.
- **The guard's verdict is cached** in the user's store, keyed by the action and content hash,
  so a resumed run cannot reverse a human decision. Every verdict is cached, including
  "guard unavailable".
- **The guard is a classifier, not an agent:** one structured call, policy as a parameter,
  content delimited as data, and it can only make a verdict stricter. Any failure becomes
  `ask`.
- **Secrets are handled by one detector set** (LangSmith's `DEFAULT_SECRET_RULES` plus
  LangChain's Luhn card detector), applied where each risk is: redacted at the app boundary
  before the graph records anything, blocked in memory writes, and masked in traces through a
  LangSmith anonymizer. `PIIMiddleware` is not used in B3; it belongs where input protection
  must travel with the agent (C4).
- **Finglish output is repaired, not enforced.** Code detects Perso-Arabic by Unicode range,
  sends only the leaked lines in chunks of 20 to a low-tier structured rewrite, keeps a line
  only if its repair comes back clean, and stops after two passes.
- **`memory-curation` proposes sensitive facts** instead of skipping them, names the three
  outcomes, and keeps a rejected fact out of later saves in the same conversation.

## Consequences

- Approval now lives in the storage layer rather than the agent loop; the request shape stays
  the standard HITL one, so the CLI and HITL-aware UIs are unchanged.
- The gate runs twice per approved change (before the pause and after the resume); only the
  guard call is saved by the cache.
- Sensitive facts reach the user as approval prompts, which is friction the C2 eval measures.
- Script repair is partial: live runs cut leaked lines from 215 to 55 across three long plans.
  The root cause is the assistant model, and choosing it is a C2 measurement.

## Alternatives considered

- **HITL for `ask` plus a backend for `block`** (the first build): rejected after the spike;
  one door removes the second check and the translation object.
- **A tool the model calls before writing** (mentee's proposal): rejected as the gate. It is
  advisory, so a forgetful or steered model skips it; the same reasoning as ADR-0008's
  "the model classifying its own writes".
- **Letting the guard lift a code-required approval** (for example on a correction the user
  asked for): deferred to B4, once a changed memory keeps its previous version and a mistake
  is recoverable.
- **Giving the guard the conversation:** rejected; text in the conversation could then argue
  it into a softer verdict.
- **Rewriting the whole answer for Finglish:** rejected, measured worse than line-level repair.
