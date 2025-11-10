import sqlite3
from contextlib import contextmanager


# ---------- connection helper ---------- #


@contextmanager
def db_connection(db_path):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ---------- level, subject, course, topic ---------- #


def get_or_create_subject(conn, name):
    cur = conn.execute("SELECT id FROM Subjects WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute("INSERT INTO Subjects (name) VALUES (?)", (name,))
    return cur.lastrowid


def get_or_create_level(conn, name, description=None):
    if not name:
        return None
    cur = conn.execute("SELECT id FROM Levels WHERE name = ?", (name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO Levels (name, description) VALUES (?, ?)",
        (name, description),
    )
    return cur.lastrowid


def get_or_create_course(conn, subject_id, name, level_id=None):
    cur = conn.execute(
        "SELECT id FROM Courses WHERE name = ? AND subject_id = ?",
        (name, subject_id),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO Courses (name, subject_id, level_id) VALUES (?, ?, ?)",
        (name, subject_id, level_id),
    )
    return cur.lastrowid


def get_course_by_name(conn, name):
    """Return (course_id, subject_id) for a course name, or (None, None)."""
    cur = conn.execute(
        "SELECT id, subject_id FROM Courses WHERE name = ?", (name,)
    )
    row = cur.fetchone()
    return row if row else (None, None)


def get_topic_id(conn, course_id, code):
    """Return topic ID for (course_id, code), or None if not found."""
    cur = conn.execute(
        "SELECT id FROM Topics WHERE course_id = ? AND code = ?",
        (course_id, code),
    )
    row = cur.fetchone()
    return row[0] if row else None


def get_or_create_topic(conn, course_id, code, name=None):
    cur = conn.execute(
        "SELECT id FROM Topics WHERE course_id = ? AND code = ?",
        (course_id, code),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO Topics (course_id, code, name) VALUES (?, ?, ?)",
        (course_id, code, name),
    )
    return cur.lastrowid


# ---------- words and versions ---------- #


def get_or_create_word(conn, subject_id, word, synonyms=None):
    cur = conn.execute(
        "SELECT id FROM Words WHERE word = ? AND subject_id = ?",
        (word, subject_id),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        "INSERT INTO Words (word, subject_id, synonyms) VALUES (?, ?, ?)",
        (word, subject_id, synonyms or ""),
    )
    return cur.lastrowid


def get_or_create_word_version(
    conn,
    word_id,
    course_id,
    definition=None,
    characteristics=None,
    examples=None,
    non_examples=None,
):
    cur = conn.execute(
        "SELECT id FROM WordVersions WHERE word_id = ? AND course_id = ?",
        (word_id, course_id),
    )
    row = cur.fetchone()
    if row:
        return row[0]
    cur = conn.execute(
        """
        INSERT INTO WordVersions
        (word_id, course_id, definition, characteristics, examples, non_examples)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            word_id,
            course_id,
            definition,
            characteristics,
            examples,
            non_examples,
        ),
    )
    return cur.lastrowid


def link_word_to_topic(conn, word_version_id, topic_id):
    conn.execute(
        """
        INSERT OR IGNORE INTO WordVersionContexts (word_version_id, topic_id)
        VALUES (?, ?)
        """,
        (word_version_id, topic_id),
    )
