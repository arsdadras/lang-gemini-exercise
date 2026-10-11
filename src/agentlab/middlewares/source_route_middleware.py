"""Source routing for the P1 researcher: a run sees only the tools of the sources routed to it.

The research graph's router (``research_sources@2``) picks the sources one sub-question needs
and passes them in the run's input as ``sources``. This middleware enforces the pick in code, at
both ends: the model is offered only the routed sources' tools, and a call to any other source's
tool (a name the model remembered or invented) is refused. Tools that belong to no source, such
as a composing caller's ``get_user_context``, are always kept. Without ``sources`` in the input
(the CLI's single run) every tool stays.
"""

from collections.abc import Callable, Mapping, Sequence
from typing import Any, NotRequired

from langchain.agents.middleware import AgentMiddleware, AgentState, ModelRequest
from langchain_core.messages import ToolMessage
from langgraph.prebuilt.tool_node import ToolCallRequest
from langgraph.types import Command

from agentlab.configs.research_config import SOURCE_TOOLS


class SourceRouteState(AgentState):
    """The agent's state plus the sources routed to this run."""

    sources: NotRequired[list[str]]


def _tool_name(tool: Any) -> str:
    return tool.name if hasattr(tool, "name") else str(tool.get("name", ""))


class SourceRouteMiddleware(AgentMiddleware[SourceRouteState]):
    """Offer and run only the routed sources' tools."""

    state_schema = SourceRouteState

    def __init__(
        self, source_tools: Mapping[str, Sequence[str]] = SOURCE_TOOLS
    ) -> None:
        super().__init__()
        self._source_tools = {name: set(tools) for name, tools in source_tools.items()}
        self._all_source_tools = set().union(*self._source_tools.values())

    def _blocked(self, state: Mapping[str, Any]) -> set[str]:
        """Tool names outside the routed sources; none when the run has no route."""
        routed = state.get("sources")
        if routed is None:
            return set()
        allowed = set().union(*(self._source_tools.get(name, set()) for name in routed))
        return self._all_source_tools - allowed

    def wrap_model_call(self, request: ModelRequest, handler: Callable) -> Any:
        blocked = self._blocked(request.state)
        if not blocked:
            return handler(request)
        tools = [tool for tool in request.tools if _tool_name(tool) not in blocked]
        return handler(request.override(tools=tools))

    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command[Any]],
    ) -> ToolMessage | Command[Any]:
        name = request.tool_call["name"]
        if name in self._blocked(request.state or {}):
            return ToolMessage(
                content=f"{name} is not one of the sources for this question.",
                tool_call_id=request.tool_call["id"],
                name=name,
                status="error",
            )
        return handler(request)
