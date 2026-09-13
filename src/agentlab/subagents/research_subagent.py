"""Researcher subagent spec: answers one narrow sub-question with cited findings."""

from deepagents import SubAgent

from agentlab.prompts.subagents_prompt import RESEARCHER_SUBAGENT_PROMPT
from agentlab.schemas.output.research_output_schema import ResearchFindings
from agentlab.tools.web_search_tool import make_web_search_tool

RESEARCHER_SUBAGENT_NAME = "researcher"


def make_researcher_subagent() -> SubAgent:
    """Build the researcher spec.

    DeepAgents compiles the spec into a child agent with its own context window,
    so each sub-question is researched without cluttering the parent's conversation.
    """
    return {
        "name": RESEARCHER_SUBAGENT_NAME,
        "description": (
            "Researches one specific sub-question using web_search and "
            "returns structured findings with sources. Delegate a single, "
            "narrow sub-question at a time, not the whole topic."
        ),
        "system_prompt": RESEARCHER_SUBAGENT_PROMPT,
        "tools": [make_web_search_tool()],
        "response_format": ResearchFindings,
    }
