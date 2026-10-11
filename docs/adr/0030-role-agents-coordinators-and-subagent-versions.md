# ADR-0030: Role agents, coordinators, and a subagent version of every role agent

- Status: Accepted
- Date: 2026-10-08
- Origin: the user (a mentor session), after reading the code: the P2 "repo-insight
  coordinator" only relays questions to the RAG graph, and nothing in the repo says what an
  agent, a coordinator, or a subagent is for.

## Context

- P1, P4, and P5 each have a role agent with its own harness (tools, backend, middleware,
  approvals). P2 and P3 have only a graph, plus its `CompiledSubAgent` adapter, so their
  subagent version stands in for a role agent that was never designed.
- `repo_insight_agent` is a deep agent whose prompt says "delegate to the right subagent" and
  "return the subagent's answer directly": a full harness spent on passing a string to RAG.
- `coding_coordinator_agent` is a real coordinator: it plans and composes the P1, P3, and P4
  role agents toward one goal.
- An earlier proposal in the same session (a coordinator as a LangGraph graph, `subagents/`
  removed) was withdrawn: it rebuilt by hand the harness DeepAgents gives, and it dropped the
  subagent versions other projects reuse.

## Decision

1. **Three kinds, one place each.**
   - **Role agent** (`agents/`): one job and its own harness. It may delegate, but only for an
     internal need of that job.
   - **Subagent version** (`subagents/`): every role agent worth reusing ships one
     (`make_<role>_subagent`), so a coordinator, or a role agent that grows an internal need,
     can call it in its own place. A graph-backed role can also be offered as a tool.
   - **Coordinator** (`agents/coordinators/`): built with `create_deep_agent`, it has no narrow
     task of its own. It orchestrates role agents through their subagent versions toward a
     composite goal the roadmap names, and it grows the large harness: many subagents and
     tools, memory, long-lived skills.
2. **The framework follows the work, not the label.** LangGraph builds what needs explicit
   control: staged pipelines with many small model calls (P3's review, P2's RAG engine, P1's
   research graph). `create_agent` and `create_deep_agent` build what needs a harness. They mix
   where a reason is named: an agent as a node or subgraph inside a graph, a graph as a tool or
   subagent of an agent, or one part of a deep agent's harness rewritten in LangGraph. A
   deterministic workflow graph over specialists (P7 A1) is a workflow, not a coordinator; P7 C1
   measures the two against each other.
3. **P2's role is the RAG agent;** the RAG graph is its engine. It grows on two axes: the engine
   (R2 retrieval and reranking, P8 C2 knowledge compilation) and the harness (P8 A2, a RAG role
   agent that also works on its own). Its subagent and tool versions serve other agents.
4. **`repo_insight` stays a coordinator** and moves to `agents/coordinators/` unchanged. It
   becomes a real codebase orchestrator later (BACKLOG, with its trigger); until then its relay
   prompt is known debt.
5. **The `researcher` subagent becomes P1's subagent version over `run_research`** (BACKLOG,
   R1), so callers get the planned, claim-checked pipeline instead of a bare prompt with tools.

## Consequences

- `coding_coordinator_agent.py` and `repo_insight_agent.py` live in `agents/coordinators/`;
  `agents/__init__.py` exports role agents only.
- A new agent first names its kind. A coordinator without a composite goal, or a role agent
  that only relays to another, is rejected in review.
- P3 gets a role agent only when a stage gives it an open-ended job a graph doesn't cover.
