"""Wrapper to cache DB connection"""

import sqlite3
import streamlit as st
from frayerstore.db.connection import get_db_uncached
from frayerstore.core.config.settings import load_settings

settings = load_settings()


@st.cache_resource(ttl=settings.cache.db_connection_ttl)
def get_db() -> sqlite3.Connection:
    """Return a cached connection to the database"""
    conn = get_db_uncached()
    return conn
