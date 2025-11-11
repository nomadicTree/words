from typing import List
import streamlit as st
from .db import get_db  # assuming this still provides a sqlite3.Row connection


def search_words(query: str) -> List[dict]:
    """Search the database for words matching the query."""
    query = query.strip()
    db = get_db()
    q = """
        SELECT w.id, w.word, s.name AS subject_name
        FROM Words w
        JOIN Subjects s ON s.id = w.subject_id
        WHERE w.word LIKE ?
        ORDER BY w.word
    """
    rows = db.execute(q, (f"%{query}%",)).fetchall()
    return [dict(r) for r in rows]


def get_subject_name(subject_id: int) -> str | None:
    """Return the name of a subject given its ID."""
    db = get_db()
    q = "SELECT name FROM Subjects WHERE id = ?"
    row = db.execute(q, (subject_id,)).fetchone()
    return row["name"] if row else None


def get_topics_for_word(word_id: int) -> List[dict]:
    """Return all topics associated with any version of a given word."""
    db = get_db()
    q = """
        SELECT
            t.code,
            t.name AS topic_name,
            c.name AS course_name,
            s.name AS subject_name,
            t.code || ': ' || t.name AS topic_label
        FROM Words w
        JOIN WordVersions v ON v.word_id = w.id
        JOIN WordVersionContexts x ON x.word_version_id = v.id
        JOIN Topics t ON x.topic_id = t.id
        JOIN Courses c ON t.course_id = c.id
        JOIN Subjects s ON c.subject_id = s.id
        WHERE w.id = ?
        ORDER BY c.name, t.code
    """
    rows = db.execute(q, (word_id,)).fetchall()
    return [dict(r) for r in rows]


@st.cache_data
def get_all_subjects_courses_topics() -> List[dict]:
    """Return all subjects, courses, and topics."""
    db = get_db()
    q = """
        SELECT
            s.name AS subject,
            c.name AS course,
            t.id AS topic_id,
            t.code,
            t.name AS topic_name,
            t.code || ': ' || t.name AS topic_label
        FROM Subjects s
        JOIN Courses c ON s.id = c.subject_id
        JOIN Topics t ON c.id = t.course_id
        ORDER BY s.name, c.name, t.code
    """
    rows = db.execute(q).fetchall()
    return [dict(r) for r in rows]


def get_words_by_topic(topic_id: int) -> List[dict]:
    """Return all words associated with a given topic."""
    db = get_db()
    q = """
        SELECT DISTINCT w.id, w.word, s.name AS subject_name
        FROM Words w
        JOIN WordVersions v ON v.word_id = w.id
        JOIN WordVersionContexts x ON x.word_version_id = v.id
        JOIN Topics t ON x.topic_id = t.id
        JOIN Courses c ON t.course_id = c.id
        JOIN Subjects s ON c.subject_id = s.id
        WHERE t.id = ?
        ORDER BY w.word
    """
    rows = db.execute(q, (topic_id,)).fetchall()
    return [dict(r) for r in rows]


def get_word_by_id(word_id: int) -> dict | None:
    """Return a word given its ID."""
    try:
        word_id = int(word_id)
    except (TypeError, ValueError):
        return None

    db = get_db()
    q = """
        SELECT w.*, s.name AS subject_name
        FROM Words w
        JOIN Subjects s ON s.id = w.subject_id
        WHERE w.id = ?
    """
    row = db.execute(q, (word_id,)).fetchone()
    return dict(row) if row else None


def get_related_words(word_id: int) -> List[dict] | None:
    """Return all related words for a given word_id."""
    db = get_db()
    q = """
        SELECT w2.id, w2.word
        FROM WordRelationships r
        JOIN Words w1 ON r.word_id1 = w1.id
        JOIN Words w2 ON r.word_id2 = w2.id
        WHERE r.word_id1 = ?
        UNION
        SELECT w1.id, w1.word
        FROM WordRelationships r
        JOIN Words w1 ON r.word_id1 = w1.id
        JOIN Words w2 ON r.word_id2 = w2.id
        WHERE r.word_id2 = ?
    """
    rows = db.execute(q, (word_id, word_id)).fetchall()
    return [dict(r) for r in rows]
