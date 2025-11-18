import streamlit as st
import datetime
from app.core.db import get_db
from app.core.models.course_model import Course
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject


@st.cache_data(ttl=datetime.timedelta(hours=1))
def get_courses() -> list[Course]:
    """Get all Courses with their Subject and Level objects."""
    db = get_db()
    q = """
        SELECT
            c.id AS course_id,
            c.name AS course_name,
            c.slug as course_slug,
            s.id AS subject_id,
            s.name AS subject_name,
            s.slug as subject_slug,
            l.id AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM Courses AS c
        JOIN Subjects AS s ON c.subject_id = s.id
        LEFT JOIN Levels AS l ON c.level_id = l.id
        ORDER BY s.name, l.name, c.name
    """
    rows = db.execute(q).fetchall()

    courses = []
    for r in rows:
        subject = Subject(
            pk=r["subject_id"], name=r["subject_name"], slug=r["subject_slug"]
        )
        level = (
            Level(
                pk=r["level_id"],
                name=r["level_name"],
                description=r["level_description"],
            )
            if r["level_id"]
            else None
        )
        course = Course(
            pk=r["course_id"],
            name=r["course_name"],
            slug=r["course_slug"],
            subject=subject,
            level=level,
        )
        courses.append(course)

    return courses
