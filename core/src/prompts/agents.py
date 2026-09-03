"""Research agent system prompt, built on the shared prompt template."""

from prompts.template.builder import build_system_prompt


def build_web_researcher_prompt() -> str:
    """Build the P1 web-researcher agent's system prompt."""
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


def build_repo_insight_prompt() -> str:
    """Build the P2 repo-insight coordinator agent's system prompt."""
    return build_system_prompt(
        assistant_name="Coordinator",
        role="a coordinator that delegates to specialized subagents",
        domain="this codebase and its indexed document corpus",
        mission="Answer questions about the project by delegating to the right subagent.",
        tools=(
            "Use rag_subagent (via the task tool) for ANY question about content in the "
            "indexed document corpus (code, docs, notes about this project). Do not use "
            "filesystem tools (glob/ls/grep) to answer such questions — always delegate first."
        ),
        output_format="Return the subagent's answer directly.",
        constraints="- Always delegate corpus-content questions to rag_subagent first.",
    )
