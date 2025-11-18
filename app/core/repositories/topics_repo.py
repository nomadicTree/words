import streamlit as st
import datetime
from app.core.db import get_db
from app.core.models.topic_model import Topic
from app.core.models.course_model import Course


@st.cache_data(ttl=datetime.timedelta(hours=1))
def get_topics_for_course(course: Course, only_with_words: bool = False) -> list[Topic]:
    """Return all topics for a given course.

    Args:
        course: The Course object to fetch topics for.
        only_with_words: If True, only return topics that have one or more linked words.
    """
    db = get_db()

    # Base query
    q = """
        SELECT
            t.id AS topic_id,
            t.code AS topic_code,
            t.name AS topic_name
        FROM Topics AS t
        WHERE t.course_id = :course_id
    """
    params = {"course_id": course.pk}

    # Add optional filter for topics that have at least one linked word
    if only_with_words:
        q += """
            AND EXISTS (
                SELECT 1
                FROM WordVersionContexts AS wvc
                JOIN WordVersions AS wv ON wvc.word_version_id = wv.id
                WHERE wvc.topic_id = t.id
                  AND wv.word_id IS NOT NULL
            )
        """

    q += " ORDER BY t.code COLLATE NOCASE"

    rows = db.execute(q, params).fetchall()

    topics = [
        Topic(
            pk=r["topic_id"],
            code=r["topic_code"],
            name=r["topic_name"],
            course=course,
        )
        for r in rows
    ]

    return topics
