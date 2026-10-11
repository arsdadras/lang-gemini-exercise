# ADR-0006: Remove the agent registry until P6 needs one

- Status: Accepted
- Date: 2026-09-13

## Context

P4 Phase C added `AgentManifest`, a global mutable `AgentRegistry` singleton with
`importlib`-based discovery, and an `as_subagent` decorator. As of 2026-09-13:

- no code looks agents up through the registry;
- the manifests list tools that don't exist (`view_file`, `list_directory`);
- the decorator's re-export imported from the mentee's scratch folder.

## Decision

Remove all of it. Agents stay plain factories. A registry comes back as a typed capability
catalog once a coordinator actually selects specialists by their metadata. That is planned for
P6 Phase C, and the catalog will be designed against that consumer.

## Consequences

- Less indirection, and metadata can no longer drift out of sync with the real agents.
- P6 Phase C has a documented trigger and a concrete first consumer.

## Alternatives considered

- **Keep it for later:** rejected, because it was speculative and already drifting.
- **Keep only `AgentManifest`:** rejected, because a schema without a consumer has no pressure
  to stay correct.
