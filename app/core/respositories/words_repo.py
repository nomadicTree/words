from collections import defaultdict
from typing import Any, Iterable

from app.core.db import get_db

from app.core.models.course_model import Course
from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.word_models import (
    Word,
    WordVersion,
    RelatedWord,
    SearchResult,
)
from app.core.models.subject_model import Subject


def search_words(query: str, subject_id=None, topic_id=None) -> list[SearchResult]:
    """Search for words by text, returning each word with its WordVersions and associated levels."""
    db = get_db()

    q = """
        SELECT
            w.id AS word_id,
            w.word,
            s.name AS subject_name,
            s.id as subject_id,
            wv.id AS word_version_id,
            l.id AS level_id,
            l.name AS level_name,
            l.description AS level_description
        FROM Words AS w
        JOIN Subjects AS s ON w.subject_id = s.id
        JOIN WordVersions AS wv ON wv.word_id = w.id
        LEFT JOIN WordVersionLevels AS wvl ON wvl.word_version_id = wv.id
        LEFT JOIN Levels AS l ON wvl.level_id = l.id
        WHERE w.word LIKE :query
    """

    params = {"query": f"%{query}%"}

    if subject_id:
        q += " AND s.id = :subject_id"
        params["subject_id"] = subject_id
    if topic_id:
        q += """
            AND wv.id IN (
                SELECT word_version_id
                FROM WordVersionContexts
                WHERE topic_id = :topic_id
            )
        """
        params["topic_id"] = topic_id

    q += " ORDER BY w.word COLLATE NOCASE"

    rows = db.execute(q, params).fetchall()

    # 🧩 Step 1: Group by word_id
    grouped_words = defaultdict(
        lambda: {
            "word": None,
            "subject_id": None,
            "subject_name": None,
            "versions": defaultdict(set),
        }
    )

    for r in rows:
        word_id = r["word_id"]
        wv_id = r["word_version_id"]

        grouped_words[word_id]["word"] = r["word"]
        grouped_words[word_id]["subject_id"] = r["subject_id"]
        grouped_words[word_id]["subject_name"] = r["subject_name"]

        if r["level_id"]:
            grouped_words[word_id]["versions"][wv_id].add(
                Level(r["level_id"], r["level_name"], r["level_description"])
            )

    # 🧩 Step 2: Build SearchResult objects
    results = []
    for word_id, data in grouped_words.items():
        versions = [
            {
                "word_version_id": wv_id,
                "levels": sorted(levels, key=lambda lvl: lvl.name),
            }
            for wv_id, levels in data["versions"].items()
        ]

        results.append(
            SearchResult(
                word_id=word_id,
                word=data["word"],
                subject=Subject(data["subject_id"], data["subject_name"]),
                versions=versions,
            )
        )

    return results


def get_related_words(word_id: int) -> list[RelatedWord]:
    db = get_db()
    q = """
        SELECT w.id AS word_id, w.word
        FROM WordRelationships r
        JOIN Words w
          ON w.id = CASE
            WHEN r.word_id1 = ? THEN r.word_id2
            ELSE r.word_id1
          END
        WHERE r.word_id1 = ? OR r.word_id2 = ?
        ORDER BY w.word
    """
    rows = db.execute(q, (word_id, word_id, word_id)).fetchall()
    return [RelatedWord(r["word_id"], r["word"]) for r in rows]


def build_word_versions_query(word_id: int) -> tuple[str, tuple]:
    """Return SQL and parameters for fetching all versions of a word."""
    q = """
        SELECT
            wv.id AS version_id,
            wv.word_id,
            w.word AS word_str,
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
        LEFT JOIN WordVersionLevels wvl ON wvl.word_version_id = wv.id
        LEFT JOIN Levels l ON wvl.level_id = l.id
        WHERE wv.word_id = ?
        ORDER BY wv.created_at DESC
    """
    return q, (word_id,)


def group_word_version_rows(rows) -> dict[int, dict[str, Any]]:
    """Group flat query rows by version_id, collecting Levels."""
    grouped = defaultdict(
        lambda: {
            "id": None,
            "word_id": None,
            "word_str": None,
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
        v_id = r["version_id"]
        data = grouped[v_id]

        # static fields (first row for that version)
        if data["id"] is None:
            data.update(
                {
                    "id": v_id,
                    "word_id": r["word_id"],
                    "word_str": r["word_str"],
                    "definition": r["definition"],
                    "characteristics": r["characteristics"],
                    "examples": r["examples"],
                    "non_examples": r["non_examples"],
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                }
            )

        # levels (can repeat)
        if r["level_id"]:
            data["levels"].append(
                Level(
                    level_id=r["level_id"],
                    name=r["level_name"],
                    description=r["level_description"],
                )
            )

    return grouped


def hydrate_word_versions(grouped: dict[int, dict[str, Any]]) -> list[WordVersion]:
    """Convert grouped rows to WordVersion model instances."""
    versions = []
    for v in grouped.values():
        versions.append(
            WordVersion(
                wv_id=v["id"],
                definition=v["definition"],
                characteristics=v["characteristics"],
                examples=v["examples"],
                non_examples=v["non_examples"],
                levels=v["levels"],
                topics=[],  # fill later
                word_id=v["word_id"],
                word=v["word_str"],
            )
        )
    return versions


def get_word_versions(word_id: int) -> list[WordVersion]:
    """Fetch all WordVersions for a given word, including their levels."""
    db = get_db()
    sql, params = build_word_versions_query(word_id)
    rows = db.execute(sql, params).fetchall()

    grouped = group_word_version_rows(rows)
    versions = hydrate_word_versions(grouped)
    return versions


def get_word_topics_for_version(version_id: int, subject: Subject) -> list[Topic]:
    db = get_db()
    q_topics = """
        SELECT
            t.id AS topic_id,
            t.code,
            t.name AS topic_name,
            c.id AS course_id,
            c.name AS course_name,
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
    rows = db.execute(q_topics, (version_id,)).fetchall()
    topics = []
    for r in rows:
        level = (
            Level(r["level_id"], r["level_name"], r["level_description"])
            if r["level_id"]
            else None
        )
        course = Course(r["course_id"], r["course_name"], subject, level)
        topics.append(Topic(r["topic_id"], r["code"], r["topic_name"], course))
    return topics


def get_word_subject(word_id: int) -> Subject:
    db = get_db()
    q_word = """
        SELECT w.id, w.word, s.id AS subject_id, s.name AS subject_name
        FROM Words w
        JOIN Subjects s ON w.subject_id = s.id
        WHERE w.id = ?
    """
    # --- fetch word & subject
    word_row = db.execute(q_word, (word_id,)).fetchone()
    if not word_row:
        return None
    subject = Subject(word_row["subject_id"], word_row["subject_name"])
    return subject


def get_word_text(word_id: int) -> str:
    db = get_db()
    q_word = """
        SELECT w.word
        FROM Words w
        Where w.id = ?
    """
    word_row = db.execute(q_word, (word_id,)).fetchone()
    if not word_row:
        return None
    return word_row["word"]


def get_word_full(word_id: int) -> Word:
    subject = get_word_subject(word_id)
    if not subject:
        return None

    versions = get_word_versions(word_id)

    # Populate topics for each version
    for version in versions:
        version.topics = get_word_topics_for_version(version.wv_id, subject)

    related_words = get_related_words(word_id)
    return Word(word_id, get_word_text(word_id), subject, versions, related_words)


def get_word_version_by_id(wv_id: int) -> WordVersion | None:
    """Return a WordVersion object with topics and levels."""
    db = get_db()

    # 1️⃣ Get the WordVersion, its Word, and Subject
    q = """
        SELECT
            wv.id AS wv_id,
            wv.word_id,
            w.word AS word,
            s.id AS subject_id,
            s.name AS subject_name,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples
        FROM WordVersions AS wv
        JOIN Words AS w ON wv.word_id = w.id
        JOIN Subjects AS s ON w.subject_id = s.id
        WHERE wv.id = :wv_id
    """
    row = db.execute(q, {"wv_id": wv_id}).fetchone()
    if not row:
        return None

    subject = Subject(row["subject_id"], row["subject_name"])

    levels = _fetch_levels_for_version(db, wv_id)
    topics = get_word_topics_for_version(row["wv_id"], subject)
    return _build_word_version(row, levels, topics)


def get_word_versions_for_topic(topic: Topic) -> list[WordVersion]:
    db = get_db()

    q = """
        SELECT
            wv.id AS wv_id,
            wv.word_id,
            w.word AS word,
            s.id AS subject_id,
            s.name AS subject_name,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples
        FROM WordVersionContexts wvc
        JOIN WordVersions wv ON wvc.word_version_id = wv.id
        JOIN Words w ON wv.word_id = w.id
        JOIN Subjects s ON w.subject_id = s.id
        WHERE wvc.topic_id = :topic_id
        ORDER BY w.word COLLATE NOCASE;
    """

    rows = db.execute(q, {"topic_id": topic.topic_id}).fetchall()

    results = []
    for r in rows:
        subject = Subject(r["subject_id"], r["subject_name"])
        levels = _fetch_levels_for_version(db, r["wv_id"])
        topics = get_word_topics_for_version(r["wv_id"], subject)
        results.append(_build_word_version(r, levels, topics))

    return results


def get_word_versions_for_course(course: Course) -> list[WordVersion]:
    db = get_db()

    q = """
        SELECT
            wv.id AS wv_id,
            wv.word_id,
            w.word AS word,
            s.id AS subject_id,
            s.name AS subject_name,
            wv.definition,
            wv.characteristics,
            wv.examples,
            wv.non_examples
        FROM WordVersionContexts wvc
        JOIN Topics t ON wvc.topic_id = t.id
        JOIN WordVersions wv ON wvc.word_version_id = wv.id
        JOIN Words w ON wv.word_id = w.id
        JOIN Subjects s ON w.subject_id = s.id
        WHERE t.course_id = :course_id
        ORDER BY w.word COLLATE NOCASE;
    """

    rows = db.execute(q, {"course_id": course.course_id}).fetchall()

    results = []
    seen = set()

    for r in rows:
        wv_id = r["wv_id"]
        if wv_id in seen:
            continue
        seen.add(wv_id)

        subject = Subject(r["subject_id"], r["subject_name"])
        levels = _fetch_levels_for_version(db, wv_id)
        topics = get_word_topics_for_version(wv_id, subject)
        results.append(_build_word_version(r, levels, topics))

    return results


def _fetch_levels_for_version(db, version_id: int) -> list[Level]:
    """Return all levels linked to a WordVersion."""
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


def _build_word_version(
    row: dict[str, Any], levels: Iterable[Level], topics: Iterable[Topic]
) -> WordVersion:
    """Create a WordVersion from a DB row and hydrated relationships."""
    return WordVersion(
        wv_id=row["wv_id"],
        word=row["word"],
        word_id=row["word_id"],
        definition=row["definition"],
        characteristics=row["characteristics"],
        examples=row["examples"],
        non_examples=row["non_examples"],
        levels=list(levels),
        topics=list(topics),
    )
