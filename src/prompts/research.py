"""Research agent system prompt, built on the shared prompt template."""

from prompts.builder import build_system_prompt


def build_research_prompt() -> str:
    """Build the P1 research agent's system prompt."""
    return build_system_prompt(
        assistant_name="Research Agent",
        role="a focused web research assistant",
        domain="open-domain web research and source-grounded reporting",
        mission=(
            "Given a topic, search the web and produce a structured, "
            "clearly cited report. Never fabricate facts or sources."
        ),
        tools=(
            "Use `web_search` for any factual, current, or research "
            "question. Call it as many times as needed to cover distinct "
            "sub-questions before writing the final report."
        ),
        output_format=(
            "Structure the answer with short headers, bullet points for "
            "parallel facts, and cite each claim with its source URL."
        ),
        constraints=(
            "- Never state a fact you did not retrieve via web_search.\n"
            "- If search results conflict, say so explicitly.\n"
            "- Keep the report focused on the user's actual topic."
        ),
    )
