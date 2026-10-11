"""CLI for the P1 researcher: ``lab-research [session-mode] [--depth DEPTH] [--corpus FILE ...]``.

``--corpus`` gives the run its own files (``.txt`` or ``.md``) as the corpus source;
without it the corpus source is this project's own docs and code.
"""

import argparse

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agentlab.agents.researcher_agent import make_researcher_agent
from agentlab.configs.research_config import DEPTH_BUDGETS
from agentlab.retrieval.corpus_retrieval import check_corpus_files
from agentlab.schemas.input.research_input_schema import ResearchOptions
from agentlab.subagents.research_subagent import verify_research
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.run_with_hitl_util import run_with_hitl
from agentlab.utils.session_util import resolve_session


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """The session mode, research depth, and corpus files the run may search."""
    parser = argparse.ArgumentParser(prog="lab-research")
    parser.add_argument(
        "session", nargs="?", default=None, help="new, secret, resume, ..."
    )
    parser.add_argument(
        "--depth",
        choices=tuple(DEPTH_BUDGETS),
        default="standard",
        help="search/read/claim budget preset (default: standard)",
    )
    parser.add_argument(
        "--corpus",
        nargs="+",
        default=[],
        metavar="FILE",
        help="text or Markdown files to research as the corpus source",
    )
    return parser.parse_args(argv)


def main() -> None:
    """Research one topic, approving each outbound search, and print the checked report."""
    load_dotenv()
    configure_utf8_stdout()
    args = parse_args()
    try:
        check_corpus_files(args.corpus)
    except ValueError as error:
        print(f"Cannot use these files: {error}")
        return
    options = ResearchOptions(depth=args.depth, corpus_files=args.corpus)
    session = resolve_session(
        args.session,
        default_thread_id="research_session_001",
        agent_factory=lambda checkpointer: make_researcher_agent(
            checkpointer, options=options
        ),
        app_name="research",
        cli_command_hint="uv run lab-research step[<index>]",
    )
    if args.corpus:
        print(f"Corpus source: {', '.join(args.corpus)}")

    topic = input("Topic to research: ").strip()
    if not topic:
        print("No topic given.")
        return

    result = run_with_hitl(
        session.agent,
        {"messages": [HumanMessage(content=topic)]},
        session.config,
        assistant_prompt="Approve this search? [y/n]: ",
    )
    report = verify_research(result, options=options)
    print(report.model_dump_json(indent=2) if report else "No report was produced.")


if __name__ == "__main__":
    main()
