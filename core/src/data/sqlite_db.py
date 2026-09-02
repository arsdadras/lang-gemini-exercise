import sqlite3
from pathlib import Path

from langgraph.checkpoint.sqlite import SqliteSaver

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / "dbs" / "checkpoints.db"

def get_sqlite_checkpointer() -> SqliteSaver:
    """makes a connection and return a SqliteSaver instance."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    return SqliteSaver(conn)