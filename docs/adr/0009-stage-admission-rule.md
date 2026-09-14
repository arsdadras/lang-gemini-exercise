# ADR-0009: A stage admission rule, and the curriculum refined by it

- Status: Accepted
- Date: 2026-09-14

## Context

- **Coverage drifted into a tour.** Asked about new DeepAgents features, the mentor audited
  the roadmap against the LangChain, LangGraph, DeepAgents, and LangSmith docs and placed
  every uncovered feature somewhere. The mentee flagged the risk: additions chosen for
  coverage bloat stages, break the flow, and serve the syllabus instead of the project.
- **The review confirmed it.** Several placements had no real consumer: harness profiles
  and programmatic tool calling in P9 (the P4 sandbox already does that analysis), the
  Functional API and emulated tools in P11 (graph nodes already keep finished side effects
  from re-running), A2A, and data export in P5. P6-C and P12 carried lessons that belong
  elsewhere.
- **P10 added little architecture.** Multimodal perception already built on P7's pipeline;
  what it added was mostly model input handling.
- **The pace estimate was wrong.** "1-2 weeks per project" doesn't match P5, which needs
  about nine stages.

## Decision

- **Stage admission rule** (in `docs/ROADMAP.md`): an item enters a stage only when the
  project needs it now, it teaches something new, and it fits a stage built around one
  central lesson. Items that fail go to the handoff backlog with a trigger.
- **P10 folded into P7:** vision over scanned pages and images is P7-B; temporal media is out
  of scope. Project numbers stay stable.
- **Moves:**
  - MCP: P5-C4 -> P11-A, the integration project.
  - Typed capability catalog: P6-C -> P12-C. P6 composes two or three specialists; P12
    routes across seven.
  - Agent Server and async subagents: P6-C -> P12-B, where long tasks need check and cancel.
- **Removed:** the placements listed under Context, plus workflow variants and multi-user
  isolation in P12-C (isolation is already covered by P5 and P11).
- **Stages are phrased as lessons.** API names appear only where the API is the decision.
- **Term E:** the shared runtime, platform, and portfolio stages merge into one stage proven
  by three workflows, since the platform is only credible once real workflows run on it.
- **Pacing** is counted in stages, not weeks.

## Consequences

- Term P is one project and several items shorter, and each stage has a named central
  lesson.
- Project numbering has a gap at P10.
- The assistant gets no external data source (MCP) until P11.
- Some framework features have no planned stage and are learned only if their trigger fires.

## Alternatives considered

- **Renumber after folding P10:** rejected; accepted ADRs and history refer to P11 and P12.
- **Keep P10 as a project:** rejected; too little new architecture for a full project.
- **Plan a stage for every framework feature:** rejected; that is a tour, not practice.
- **Keep MCP in P5:** rejected; P11 is the integration project, and P5 already has four C
  stages.
