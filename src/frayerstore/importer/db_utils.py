from __future__ import annotations
import sqlite3
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import ImportSubject


def get_subject_by_name(conn: sqlite3.Connection, name: str) -> sqlite3.Row | None:
    """Return row of matching subject name"""
    query = """
    SELECT * FROM Subjects WHERE name = ?
    """
    row = conn.execute(query, (name,)).fetchone()
    if row:
        return row
    else:
        return None


def get_subject_by_slug(conn: sqlite3.Connection, slug: str) -> sqlite3.Row | None:
    """Return row of matching subject slug"""
    query = """
    SELECT * FROM Subjects WHERE slug = ?
    """
    row = conn.execute(query, (slug,)).fetchone()
    if row:
        return row
    else:
        return None


def insert_subject(conn: sqlite3.Connection, incoming: ImportSubject) -> int:
    query = """
    INSERT INTO Subjects (name, slug)
    VALUES (?, ?)
    """
    cur = conn.execute(
        query,
        (
            incoming.name,
            incoming.slug,
        ),
    )
    return cur.lastrowid
