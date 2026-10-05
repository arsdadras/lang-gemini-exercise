# ADR-0021: Decision models as a second model family, and one standard for every decision point

- Status: Accepted
- Date: 2026-09-28
- Origin: user direction (the Jev file, opened 2026-09-27); research's BR-003 version 3; the
  lead's [dossier](../../mentor/artifacts/jev-dossier.md), accepted in full by the user
  after the joint review. Supersedes the "P8-C3 first" part of DEC-004.
- Revisit when: a Jev release or an alias move; `langchain-typesafe` leaves alpha, or is still
  alpha at P8-C3; R2's measurement; a Finglish or Persian study.

## Update (2026-10-05)

The seam is built (`models/decision_model.py`, [decision-models.md](../../library/architecture/decision-models.md#in-this-repo)).
At the user's direction Jev is called directly at TypeSafe with `TYPESAFE_API_KEY`, pinned to
`jev-1.13.0`, instead of through OpenRouter's System One API; the protocol, the answers, and the
price are the same, and OpenRouter stays the documented alternative. Nothing else in the
decision changes: where this ADR says OpenRouter and `OPENROUTER_API_KEY`, read TypeSafe and
`TYPESAFE_API_KEY`.

## Context

- **The repo already decides with models in many places:** RAG relevance and hallucination
  grading, the groundedness check, the memory guard, the consolidator's edit choices, and the
  coordinators' delegation. Every one of them runs on an LLM tier, and none has a labeled set.
- **Decision models answer typed questions** (`choice`, `score`, `noul`) with a probability per
  option, many questions per request. Measured here through OpenRouter (research's
  `EV-2026-09-27-jev-openrouter` and `EV-2026-09-27-jev-harness-decisions`):
  - 439-475 ms per decision end to end, against 1.3-2.3 s for our LLM tiers; six batched
    decisions in about 0.45 s; about $0.00002 per decision;
  - 22/23 on our grader and guard cases (`glm-5.3` 23/23), and none of 48 guard answers less
    strict than its label;
  - routing 32/32 in three runs, where two LLM tiers scored 30/32;
  - weaker where its own documentation says: implied conditions, off-distribution calibration;
    Finglish is barely measured.
- **The user's frame:** decision models and language models are the two wings of agentic
  systems. Using one should be as natural as calling a model, and decision engineering is a
  discipline the learner practices early.
- **Research's version 2 held a decider to a bar the LLM deciders in the code never met,** and
  placed its first code at R2 and tier routing at P9. Version 3 corrected both; the lead's
  dossier added the rest recorded below.

## Decision

1. **Two model families.** A language model writes; a decision model decides; code does what a
   parser, a lookup, arithmetic, or a rule settles. Every AI step is one of the three or a
   composition of them.
2. **One standard for every decision point, whatever its backend:**
   - a labeled set with a Finglish subset; accuracy per class, unsafe errors, latency, and cost;
   - the decider is the first candidate and the LLM its escalation; the LLM stays primary only
     where the measurement says so;
   - a step that writes goes to an LLM (a step that decides and explains is split), and a step
     code can decide goes to code.
3. **Gates escalate; they never approve,** for every model (ARCHITECTURE principle 4).
4. **The seam:** `decision_model` in `models/`, beside `llm_model`, arriving at R1 with its first
   consumer:
   - the pinned model ID (`typesafe/jev-1.13`) and base URL in `configs/models_config.py`, the key
     by variable name (`OPENROUTER_API_KEY`), and an explicit timeout;
   - one retry layer on the calling node, since the client has none; in a cascade a decider
     error takes the LLM path;
   - test mode keeps the backend; a test profile may route decisions to the LLM path; unit tests
     use a scripted fake;
   - a decision log: the state's hash, the question set's version, the served snapshot, the
     probabilities, the path taken, latency, and cost computed from input tokens;
   - the client is `langchain-typesafe` behind the seam, entered as a pre-release: it is the
     maintained LangChain client for the System One API. Exit: its first non-alpha release, or
     an in-house client over `/v1/systemone` if it is still alpha at P8-C3;
   - backends are configuration: Jev through OpenRouter's System One API now; a local server on
     the same protocol is the production path for private state. Hosted decisions follow the
     one data policy every hosted provider follows.
5. **Question sets are versioned artifacts** with their labeled sets, beside the prompts they
   parallel; thresholds live in `configs/`. No registry of decision points before E2's
   versioned registries (ADR-0006).
6. **The curriculum** (ROADMAP v4.2):
   - Phase 1 retrofits the decision points P1 to P5 already have, inside R1-R5's and the P5
     teaching pass's own hard concepts;
   - a new stage, **D1, decision engineering**, between R5 and P6: the decision workbench and
     its labs;
   - **tier selection** as three mechanisms (a measured catalog, per-request routing, verify then
     escalate): measured at R2, whose labeled set carries reference answers; built at D1; costed
     at P9-B2;
   - **schema determination** as three decisions (filling closed fields, choosing the contract,
     verifying fields an LLM filled); the field compiler arrives at its third consumer in the P5
     teaching pass.
7. **The development loop:** advisory hooks (document health, a done gate, shell edits and
   ownership, meaning-level conventions), built by the engineer (ADR-0022). Before a hook sends
   session content to a hosted decider, or before a replay reads past transcripts, the user
   gives an explicit yes.
8. **One meaning for "cascade":** escalation on uncertainty. `TIER_CASCADE_ORDER`, which falls
   down the tiers when providers fail, is renamed "fallback order" when the quality escalation
   lands.

## Consequences

- Every decision point, the LLM ones included, gets a labeled set and a measurement before any
  backend change, and the design card template gains point 17, decision points.
- A pre-release package enters the lock at R1, with its reason and exit recorded on the radar.
- Decision requests send state to OpenRouter and TypeSafe, as the LLM tiers already send it to
  their providers.
- The roadmap gains one stage (D1).
- Research's design guide splits: the binding rules move to
  [`library/architecture/decision-models.md`](../../library/architecture/decision-models.md),
  maintained by the lead; the facts and the evidence stay in research's landscape.

## Alternatives considered

- **Keep the LLM deciders and use a decision model only at P8-C3** (DEC-004, BR-001): rejected
  on evidence. It kept a double standard, and the measurements above answer the questions
  DEC-004 left open.
- **Research's version 2: no code before R2, tier routing at P9:** rejected on sequencing. The
  prerequisites exist at R1 and R2.
- **Replace every LLM decision without measuring:** rejected on evidence. Wording alone moved
  answers both ways on our cases, and thresholds need labels.
- **The experimental middlewares as they ship:** rejected as wrong at production scale.
  `AutoModeMiddleware` hard-codes a 0.5 threshold and blocks without asking a person;
  `ModelRouterMiddleware` has no confidence gate.
- **An in-house client now:** deferred. Built-ins come first (convention 9), and the seam keeps
  the swap cheap.
- **A foundation stage right after R0** (the lead's first leaning): rejected. Everyday calls fit
  inside R1-R4's own hard concepts, and D1's workbench is an observed abstraction only after
  those stages have measured about six decision points by hand.
