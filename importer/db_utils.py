import sqlite3
from contextlib import contextmanager
from importer.strings import slugify
from collections import defaultdict
from typing import Optional


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


def get_or_create_subject(conn: sqlite3.Connection, name: str) -> int:
    """
    Create or retrieve a subject in a slug-stable way
    - Always match by slug first.
    - If slug exists, update the name (slug preserved).
    - If name exists (but slug does not), preserve the existing slug.
    - If neither exists, create with a derived slug.
    """

    new_slug = slugify(name)

    # 1. Try to find an existing subject by slug (canonical identity)
    row = conn.execute(
        "SELECT id, name, slug FROM Subjects WHERE slug = ?", (new_slug,)
    ).fetchone()

    if row:
        # Slug already exists → update name if needed, slug stays fixed
        subject_id = row["id"]
        old_name = row["name"]

        if old_name != name:
            conn.execute(
                "UPDATE Subjects SET name = ? WHERE id = ?", (name, subject_id)
            )

        return subject_id

    # 2. Try to find an existing subject by name (legacy match)
    row = conn.execute(
        "SELECT id, name, slug FROM Subjects WHERE name = ?", (name,)
    ).fetchone()

    if row:
        # Keep the old slug, don’t assign a new one
        return row["id"]

    # 3. New subject — ensure slug is free
    row = conn.execute(
        "SELECT id, name FROM Subjects WHERE slug = ?", (new_slug,)
    ).fetchone()

    if row:
        raise ValueError(
            f"Cannot create subject '{name}': slug '{new_slug}' "
            f"already belongs to subject '{row['name']}'."
        )

    # 4. Safe to create new subject
    cur = conn.execute(
        "INSERT INTO Subjects (name, slug) VALUES (?, ?)", (name, new_slug)
    )
    return cur.lastrowid


def get_or_create_level(conn, name: str, description: str) -> int:
    row = conn.execute(
        "SELECT id, description FROM Levels WHERE name = ?", (name,)
    ).fetchone()

    if row:
        level_id = row["id"]
        old_desc = row["description"] or ""

        # Update description if needed
        if old_desc != description:
            conn.execute(
                "UPDATE Levels SET description = ? WHERE id = ?",
                (description, level_id),
            )
            conn.commit()

        return level_id

    # Create new level
    cur = conn.execute(
        "INSERT INTO Levels (name, description) VALUES (?, ?)", (name, description)
    )
    return cur.lastrowid


def get_or_create_course(
    conn: sqlite3.Connection, subject_id: int, name: str, level_id: int
) -> int:
    """
    Create or retrieve a course in a slug-stable way.

    Slug rules:
      - Derived once when inserting new course.
      - If slug exists, update name/level but keep slug.
      - If name exists but slug differs, keep the old slug.
      - If slug collides with another course in the same subject -> error.

    Returns:
        int: the course's primary key.
    """

    new_slug: str = slugify(name)

    # 1. Try slug match (canonical identity)
    row = conn.execute(
        """
        SELECT id, name, slug, level_id
        FROM Courses
        WHERE slug = ? AND subject_id = ?
        """,
        (new_slug, subject_id),
    ).fetchone()

    if row is not None:
        course_id: int = row["id"]
        old_name: str = row["name"]
        old_level: int = row["level_id"]

        # Update name if it changed
        if old_name != name:
            conn.execute("UPDATE Courses SET name = ? WHERE id = ?", (name, course_id))

        # Update level if it changed
        if old_level != level_id:
            conn.execute(
                "UPDATE Courses SET level_id = ? WHERE id = ?", (level_id, course_id)
            )

        return course_id

    # 2. Legacy match: same name in same subject
    row = conn.execute(
        """
        SELECT id, slug, level_id
        FROM Courses
        WHERE name = ? AND subject_id = ?
        """,
        (name, subject_id),
    ).fetchone()

    if row is not None:
        course_id: int = row["id"]
        old_level: int = row["level_id"]

        if old_level != level_id:
            conn.execute(
                "UPDATE Courses SET level_id = ? WHERE id = ?", (level_id, course_id)
            )

        return course_id

    # 3. Ensure slug is free within subject
    row = conn.execute(
        """
        SELECT id, name FROM Courses 
        WHERE slug = ? AND subject_id = ?
        """,
        (new_slug, subject_id),
    ).fetchone()

    if row is not None:
        raise ValueError(
            f"Cannot create course '{name}': slug '{new_slug}' already belongs "
            f"to '{row['name']}' (id={row['id']}) in this subject."
        )

    # 4. Create new course
    cur = conn.execute(
        """
        INSERT INTO Courses (name, subject_id, level_id, slug)
        VALUES (?, ?, ?, ?)
        """,
        (name, subject_id, level_id, new_slug),
    )
    return int(cur.lastrowid)


def get_course_by_name(conn, name):
    """Return (course_id, subject_id) for a course name, or (None, None)."""
    cur = conn.execute("SELECT id, subject_id FROM Courses WHERE name = ?", (name,))
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


def get_or_create_topic(
    conn: sqlite3.Connection, course_id: int, code: str, name: str
) -> int:
    """
    Create or retrieve a topic.

    Topic identity:
        (course_id, code) is the unique key.

    Behaviour:
        - If a topic with this (course_id, code) exists → update name if changed.
        - If not → insert a new topic.
    """

    # 1. Check for existing topic by (course_id, code)
    row = conn.execute(
        """
        SELECT id, name
        FROM Topics
        WHERE course_id = ? AND code = ?
        """,
        (course_id, code),
    ).fetchone()

    if row is not None:
        topic_id: int = row["id"]
        old_name: str = row["name"]

        # Update name if changed
        if old_name != name:
            conn.execute("UPDATE Topics SET name = ? WHERE id = ?", (name, topic_id))

        return topic_id

    # 2. Insert new topic
    cur = conn.execute(
        """
        INSERT INTO Topics (course_id, code, name)
        VALUES (?, ?, ?)
        """,
        (course_id, code, name),
    )
    return int(cur.lastrowid)


# ---------- words and versions ---------- #
def get_word_versions_with_levels(
    conn: sqlite3.Connection,
    word_id: int,
) -> dict[int, set[int]]:
    """
    Return a mapping: version_id -> set(level_id) for all WordVersions of this word.
    """
    rows = conn.execute(
        """
        SELECT wv.id AS version_id, wvl.level_id
        FROM WordVersions AS wv
        LEFT JOIN WordVersionLevels AS wvl
          ON wv.id = wvl.word_version_id
        WHERE wv.word_id = ?
        """,
        (word_id,),
    ).fetchall()

    version_levels: dict[int, set[int]] = defaultdict(set)
    for row in rows:
        vid = row["version_id"]
        level_id = row["level_id"]
        if level_id is not None:
            version_levels[vid].add(level_id)
        else:
            # Version with no levels: represent as empty set
            version_levels.setdefault(vid, set())

    return dict(version_levels)


def get_or_create_word(conn: sqlite3.Connection, subject_id: int, word: str) -> int:
    """
    Create or retrieve a Word in a slug-stable way.

    Slug rules:
      - Derived once from the word on initial insertion.
      - Slug is preserved forever, even if the word's text changes.
      - Matching by slug (within a subject) has priority over matching by name.
    """

    new_slug = slugify(word)

    # 1. Prefer slug match (stable identity within subject)
    row = conn.execute(
        """
        SELECT id, word, slug
        FROM Words
        WHERE slug = ? AND subject_id = ?
        """,
        (new_slug, subject_id),
    ).fetchone()

    if row is not None:
        word_id: int = row["id"]
        old_word: str = row["word"]

        # Name changed in YAML → update, but keep slug
        if old_word != word:
            conn.execute(
                "UPDATE Words SET word = ? WHERE id = ?",
                (word, word_id),
            )

        return word_id

    # 2. Fallback: match by (word, subject) if it exists
    row = conn.execute(
        """
        SELECT id, slug
        FROM Words
        WHERE word = ? AND subject_id = ?
        """,
        (word, subject_id),
    ).fetchone()

    if row is not None:
        # Keep existing slug, don't regenerate
        return int(row["id"])

    # 3. Ensure slug isn't already used for another word in this subject
    row = conn.execute(
        """
        SELECT id, word
        FROM Words
        WHERE slug = ? AND subject_id = ?
        """,
        (new_slug, subject_id),
    ).fetchone()

    if row is not None:
        raise ValueError(
            f"Cannot create word '{word}': slug '{new_slug}' already belongs to "
            f"'{row['word']}' (id={row['id']}) in this subject."
        )

    # 4. Insert new word
    cur = conn.execute(
        "INSERT INTO Words (word, subject_id, slug) VALUES (?, ?, ?)",
        (word, subject_id, new_slug),
    )
    return int(cur.lastrowid)


def get_or_create_word_version_for_levels(
    conn: sqlite3.Connection,
    word_id: int,
    level_ids: list[int],
    definition: str,
    characteristics: str,
    examples: str,
    non_examples: str,
) -> int:
    """
    Enforce one WordVersion per (word, exact level-set) with strict level exclusivity.

    Implements your rules:

      - Each YAML file describes exactly one WordVersion and its level-set L_new.
      - For a given word:
          * Each level can belong to at most one version.
          * If any level in L_new is already owned by a *different* level-set → conflict.
      - If an existing version has exactly L_new → reuse and update it.
      - If no level in L_new is owned → create a new version and attach levels.
      - No merging, splitting or reassigning; conflicts raise ValueError.
    """

    new_levels: set[int] = set(level_ids)

    # Get all existing versions + their level sets for this word
    version_levels: dict[int, set[int]] = get_word_versions_with_levels(conn, word_id)

    # Build reverse index: level_id -> set(version_id)
    level_to_versions: dict[int, set[int]] = {}
    for vid, levels in version_levels.items():
        for lid in levels:
            level_to_versions.setdefault(lid, set()).add(vid)

    # Sanity check: detect DB corruption - multiple versions with identical level sets
    seen_sets: dict[frozenset[int], list[int]] = {}
    for vid, levels in version_levels.items():
        key = frozenset(levels)
        seen_sets.setdefault(key, []).append(vid)

    for key, vids in seen_sets.items():
        if len(vids) > 1:
            raise ValueError(
                f"Data integrity error: multiple WordVersions {vids} share the same "
                f"level-set {sorted(key)} for word_id={word_id}. "
                "Fix the DB before importing."
            )

    # --- 1️⃣ Conflict detection per your rules ---

    conflicting_versions: set[int] = set()

    for level_id in new_levels:
        owners = level_to_versions.get(level_id, set())

        # level owned by multiple existing versions -> conflict
        if len(owners) > 1:
            conflicting_versions.update(owners)
            continue

        if len(owners) == 1:
            vid = next(iter(owners))
            existing_set = version_levels.get(vid, set())

            # If the existing owner has a different level-set than L_new -> conflict
            if existing_set != new_levels:
                conflicting_versions.add(vid)

    if conflicting_versions:
        # Build a helpful message
        details = []
        for vid in sorted(conflicting_versions):
            levels = sorted(version_levels.get(vid, set()))
            details.append(f"version {vid} owns levels {levels}")

        raise ValueError(
            "Level ownership conflict while importing WordVersion for word_id="
            f"{word_id} with level-set {sorted(new_levels)}.\n"
            "Conflicting existing versions:\n  "
            + "\n  ".join(details)
            + "\nNo changes have been made; fix YAML or DB and re-run."
        )

    # --- 2️⃣ Exact match reuse (Case A) ---

    exact_match_id: Optional[int] = None
    for vid, levels in version_levels.items():
        if levels == new_levels:
            exact_match_id = vid
            break

    if exact_match_id is not None:
        conn.execute(
            """
            UPDATE WordVersions
            SET definition     = ?,
                characteristics = ?,
                examples        = ?,
                non_examples    = ?,
                updated_at      = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (definition, characteristics, examples, non_examples, exact_match_id),
        )
        conn.commit()
        return exact_match_id

    # --- 3️⃣ No owner exists -> create new version (Case B) ---

    # Defensive check: there should be no owner of any level at this point
    for level_id in new_levels:
        if level_to_versions.get(level_id):
            # Should be impossible if conflict detection is correct
            raise RuntimeError(
                f"Unexpected owner for level {level_id} when creating new version."
            )

    cur = conn.execute(
        """
        INSERT INTO WordVersions (word_id, definition, characteristics, examples, non_examples)
        VALUES (?, ?, ?, ?, ?)
        """,
        (word_id, definition, characteristics, examples, non_examples),
    )
    version_id = int(cur.lastrowid)

    # Attach levels to this new version
    for level_id in new_levels:
        conn.execute(
            """
            INSERT INTO WordVersionLevels (word_version_id, level_id)
            VALUES (?, ?)
            """,
            (version_id, level_id),
        )

    conn.commit()
    return version_id


def prune_supersets_for_word(conn: sqlite3.Connection, word_id: int) -> None:
    """
    After importing all YAML files for a word, prune obsolete superset versions.

    If any WordVersion's level-set is a strict superset of two or more smaller versions
    whose level-sets together exactly cover the superset's levels, delete the superset.

    This covers the case where the user intentionally splits a combined KS4+KS5
    definition into separate KS4 and KS5 YAMLs.
    """

    version_levels = get_word_versions_with_levels(conn, word_id)

    # Precompute list of (version_id, levels) for convenience
    items = [(vid, levels) for vid, levels in version_levels.items()]

    to_delete: set[int] = set()

    for vid, levels in items:
        if not levels:
            continue  # ignore versions with no levels

        # Find proper subset versions
        subset_versions: list[int] = []
        subset_union: set[int] = set()

        for other_vid, other_levels in items:
            if other_vid == vid:
                continue

            # Proper subset: non-empty, strictly smaller, and contained
            if other_levels and other_levels < levels:
                subset_versions.append(other_vid)
                subset_union |= other_levels

        # Need at least 2 smaller versions and their union must exactly match this superset
        if len(subset_versions) >= 2 and subset_union == levels:
            to_delete.add(vid)

    for vid in sorted(to_delete):
        conn.execute(
            "DELETE FROM WordVersions WHERE id = ?",
            (vid,),
        )

    if to_delete:
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


def get_levels_for_courses(conn, course_names: list[str]) -> set[str]:
    """
    Given a list of course names, return the set of level names they imply.
    """
    inferred_levels = set()

    for course_name in course_names:
        row = conn.execute(
            """
            SELECT l.name AS level_name
            FROM Courses c
            JOIN Levels l ON c.level_id = l.id
            WHERE c.name = ?
            """,
            (course_name,),
        ).fetchone()

        if row:
            inferred_levels.add(row["level_name"])

    return inferred_levels


def link_word_to_topic(
    conn: sqlite3.Connection, word_version_id: int, topic_id: int
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO WordVersionContexts (word_version_id, topic_id)
        VALUES (?, ?)
        """,
        (word_version_id, topic_id),
    )


def link_wordversion_to_level(
    conn: sqlite3.Connection, word_version_id: int, level_id: int
) -> None:
    conn.execute(
        """
        INSERT OR IGNORE INTO WordVersionLevels (word_version_id, level_id)
        VALUES (?, ?)
        """,
        (word_version_id, level_id),
    )
    conn.commit()


def get_level_id(conn: sqlite3.Connection, name: str) -> int | None:
    cur = conn.execute(
        "SELECT id FROM Levels WHERE name = ?",
        (name.strip(),),
    )
    row = cur.fetchone()
    return row["id"] if row else None


def get_word_name(conn, word_id: int) -> str:
    row = conn.execute(
        "SELECT word FROM Words WHERE id = ?",
        (word_id,),
    ).fetchone()
    return row["word"] if row else ""
