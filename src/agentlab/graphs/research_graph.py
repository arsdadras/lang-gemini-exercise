"""Graph assembly for P1's research: plan -> route -> one research run per sub-question -> check -> pack_result.

```
START -> plan -> route --fan_out--> research (x N, in parallel, via Send) -> check -> pack_result -> END
```

No node has a retry policy, by convention 11: ``plan`` and ``research`` call models (the SDKs
retry and the fallback switches providers); a decider failure in ``route`` keeps every source,
and one in ``check`` takes the LLM path inside the claim check (a cascade, ``decision-models.md``),
so neither node fails on its decider.
"""

from typing import Any, NewType

from langchain_core.runnables import Runnable
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

ResearchGraph = NewType("ResearchGraph", CompiledStateGraph)

from agentlab.agents.researcher_agent import ResearcherAgent, make_researcher_agent
from agentlab.nodes.claim_check_node import Decide, make_check_node
from agentlab.nodes.research_node import (
    RESEARCH_NODE,
    fan_out,
    make_plan_node,
    make_research_node,
)
from agentlab.nodes.source_route_node import make_route_node
from agentlab.schemas.input.research_input_schema import ResearchInput, ResearchOptions
from agentlab.schemas.output.research_output_schema import (
    ClaimVerdict,
    ResearchPlan,
    ResearchReport,
)
from agentlab.schemas.state.research_state import ResearchState
from agentlab.workflows.specialist_workflow import ResultNode, SpecialistSpec

DEFAULT_RESEARCH_DESCRIPTION = (
    "Plans, routes across web/academic/corpus sources, researches sub-questions in "
    "parallel, and verifies every claim against the source documents read."
)

RESEARCH_SPEC = SpecialistSpec[ResearchInput, ResearchReport](
    name="research",
    description=DEFAULT_RESEARCH_DESCRIPTION,
    input_schema=ResearchInput,
    report_schema=ResearchReport,
)


def build_research_graph(
    agent: ResearcherAgent | CompiledStateGraph | Any,
    *,
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
    decide: Decide | None = None,
    verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
    route_decide: Decide | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> ResearchGraph:
    """Compile the research graph around an injected P1 agent, ending in ``pack_result``."""
    graph = StateGraph(ResearchState)
    graph.add_node("plan", make_plan_node(plan_chain))
    graph.add_node("route", make_route_node(route_decide))
    graph.add_node(RESEARCH_NODE, make_research_node(agent))
    graph.add_node("check", make_check_node(decide=decide, verdict_chain=verdict_chain))
    graph.add_node("pack_result", ResultNode(RESEARCH_SPEC))
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "route")
    graph.add_conditional_edges("route", fan_out, [RESEARCH_NODE])
    graph.add_edge(RESEARCH_NODE, "check")
    graph.add_edge("check", "pack_result")
    graph.add_edge("pack_result", END)
    compiled = graph.compile(checkpointer=checkpointer)
    return ResearchGraph(compiled)


def make_research_graph(
    agent: ResearcherAgent | CompiledStateGraph | Any = None,
    *,
    options: ResearchOptions | None = None,
    plan_chain: Runnable[Any, ResearchPlan] | None = None,
    route_decide: Decide | None = None,
    decide: Decide | None = None,
    verdict_chain: Runnable[Any, ClaimVerdict] | None = None,
    checkpointer: BaseCheckpointSaver | None = None,
) -> ResearchGraph:
    """Compile the research graph around an injected or default researcher agent."""
    resolved_agent = (
        agent if agent is not None else make_researcher_agent(options=options)
    )
    return build_research_graph(
        resolved_agent,
        plan_chain=plan_chain,
        route_decide=route_decide,
        decide=decide,
        verdict_chain=verdict_chain,
        checkpointer=checkpointer,
    )
