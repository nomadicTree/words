from typing import List

import streamlit as st

from app.core.db import get_db
from app.core.models.word_models import Word
from app.core.respositories.words_repo import get_word_full


@st.cache_data
def get_all_subjects_courses_topics() -> List[dict]:
    """Return all subjects, courses, and topics for selection widgets."""
    db = get_db()
    q = """
        SELECT
            s.id AS subject_id,
            s.name AS subject_name,
            c.id AS course_id,
            c.name AS course_name,
            c.level_id AS level_id,
            l.name AS level_name,
            l.description AS level_description,
            t.id AS topic_id,
            t.code AS topic_code,
            t.name AS topic_name
        FROM Subjects s
        JOIN Courses c ON c.subject_id = s.id
        LEFT JOIN Levels l ON l.id = c.level_id
        JOIN Topics t ON t.course_id = c.id
        ORDER BY s.name, c.name, t.code
    """
    rows = db.execute(q).fetchall()

    return [
        {
            "subject": row["subject_name"],
            "subject_id": row["subject_id"],
            "course": row["course_name"],
            "course_id": row["course_id"],
            "level_id": row["level_id"],
            "level_name": row["level_name"],
            "level_description": row["level_description"],
            "topic_id": row["topic_id"],
            "code": row["topic_code"],
            "topic_name": row["topic_name"],
            "topic_label": f"{row['topic_code']}: {row['topic_name']}",
        }
        for row in rows
    ]


def get_words_for_topic(topic_id: int) -> List[Word]:
    """Return Word objects filtered to versions linked to the given topic."""
    db = get_db()
    q = """
        SELECT DISTINCT w.id AS word_id, w.word AS word_name
        FROM WordVersionContexts wvc
        JOIN WordVersions wv ON wv.id = wvc.word_version_id
        JOIN Words w ON w.id = wv.word_id
        WHERE wvc.topic_id = ?
        ORDER BY w.word COLLATE NOCASE
    """
    rows = db.execute(q, (topic_id,)).fetchall()

    words: List[Word] = []
    for row in rows:
        word = get_word_full(row["word_id"])
        if not word:
            continue

        filtered_versions = []
        for version in word.versions:
            matching_topics = [
                topic for topic in version.topics if topic.topic_id == topic_id
            ]
            if matching_topics:
                version.topics = matching_topics
                filtered_versions.append(version)

        if filtered_versions:
            word.versions = filtered_versions
            words.append(word)

    words.sort(key=lambda w: w.word.lower())
    return words
