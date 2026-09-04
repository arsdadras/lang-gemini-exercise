import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

DB_DIR = Path(__file__).resolve().parent / "dbs"
DB_PATH = DB_DIR / "checkpoints.db"


def get_sqlite_checkpointer() -> SqliteSaver:
    """makes a connection and return a SqliteSaver instance."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    return SqliteSaver(conn)


def get_recent_threads(limit: int | None = None) -> list[str]:
    """Return distinct thread IDs from checkpoints.db, ordered by latest checkpoint descending."""
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    query = (
        "SELECT thread_id, MAX(checkpoint_id) as latest "
        "FROM checkpoints GROUP BY thread_id ORDER BY latest DESC"
    )
    if limit is not None:
        query += f" LIMIT {limit}"
    rows = conn.execute(query).fetchall()
    conn.close()
    return [r[0] for r in rows]
