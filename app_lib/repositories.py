"""Database queries"""

from typing import List
import streamlit as st
from app_lib.db import get_db


def search_words(query: str) -> List[dict]:
    """Search the database for words matching the query.

    Args:
        query: The search text.

    Returns:
        A list of dictionaries, each representing a matching word row.
        Keys correspond to column names in the Word table.
    """
    query = query.strip()
    db = get_db()
    q = "SELECT * FROM Word WHERE word LIKE ? ORDER BY Word.word"
    rows = db.execute(q, (f"%{query}%",)).fetchall()
    return [dict(r) for r in rows]


def get_subject_name(subject_id: int) -> str | None:
    """Return the name of a subject given its ID.

    Args:
        subject_id: The subject ID.

    Returns:
        The subject name as a string, or None if no such subject exists.
    """
    db = get_db()
    q = "SELECT name FROM Subject WHERE id = ?"
    row = db.execute(q, (subject_id,)).fetchone()
    return row["name"] if row else None


def get_topics_for_word(word_id: int) -> List[dict]:
    """Return all topics associated with a given word.

    Args:
        word_id: The word ID.

    Returns:
        A list of dictionaries, each containing:
            - code
            - topic_name
            - course_name
            - subject_name
            - topic_label
        Ordered by course name and topic code.
    """
    db = get_db()
    q = """
    SELECT
        Topic.code,
        Topic.name AS topic_name,
        Course.name AS course_name,
        Subject.name AS subject_name,
        Topic.code || ': ' || Topic.name AS topic_label
    FROM Topic
    JOIN WordTopic ON Topic.id = WordTopic.topic_id
    JOIN Course ON Topic.course_id = Course.id
    JOIN Subject ON Course.subject_id = Subject.id
    WHERE WordTopic.word_id = ?
    ORDER BY Course.name, Topic.code
    """
    rows = db.execute(q, (word_id,)).fetchall()
    return [dict(r) for r in rows]


@st.cache_data
def get_all_subjects_courses_topics() -> List[dict]:
    """Return all subjects, courses, and topics.

    Returns:
        A list of dictionaries, each containing:
            - subject
            - course
            - topic_id
            - code
            - topic_name
            - topic_label
        Results are ordered by subject, course, and topic code.
    """
    db = get_db()
    q = """
    SELECT
        Subject.name as subject,
        Course.name as course,
        Topic.id as topic_id,
        Topic.code,
        Topic.name as topic_name,
        Topic.code || ': ' || Topic.name AS topic_label
    FROM Subject
    JOIN Course ON Subject.id = Course.subject_id
    JOIN Topic ON Course.id = Topic.course_id
    ORDER BY Subject.name, Course.name, Topic.code
    """
    rows = db.execute(q).fetchall()
    return [dict(r) for r in rows]


def get_words_by_topic(topic_id: int) -> List[dict]:
    """Return all words associated with a given topic.

    Args:
        topic_id: The topic ID.

    Returns:
        A list of dictionaries representing word rows.
    """
    db = get_db()
    q = """
        SELECT Word.*
        FROM Word
        JOIN WordTopic ON Word.id = WordTopic.word_id
        WHERE WordTopic.topic_id = ?
    """
    rows = db.execute(q, (topic_id,)).fetchall()
    return [dict(r) for r in rows]


def get_word_by_id(word_id: int) -> dict | None:
    """Return a word given its ID.

    Args:
        word_id: The word ID.

    Returns:
        A dictionary representing the word row, or None if not found.
    """
    try:
        word_id = int(word_id)
    except (TypeError, ValueError):
        return None

    db = get_db()
    q = "SELECT * FROM Word WHERE id = ?"
    row = db.execute(q, (word_id,)).fetchone()
    return dict(row) if row else None
