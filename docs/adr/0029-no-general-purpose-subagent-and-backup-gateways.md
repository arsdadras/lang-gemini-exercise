# ADR-0029: No general-purpose subagent anywhere; every gateway model has a backup

- Status: Accepted
- Date: 2026-10-08
- Origin: the user (a mentor session), from an LLM's guidance on DeepAgents' harness profiles,
  verified against the installed `deepagents` source.

## Context

- DeepAgents adds a `general-purpose` subagent to every deep agent. It receives the parent's
  tools but none of its middleware, so through `task` it skips approval gates, tool budgets,
  security guards, and redaction, and its work never reaches the parent's messages. The
  research agent's claim check, the interpreter's HITL, and P5's memory gate all met it.
- `register_harness_profile(provider, HarnessProfile(general_purpose_subagent=
  GeneralPurposeSubagentProfile(enabled=False)))` turns it off; a provider-level profile merges
  with the provider's built-in one, and an agent with no named subagents then has no `task`.
- GapGPT, the gateway for every paid tier, was unreachable on 2026-10-07 and answered again on
  2026-10-08. Every model it serves is also on OpenRouter.

## Decision

1. **Every deep agent is built through `utils/deep_agent_util.create_deep_agent`,** which
   registers that profile for our providers once, on the first build.
2. **What stays:** P5's gate inside the memory storage (ADR-0010) keeps its place. The
   general-purpose subagent was one of its reasons; the others still hold: one enforcement point
   that can both ask and refuse, and every writer, the consolidator included, goes through the
   storage. The research agent stays a plain `create_agent`: it needs two tools, not a deep
   agent's file tools.
3. **Every GapGPT model has a backup** (`ModelSpec.backup`): the same model on OpenRouter, tried
   right after it, before the tier's next provider. Test mode is Gemini on Google's API, then
   Claude Haiku 5.5 (OpenRouter-only until GapGPT serves it). *Update 2026-10-08:* at the user's
   direction test mode calls Gemini through GapGPT first, then Google's API, then Haiku.
   *Update 2026-10-08 (later):* Haiku left the free tier; test mode is a ladder of tiers
   ([ADR-0031](0031-jev-model-router-and-test-mode-ladder.md)).
4. **Specialist subagents share one adapter,** `utils/subagent_util.specialist_subagent`: the
   code review, interpreter, and RAG factories each pass their `run_*` and keep their defaults
   (rule of three).

## Consequences

- A coordinator's only route to work is a named subagent behind its own boundary.
- A gateway outage costs one failed call per request. The OpenRouter key's credit (2026-10-08:
  too little for one 4096-token reservation) blocks the backups until it is topped up.

## Alternatives considered

- **A subagent named `general-purpose` of our own:** keeps `task` on agents that need none.
- **`excluded_tools={"task"}`:** hides the tool but keeps the middleware; the profile is simpler.
- **Interleaving gateways per tier** (all GapGPT models, then all OpenRouter): a gateway outage
  would fail every provider of the tier before the first backup.
