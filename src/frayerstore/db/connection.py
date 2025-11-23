import sqlite3
from pathlib import Path
from frayerstore.core.config.paths import DB_PATH

def open_db_at(db_path: str | Path) -> sqlite3.Connection:
    path = Path(db_path)

    # Ensure parent folder exists (optional safety)
    path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(
        path,
        detect_types=sqlite3.PARSE_DECLTYPES,
        check_same_thread=False,       # required for Streamlit threads
    )

    # Dict-like rows: row["column"]
    conn.row_factory = sqlite3.Row

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # WAL mode = faster reads + safe for multiple Streamlit reruns
    conn.execute("PRAGMA journal_mode = WAL;")

    # Slightly faster synchronous mode
    conn.execute("PRAGMA synchronous = NORMAL;")

    return conn

def get_db_uncached():
    return open_db_at(DB_PATH)