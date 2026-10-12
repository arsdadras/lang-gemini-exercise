"""Mini-workflow P5 + P1, a personalized research brief: ``lab-brief [user_id]``.

P1 researches the topic; P5 supplies the user's stored context through a read-only tool, so the
brief fits their constraints and goals. Personal data in that context (emails, card numbers,
IPs) is redacted before the research model sees it, so it can't leak into web searches.
Defaults to the P5 app's last active user.
"""

import sys

from dotenv import load_dotenv

from agentlab.configs.personal_assistant_config import ASSISTANT_STORE_DB_PATH
from agentlab.data.sqlite_db_data import get_sqlite_store
from agentlab.utils.console_util import configure_utf8_stdout
from agentlab.utils.memory_session_util import load_session
from agentlab.workflows.personal_brief_workflow import run_personal_brief


def main() -> None:
    """Research one topic for the user, tailored to their P5 memory."""
    load_dotenv()
    configure_utf8_stdout()
    store = get_sqlite_store(ASSISTANT_STORE_DB_PATH)
    user_id = sys.argv[1] if len(sys.argv) > 1 else load_session(store)[0]

    topic = input(f"[{user_id}] Topic to research: ").strip()
    if not topic:
        print("No topic given.")
        return
    report = run_personal_brief(store, user_id, topic)
    print(report.model_dump_json(indent=2) if report else "No report was produced.")


if __name__ == "__main__":
    main()
