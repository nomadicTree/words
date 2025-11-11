import os
import sqlite3
import streamlit as st

# Resolve path to app/db/Words.db
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "db",
    "Words.db",
)


@st.cache_resource
def get_db() -> sqlite3.Connection:
    """Open a cached connection to the database

    Returns:
        A connection object to the application's SQLite database.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
