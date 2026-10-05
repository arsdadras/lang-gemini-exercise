# ADR-0026: The specialist contract

- Status: Accepted
- Date: 2026-10-05
- Origin: lead, closing stage R0 ([roadmap](../../offices/lead/ROADMAP.md#return-pass-r0-r5),
  [ADR-0011](0011-return-pass-before-p6.md)); the user's go-ahead closed the stage.
- Revisit when: P6 composes specialists through inter-agent contracts, or a specialist needs a
  fourth status.

## Context

P1-P4 were built as standalone apps. P6 and every later workflow call them as specialists, so a
caller needs one answer to "did it work, where did the answer come from, what changed", and one
rule for "who retries". R0 taught and built that, in three topics.

## Decision

- **One result envelope,** `SpecialistResult[T]` (`schemas/output/specialist_output_schema.py`):
  `specialist`, `status`, `reason`, `output`, `provenance`, `side_effects`.
  - `status` is `ok`, `partial` (usable output, `reason` says what is missing: a fallback answered,
    or the run stopped at an approval), or `failed` (no usable answer, `reason` says why).
  - **Code decides `status`** from facts in the final state, never from the model's opinion of
    its own work.
  - `Provenance` names the source kind (`web`, `corpus`, `memory`, `sandbox`) and its reference;
    `SideEffect` names what changed (`created`, `modified`, `deleted`) and where.
  - `to_text()` renders the envelope for a model caller: status and sources first, then the answer.
- **One boundary per specialist,** a `run_*` function (`run_research`, `run_rag`,
  `run_code_review`, `run_interpreter`) that returns the envelope. An external failure becomes
  a `failed` envelope whose `reason` is `failure_reason(error)`, redacted; anything
  `failure_kind` can't classify is a bug and raises (`AGENTS.md`, convention 11).
- **One failure contract** (`utils/failure_util.py`):
  - an error is *transient* (rate limit, timeout, 5xx, network) or *permanent* (the other 4xx);
  - the classifier follows explicit `__cause__` links and knows each HTTP stack the SDKs use
    (`httpx2`, `httpx`, `requests`), so an SDK upgrade that moves a client is one edit;
  - one retry layer per call, chosen by what the call is (model SDK, `TRANSIENT_RETRY`,
    `ToolRetryMiddleware`), never two;
  - every external client has an explicit timeout (`configs/timeouts_config.py`), because a
    call that can hang never produces a failure the contract can classify.
- **One evaluation harness,** `utils/eval_util.py`: labeled cases, a decider injected per
  scenario, accuracy per class, unsafe errors, p50 and p95 latency, cost, and coverage at a
  threshold. It never calls a model itself. Decision points are its first datasets
  (`evals/datasets/`).
- **Per-app checkpoint databases** (`<app>_checkpoints.db`), so one app's session list shows
  only its own threads; delegated runs use a `delegations` database.

## Consequences

- **A caller composes without reading a specialist's insides:** it reads `status`, `reason`,
  and `provenance`, and only then `output`.
- **The remaining conformance items stay with their stages:** `UserContext` wherever user data
  is touched, one HITL path streamed by the app, redaction and trace masking in every app (R5),
  a design card per specialist before its stage, and an eval-lite smoke set of 5-10 scenarios.
  Each is checked in the R stage that touches the specialist.
- **`partial` is deliberately coarse.** If a caller needs to tell "fell back" from "stopped at an
  approval" without parsing `reason`, add a field then, not now (Principle 3: no predicted
  shapes).

## Alternatives considered

- **Raise on failure and let callers catch.** Rejected: a caller then needs each SDK's exception
  types, and a transient failure looks the same as a bug.
- **Let the model report its own status.** Rejected: the failure it reports most is the one it
  doesn't notice (low-tier models claim tool actions they never took).
