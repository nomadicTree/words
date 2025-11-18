from collections import defaultdict
from typing import Any

from app.core.db import get_db
import datetime
import streamlit as st

from app.core.models.course_model import Course
from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.word_models import (
    Word,
    WordVersion,
    RelatedWord,
)
from app.core.models.subject_model import Subject

# ============================================================
# RELATED WORDS
# ============================================================


def get_related_words(word_id: int) -> list[RelatedWord]:
    db = get_db()
    q = """
        SELECT w.id, w.word, w.slug, s.slug AS subject_slug
        FROM WordRelationships r
        JOIN Words w
          ON w.id = CASE
            WHEN r.word_id1 = ? THEN r.word_id2
            ELSE r.word_id1
          END
        JOIN Subjects s ON w.subject_id = s.id
        WHERE r.word_id1 = ? OR r.word_id2 = ?
        ORDER BY w.word
    """
    rows = db.execute(q, (word_id, word_id, word_id)).fetchall()
    return [
        RelatedWord(
            word_id=r["id"],
            word=r["word"],
            slug=r["slug"],
            subject_slug=r["subject_slug"],
        )
        for r in rows
    ]


# ============================================================
# WORD VERSIONS (including levels)
# ============================================================


def build_word_versions_query(word_id: int):
    q = """
        SELECT
            wv.id AS version_id,
            wv.word_id,
            w.word AS word_str,
            w.slug AS word_slug,
            s.slug AS subject_slug,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples,
            wv.created_at,
            wv.updated_at,
            l.id AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM WordVersions wv
        JOIN Words w ON w.id = wv.word_id
        JOIN Subjects s ON w.subject_id = s.id
        LEFT JOIN WordVersionLevels wvl ON wvl.word_version_id = wv.id
        LEFT JOIN Levels l ON wvl.level_id = l.id
        WHERE wv.word_id = ?
        ORDER BY wv.created_at DESC
    """
    return q, (word_id,)


def group_word_version_rows(rows) -> dict[int, dict[str, Any]]:
    grouped = defaultdict(
        lambda: {
            "id": None,
            "word": None,
            "word_slug": None,
            "subject_slug": None,
            "definition": None,
            "characteristics": None,
            "examples": None,
            "non_examples": None,
            "created_at": None,
            "updated_at": None,
            "levels": [],
        }
    )

    for r in rows:
        vid = r["version_id"]
        data = grouped[vid]

        if data["id"] is None:
            data.update(
                {
                    "id": vid,
                    "word": r["word_str"],
                    "word_slug": r["word_slug"],
                    "subject_slug": r["subject_slug"],
                    "definition": r["definition"],
                    "characteristics": r["characteristics"],
                    "examples": r["examples"],
                    "non_examples": r["non_examples"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                }
            )

        if r["level_id"]:
            data["levels"].append(
                Level(
                    pk=r["level_id"],
                    name=r["level_name"],
                    description=r["level_description"],
                )
            )

    return grouped


def hydrate_word_versions(grouped) -> list[WordVersion]:
    versions = []
    for v in grouped.values():
        versions.append(
            WordVersion(
                pk=v["id"],
                word=v["word"],
                word_slug=v["word_slug"],
                subject_slug=v["subject_slug"],
                definition=v["definition"],
                characteristics=v["characteristics"],
                examples=v["examples"],
                non_examples=v["non_examples"],
                levels=v["levels"],
                topics=[],  # filled later
            )
        )
    return versions


def get_word_versions(word_id: int) -> list[WordVersion]:
    db = get_db()
    sql, params = build_word_versions_query(word_id)
    rows = db.execute(sql, params).fetchall()
    grouped = group_word_version_rows(rows)
    versions = hydrate_word_versions(grouped)
    return versions


# ============================================================
# TOPICS FOR A VERSION
# ============================================================


def get_word_topics_for_version(version_id: int, subject: Subject) -> list[Topic]:
    db = get_db()
    q = """
        SELECT
            t.id AS topic_id,
            t.code,
            t.name AS topic_name,
            c.id AS course_id,
            c.name AS course_name,
            c.slug AS course_slug,
            l.id AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM WordVersionContexts wvc
        JOIN Topics t ON wvc.topic_id = t.id
        JOIN Courses c ON t.course_id = c.id
        LEFT JOIN Levels l ON c.level_id = l.id
        WHERE wvc.word_version_id = ?
        ORDER BY t.code
    """
    rows = db.execute(q, (version_id,)).fetchall()
    topics = []
    for r in rows:
        level = (
            Level(r["level_id"], r["level_name"], r["level_description"])
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
        topics.append(Topic(r["topic_id"], r["code"], r["topic_name"], course))
    return topics


# ============================================================
# WORD + SUBJECT
# ============================================================


def get_word_subject(word_id: int) -> Subject | None:
    db = get_db()
    q = """
        SELECT s.id, s.name, s.slug
        FROM Words w
        JOIN Subjects s ON w.subject_id = s.id
        WHERE w.id = ?
    """
    row = db.execute(q, (word_id,)).fetchone()
    if not row:
        return None
    return Subject(row["id"], row["name"], row["slug"])


def get_word_text_and_slug(word_id: int) -> tuple[str, str] | None:
    db = get_db()
    q = """SELECT word, slug FROM Words WHERE id = ?"""
    row = db.execute(q, (word_id,)).fetchone()
    if not row:
        return None
    return row["word"], row["slug"]


def get_synonyms_for_word(word_id: int) -> list[str]:
    db = get_db()
    q = "SELECT synonym FROM Synonyms WHERE word_id = ? ORDER BY synonym"
    rows = db.execute(q, (word_id,)).fetchall()
    return [r["synonym"] for r in rows]


# ============================================================
# FULL WORD OBJECT
# ============================================================


@st.cache_data(ttl=datetime.timedelta(hours=1), max_entries=100)
def get_word_full(word_id: int) -> Word | None:
    subject = get_word_subject(word_id)
    if not subject:
        return None

    row = get_word_text_and_slug(word_id)
    if not row:
        return None

    word_text, word_slug = row

    versions = get_word_versions(word_id)
    for version in versions:
        version.topics = get_word_topics_for_version(version.pk, subject)

    related_words = get_related_words(word_id)
    synonyms = get_synonyms_for_word(word_id)

    return Word(
        pk=word_id,
        word=word_text,
        slug=word_slug,
        subject=subject,
        versions=versions,
        related_words=related_words,
        synonyms=synonyms,
    )


# ============================================================
# GET WORDVERSION BY ID (rarely used now)
# ============================================================


def get_word_version_by_id(wv_id: int) -> WordVersion | None:
    db = get_db()
    q = """
        SELECT
            wv.id AS wv_id,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples,
            w.word AS word,
            w.slug AS word_slug,
            s.slug AS subject_slug
        FROM WordVersions wv
        JOIN Words w ON wv.word_id = w.id
        JOIN Subjects s ON w.subject_id = s.id
        WHERE wv.id = :wv_id
    """
    row = db.execute(q, {"wv_id": wv_id}).fetchone()
    if not row:
        return None

    subject = Subject(None, None, row["subject_slug"])
    levels = _fetch_levels_for_version(db, wv_id)
    topics = get_word_topics_for_version(wv_id, subject)

    return WordVersion(
        pk=row["wv_id"],
        word=row["word"],
        word_slug=row["word_slug"],
        subject_slug=row["subject_slug"],
        definition=row["definition"],
        characteristics=row["characteristics"],
        examples=row["examples"],
        non_examples=row["non_examples"],
        levels=levels,
        topics=topics,
    )


# ============================================================
# VERSIONS PER TOPIC/COURSE
# ============================================================


def get_word_versions_for_topic(topic: Topic) -> list[WordVersion]:
    db = get_db()

    q = """
        SELECT
            wv.id AS wv_id,
            w.word AS word,
            w.slug AS word_slug,
            s.slug AS subject_slug,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples
        FROM WordVersionContexts wvc
        JOIN WordVersions wv ON wvc.word_version_id = wv.id
        JOIN Words w ON wv.word_id = w.id
        JOIN Subjects s ON w.subject_id = s.id
        WHERE wvc.topic_id = :topic_id
        ORDER BY w.word COLLATE NOCASE
    """

    rows = db.execute(q, {"topic_id": topic.pk}).fetchall()

    results = []
    for r in rows:
        subject = Subject(None, None, r["subject_slug"])
        levels = _fetch_levels_for_version(db, r["wv_id"])
        topics = get_word_topics_for_version(r["wv_id"], subject)
        results.append(
            WordVersion(
                pk=r["wv_id"],
                word=r["word"],
                word_slug=r["word_slug"],
                subject_slug=r["subject_slug"],
                definition=r["definition"],
                characteristics=r["characteristics"],
                examples=r["examples"],
                non_examples=r["non_examples"],
                levels=levels,
                topics=topics,
            )
        )

    return results


# ============================================================
# HELPERS
# ============================================================


def _fetch_levels_for_version(db, version_id: int) -> list[Level]:
    rows = db.execute(
        """
        SELECT l.id, l.name, l.description
        FROM WordVersionLevels wvl
        JOIN Levels l ON wvl.level_id = l.id
        WHERE wvl.word_version_id = :wv_id
        """,
        {"wv_id": version_id},
    ).fetchall()
    return [Level(r["id"], r["name"], r["description"]) for r in rows]


def _build_word_version(row, levels, topics) -> WordVersion:
    return WordVersion(
        pk=row["wv_id"],
        word=row["word"],
        word_slug=row["word_slug"],
        subject_slug=row["subject_slug"],
        definition=row["definition"],
        characteristics=row["characteristics"],
        examples=row["examples"],
        non_examples=row["non_examples"],
        levels=list(levels),
        topics=list(topics),
    )


def get_word_by_word_slug_and_subject_slug(word_slug: str, subject_slug: str):
    db = get_db()
    q = """
        SELECT w.id
        FROM Words w
        JOIN Subjects s ON w.subject_id = s.id
        WHERE w.slug = ? AND s.slug = ?
        LIMIT 1;
    """
    row = db.execute(q, (word_slug, subject_slug)).fetchone()
    if not row:
        return None
    return get_word_full(row["id"])


def get_word_versions_for_course(course: Course) -> list[WordVersion]:
    """
    Return all WordVersions that appear in any Topic belonging to the given course.
    """

    db = get_db()

    q = """
        SELECT DISTINCT
            wv.id AS wv_id,
            w.word AS word,
            w.slug AS word_slug,
            s.slug AS subject_slug,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples
        FROM WordVersionContexts wvc
        JOIN WordVersions wv ON wvc.word_version_id = wv.id
        JOIN Words w ON wv.word_id = w.id
        JOIN Subjects s ON w.subject_id = s.id
        JOIN Topics t ON wvc.topic_id = t.id
        WHERE t.course_id = :course_id
        ORDER BY w.word COLLATE NOCASE
    """

    rows = db.execute(q, {"course_id": course.pk}).fetchall()

    results = []
    for r in rows:
        # Subject object needed for topic hydration
        subject = Subject(
            pk=None,  # not needed here
            name=None,  # not needed here
            slug=r["subject_slug"],
        )

        levels = _fetch_levels_for_version(db, r["wv_id"])
        topics = get_word_topics_for_version(r["wv_id"], subject)

        results.append(
            WordVersion(
                pk=r["wv_id"],
                word=r["word"],
                word_slug=r["word_slug"],
                subject_slug=r["subject_slug"],
                definition=r["definition"],
                characteristics=r["characteristics"],
                examples=r["examples"],
                non_examples=r["non_examples"],
                levels=levels,
                topics=topics,
            )
        )

    return results
