import sqlite3
from contextlib import contextmanager


# ---------- connection helper ---------- #


@contextmanager
def db_connection(db_path):
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row  # rows behave like dicts: row["id"]
    try:
        yield conn  # this is what `with db_connection(...) as conn` uses
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
        "INSERT INTO Words (word, subject_id) VALUES (?, ?)",
        (word, subject_id),
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


def link_wordversion_to_level(conn, word_version_id, level_id):
    conn.execute(
        """
        INSERT OR IGNORE INTO WordVersionLevels (word_version_id, level_id)
        VALUES (?, ?)
        """,
        (word_version_id, level_id),
    )
    conn.commit()


def get_or_create_word_version(
    conn, word_id, definition, characteristics, examples, non_examples
):
    """Ensure one unique version per word+meaning."""
    cur = conn.execute(
        """
        INSERT INTO WordVersions (word_id, definition, characteristics, examples, non_examples)
        VALUES (?, ?, ?, ?, ?)
        """,
        (word_id, definition, characteristics, examples, non_examples),
    )
    conn.commit()
    return cur.lastrowid


def get_level_id(conn, name):
    cur = conn.execute(
        "SELECT id FROM Levels WHERE name = ?",
        (name.strip(),),
    )
    row = cur.fetchone()
    return row["id"] if row else None


def get_or_create_word_version_for_levels(
    conn,
    word_id: int,
    level_ids: list[int],
    definition: str,
    characteristics: str,
    examples: str,
    non_examples: str,
) -> int:
    """
    Find a WordVersion for this word with exactly this set of levels.
    If found, update it and return its id.
    If not, create a new WordVersion and link it to these levels.
    """
    level_ids_set = set(level_ids)

    # 1️⃣ Look for an existing version with the same level set
    cur = conn.execute(
        "SELECT id FROM WordVersions WHERE word_id = ?",
        (word_id,),
    )
    candidates = [row["id"] for row in cur.fetchall()]

    for vid in candidates:
        cur_levels = conn.execute(
            "SELECT level_id FROM WordVersionLevels WHERE word_version_id = ?",
            (vid,),
        )
        existing = {r["level_id"] for r in cur_levels.fetchall()}
        if existing == level_ids_set:
            # Update this version and reuse it
            conn.execute(
                """
                UPDATE WordVersions
                SET definition = ?,
                    characteristics = ?,
                    examples = ?,
                    non_examples = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (definition, characteristics, examples, non_examples, vid),
            )
            conn.commit()
            return vid

    # 2️⃣ No matching version: create a new one
    cur = conn.execute(
        """
        INSERT INTO WordVersions (word_id, definition, characteristics, examples, non_examples)
        VALUES (?, ?, ?, ?, ?)
        """,
        (word_id, definition, characteristics, examples, non_examples),
    )
    version_id = cur.lastrowid

    # Link this version to the given levels
    for level_id in level_ids:
        conn.execute(
            """
            INSERT OR IGNORE INTO WordVersionLevels (word_version_id, level_id)
            VALUES (?, ?)
            """,
            (version_id, level_id),
        )

    conn.commit()
    return version_id


def prune_superset_word_versions(conn, word_id: int) -> int:
    """
    Delete any WordVersion whose level set is a strict superset of two or more
    other versions for the same word.

    Returns the number of pruned versions.
    """
    # Get all versions for this word and their level sets
    q_versions = """
    SELECT wv.id, GROUP_CONCAT(l.name, ',') AS levels
    FROM WordVersions wv
    LEFT JOIN WordVersionLevels wvl ON wv.id = wvl.word_version_id
    LEFT JOIN Levels l ON wvl.level_id = l.id
    WHERE wv.word_id = ?
    GROUP BY wv.id
    """
    cur = conn.execute(q_versions, (word_id,))
    rows = [dict(r) for r in cur.fetchall()]
    if len(rows) <= 1:
        return 0  # nothing to prune

    # Build a map of version_id → level set
    level_sets = {r["id"]: set((r["levels"] or "").split(",")) for r in rows}
    pruned_ids = set()

    for vid_a, levels_a in level_sets.items():
        for vid_b, levels_b in level_sets.items():
            if vid_a == vid_b or not levels_b:
                continue
            # If A’s levels strictly contain B’s levels
            if levels_a > levels_b:
                pruned_ids.add(vid_a)

    for vid in pruned_ids:
        conn.execute(
            "DELETE FROM WordVersionLevels WHERE word_version_id = ?", (vid,)
        )
        conn.execute(
            "DELETE FROM WordVersionContexts WHERE word_version_id = ?", (vid,)
        )
        conn.execute("DELETE FROM WordVersions WHERE id = ?", (vid,))
    conn.commit()

    if pruned_ids:
        print(
            f"🧹 Pruned {len(pruned_ids)} superseded WordVersions for word_id={word_id}"
        )
    return len(pruned_ids)
