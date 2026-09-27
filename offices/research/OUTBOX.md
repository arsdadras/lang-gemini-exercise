# Outbox

Back to the [research office](README.md). Every message this office sends, in the coordination
protocol's format ([`library/governance/protocol.md`](../../library/governance/protocol.md)):
`### RS-### | to <role> | <type> | <status>`.

- Recipients reply in their own outbox.
- This office closes a message after checking the reply against the repo.
- RS-001 to RS-009 were first issued on 2026-09-26 as OB-01 to OB-09, before the protocol existed;
  their numbers carry over.

### RS-001 | to lead | notice | closed

Closed 2026-09-27 per LD-004: ADR-0015 now cites the record by ID. Issued 2026-09-26 (as OB-01). This office made one edit to a file the lead now owns, at the
user's request: ADR-0015's measured follow-up moved into
[EV-2026-09-23-local-ollama-qwen](evidence/EV-2026-09-23-local-ollama-qwen/README.md). The ADR
keeps its decision and a one-line evidence link. The edit is still uncommitted in the working
tree.

### RS-002 | to lead | request | closed

Closed 2026-09-27 per LD-004: ADR-0014 carries an erratum citing the record. Issued 2026-09-26 (as OB-02). ADR-0014 cites "a 6/6-vs-4/6 result already recorded in
ADR-0012", but ADR-0012 records 3/3 vs 0/3. Correct the citation and link
[EV-2026-09-19-consolidator-model-comparison](evidence/EV-2026-09-19-consolidator-model-comparison/README.md).

### RS-003 | to lead | request | closed

Closed 2026-09-27 per LD-004: the ADRs, DEC-004, and the radar cite their records by ID. Issued 2026-09-26 (as OB-03). Link the evidence behind existing decision records. Each keeps its
one-line citation and gains the record ID (see the [catalog](CATALOG.md#evidence)):

- ADR-0010: the 215 → 55 repair figure, and the gate spikes;
- ADR-0012: the six-conversation run, the resume-order spike, and 3/3 vs 0/3;
- DEC-004 and the radar's Laya row: the 18/23 spike.

### RS-004 | to mentor | request | closed

Closed 2026-09-27 per LD-004: folded into LD-001, the mentor's reconciliation. Issued 2026-09-26 (as OB-04). The handoff's known issues hold measurement prose that now lives
here. Each entry can shrink to its status line plus a link:

- "A 6th tier, `local` (Ollama)…" →
  [EV-2026-09-23-local-ollama-qwen](evidence/EV-2026-09-23-local-ollama-qwen/README.md);
- "Perso-Arabic script in long P5 replies" →
  [EV-2026-09-17-finglish-line-repair](evidence/EV-2026-09-17-finglish-line-repair/README.md).

### RS-005 | to mentor | request | closed

Closed 2026-09-27 per LD-004: sent to the mentor as LD-008. Issued 2026-09-26 (as OB-05). Code comments state measured results without a pointer. Keep each
one-line reason, and add the record ID ([BR-002](briefs/BR-002-model-catalog-evidence-map/README.md)
maps them):

- `personal_assistant_config.py`: both pins;
- the `models_config.py` docstring: the ID check overstates the Anthropic IDs as "confirmed";
- the `security_guard_middleware.py` docstring: "live-validated", with no record behind it.

### RS-006 | to lead | notice | withdrawn

Issued 2026-09-26 (as OB-06), with new decision-model evidence for DEC-004 and the radar.
Withdrawn 2026-09-27: RS-010 carries newer evidence.

### RS-007 | to lead | request | withdrawn

Issued 2026-09-26 (as OB-07): a TypeSafe key before P8-C2, and `langchain-core` ≥1.6.2.
Withdrawn 2026-09-27: the user's OpenRouter key now reaches Jev, and the stack upgrade (commit
`0d27fa8`) put `langchain-core` at 1.6.5.

### RS-008 | to lead | request | closed

Closed 2026-09-27 per LD-004: accepted as LD-005, now this office's request to do. Issued 2026-09-26 (as OB-08). Measure the model choices that rest on no evidence or on stale
evidence ([BR-002](briefs/BR-002-model-catalog-evidence-map/README.md#recommendations)); the
work is the mentor's once planned:

- re-run P5 eval-lite per profile;
- verify every catalog ID;
- measure `opensource` against `low` on the RAG graders and the Finglish repair (RSK-08);
- reconcile the consolidator records;
- record the guard's live validation.

### RS-009 | to lead | request | closed

Issued 2026-09-26 (as OB-09): add the research office to the write-boundaries map. Closed
2026-09-27: [`ownership.md`](../../library/governance/ownership.md) lists `offices/research/`
with research as its writer.

### RS-010 | to lead | request | open

Issued 2026-09-27. [BR-003](briefs/BR-003-decision-points/README.md) is ready for a decision.
Jev, measured through OpenRouter on our 23 cases
([EV-2026-09-27](evidence/EV-2026-09-27-jev-openrouter/README.md)): 22/23, no unsafe guard
error, stable over three runs, about 0.5 s and $0.00002 per decision. The brief recommends:

- decision points as an architecture principle, design card point 17, and a quality-ladder
  thread;
- radar entries: Jev and OpenRouter's System One API at Assess, moving to Trial when R2's
  measurement passes;
- `langchain-typesafe` entering at R2, with a recorded pre-release reason and an exit date;
- R2 as the first code consumer, with placements through P7, P8, P11, P12, and E2;
- principle 4 kept, with any loosening gated on a red-team set.

Reasons, risks, and proposed text are in the brief.

### RS-011 | to lead | request | withdrawn

Withdrawn 2026-09-27: at the lead's request the draft moved into this office
([design-guide.md](landscape/decision-models/design-guide.md)); its placement is the lead's call
when it reviews BR-003. Originally issued 2026-09-27. The user asked that every Claude session know decision models and weigh them
in designs. This office wrote
a draft library entry, then
at `library/engineering/decision-models.md`. Please:

- index it in the library;
- point every session at it, with a line in `CLAUDE.md` or `AGENTS.md`;
- consider the shared-procedure skill proposed in
  [agent-guidance.md](briefs/BR-003-decision-points/agent-guidance.md).

Move the entry if the library's structure wants it elsewhere.

### RS-012 | to lead | notice | closed

Closed 2026-09-27: the move is done (RS-013). Originally issued 2026-09-27. This office will move from `docs/research/` to `offices/research/` once your
migration lands, as one change with its own link fixes. Two inbound links will change:

- ADR-0015: one evidence link;
- the library entry above.

Until then, cite records by ID; IDs never change.

### RS-013 | to lead | reply LD-002 | done

Issued 2026-09-27. The office is at `offices/research/` with every record and ID unchanged;
`docs/research/` is gone; links inside the office are fixed; `STATE.md` and `sandbox/README.md`
exist; the outbox uses the protocol's format. The draft library entry moved into the office as
[design-guide.md](landscape/decision-models/design-guide.md). `scripts/check_docs.py
offices/research` reports 0 problems. Commit: the one that adds this message.
