"""Graph assembly for P1's research: plan -> one research run per sub-question -> claim check.

```
START -> plan --fan_out--> research (x N, in parallel, via Send) -> check -> END
```

No node has a retry policy, by convention 11: ``plan`` and ``research`` call models (the SDKs
retry and the fallback switches providers), and ``check``'s decider failures already take the
LLM path inside the claim check (a cascade, ``decision-models.md``).
"""

from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agentlab.nodes.claim_check_node import Decide, make_check_node
from agentlab.nodes.research_node import (
    RESEARCH_NODE,
    fan_out,
    make_plan_node,
    make_research_node,
)
from agentlab.schemas.state.research_state import ResearchState


def build_research_graph(
    agent: Runnable,
    *,
    plan_chain: Runnable | None = None,
    decide: Decide | None = None,
    verdict_chain: Runnable | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph:
    """Compile the research graph around an injected P1 agent.

    Args:
        agent: The researcher agent (``make_web_researcher_agent``), built with the same options
            the graph is invoked with: the agent holds the per-run budgets.
        plan_chain: The planner's structured chain; defaults to the ``low`` tier.
        decide, verdict_chain: The claim check's decider and LLM escalation; default to the
            ``decision_model`` seam and the ``low`` tier.
        checkpointer: None keeps a run in memory only. Production path: a durable saver, so a
            run that fails after some sub-questions resumes from the last finished step
            instead of paying for every run again.
    """
    graph = StateGraph(ResearchState)
    graph.add_node("plan", make_plan_node(plan_chain))
    graph.add_node(RESEARCH_NODE, make_research_node(agent))
    graph.add_node("check", make_check_node(decide=decide, verdict_chain=verdict_chain))
    graph.add_edge(START, "plan")
    graph.add_conditional_edges("plan", fan_out, [RESEARCH_NODE])
    graph.add_edge(RESEARCH_NODE, "check")
    graph.add_edge("check", END)
    return graph.compile(checkpointer=checkpointer)
