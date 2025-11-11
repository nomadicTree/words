from app.core.db import get_db

from app.core.models.course_model import Course
from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.word_models import Word, WordVersion, RelatedWord
from app.core.models.subject_model import Subject


def search_words(
    query: str, subject_id=None, course_id=None, topic_id=None
) -> list[dict]:
    """Search for words by text and optional filters."""
    db = get_db()
    q = """
        SELECT
            word_id,
            word,
            MIN(subject_name) AS subject_name,
            MIN(course_name) AS course_name
        FROM vw_WordDetails
        WHERE word LIKE :query
    """
    params = {"query": f"%{query}%"}

    if subject_id:
        q += " AND subject_id = :subject_id"
        params["subject_id"] = subject_id
    if course_id:
        q += " AND course_id = :course_id"
        params["course_id"] = course_id
    if topic_id:
        q += " AND topic_id = :topic_id"
        params["topic_id"] = topic_id

    q += " GROUP BY word_id, word ORDER BY word"

    rows = db.execute(q, params).fetchall()
    return [dict(r) for r in rows]


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


def get_word_versions(word_id: int) -> list[WordVersion]:
    db = get_db()
    q_versions = """
        SELECT
            wv.id AS version_id,
            wv.word_id,
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
        LEFT JOIN WordVersionLevels wvl ON wvl.word_version_id = wv.id
        LEFT JOIN Levels l ON wvl.level_id = l.id
        WHERE wv.word_id = ?
        ORDER BY wv.created_at DESC
    """

    rows = db.execute(q_versions, (word_id,)).fetchall()
    versions_by_id: dict[int, dict] = {}

    for row in rows:
        v_id = row["version_id"]
        if v_id not in versions_by_id:
            versions_by_id[v_id] = {
                "id": v_id,
                "definition": row["definition"],
                "characteristics": row["characteristics"],
                "examples": row["examples"],
                "non_examples": row["non_examples"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "levels": [],
            }
        if row["level_id"]:
            versions_by_id[v_id]["levels"].append(
                Level(
                    row["level_id"],
                    row["level_name"],
                    row["level_description"],
                )
            )

    return [
        WordVersion(
            wv_id=v["id"],
            definition=v["definition"],
            characteristics=v["characteristics"],
            examples=v["examples"],
            non_examples=v["non_examples"],
            levels=v["levels"],
            topics=[],  # fill later
        )
        for v in versions_by_id.values()
    ]


def get_word_topics_for_version(
    version_id: int, subject: Subject
) -> list[Topic]:
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
    return Word(
        word_id, get_word_text(word_id), subject, versions, related_words
    )
