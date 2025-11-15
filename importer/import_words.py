import os
from importer.db_utils import (
    db_connection,
    get_course_by_name,
    get_topic_id,
    get_or_create_word,
    link_word_to_topic,
    get_levels_for_courses,
    get_level_id,
    get_or_create_word_version_for_levels,
    prune_supersets_for_word,
    get_word_name,
)
from collections import defaultdict
from importer.yaml_utils import load_word_file, clean_list


def find_word_files(subjects_root):
    """Return a list of all YAML files under any 'words' directory (recursively)."""
    word_files = []

    for root, dirs, files in os.walk(subjects_root):
        # Once we find a 'words' folder, traverse it fully
        if os.path.basename(root) == "words" or "words" in os.path.relpath(
            root, subjects_root
        ).split(os.sep):
            for fname in files:
                if fname.lower().endswith(".yaml"):
                    word_files.append(os.path.join(root, fname))

    return word_files


def import_words(subjects_root: str, db_path: str) -> None:
    """Recursively import all YAML word files under any 'words' directory and
    show a detailed summary per word."""

    word_files = find_word_files(subjects_root)
    if not word_files:
        print(
            f"⚠️  No word YAML files found under any 'words' directory in {subjects_root}."
        )
        return

    # Counters
    total_version_files = 0
    total_synonym_files = 0
    total_word_groups = 0
    total_skipped = 0

    # Per-word summary data
    word_summaries = []  # list of dicts, appended after each word group import

    # Split files
    version_files: list[str] = []
    synonym_files: list[str] = []

    for path in word_files:
        if path.lower().endswith(".synonyms.yaml"):
            synonym_files.append(path)
        else:
            version_files.append(path)

    total_version_files = len(version_files)
    total_synonym_files = len(synonym_files)

    with db_connection(db_path) as conn:
        # Group version files by (subject_id, word_name)
        groups: dict[tuple[int, str], list[str]] = group_word_files(conn, version_files)
        total_word_groups = len(groups)

        for (subject_id, word_name), paths in groups.items():
            # Find matching synonym file
            synonym_path = find_synonym_file_for_group(
                word_name=word_name,
                version_paths=paths,
                synonym_files=synonym_files,
            )

            # Count versions before import
            versions_before = count_word_versions(conn, subject_id, word_name)

            try:
                import_word_group(conn, subject_id, word_name, paths, synonym_path)
            except Exception as e:
                total_skipped += 1
                print(
                    f"❌ Error importing '{word_name}' (subject_id={subject_id}): {e}"
                )
                continue

            # Count versions after import
            versions_after = count_word_versions(conn, subject_id, word_name)

            # Compute deltas
            added = max(0, versions_after - versions_before)
            pruned = max(0, versions_before - versions_after)

            word_summaries.append(
                {
                    "word": word_name,
                    "subject_id": subject_id,
                    "before": versions_before,
                    "after": versions_after,
                    "added": added,
                    "pruned": pruned,
                }
            )

    # --------------------------
    # Final summary
    # --------------------------
    print("\n──────────────────────────────────────────────")
    print("📘 WORD IMPORT SUMMARY")
    print("──────────────────────────────────────────────")
    print(f"   • WordVersion files found: {total_version_files}")
    print(f"   • Synonym files found:     {total_synonym_files}")
    print(f"   • Word groups processed:   {total_word_groups}")
    print(f"   • Groups skipped/errors:   {total_skipped}")
    print("──────────────────────────────────────────────\n")

    # Per-word breakdown
    print("📗 PER-WORD VERSION SUMMARY\n")

    for s in word_summaries:
        print(f"   {s['word']} (subject={s['subject_id']}):")
        print(f"       Versions before:  {s['before']}")
        print(f"       Versions after:   {s['after']}")
        if s["added"] > 0:
            print(f"       ➕ Added:          {s['added']}")
        if s["pruned"] > 0:
            print(f"       ➖ Pruned:         {s['pruned']}")
        if s["added"] == 0 and s["pruned"] == 0:
            print(f"       (No change)")
        print()  # blank line for readability

    print("   Import completed.\n")


def count_word_versions(conn, subject_id: int, word_name: str) -> int:
    row = conn.execute(
        """
        SELECT Words.id AS word_id
        FROM Words
        WHERE Words.subject_id = ? AND Words.word = ?
        """,
        (subject_id, word_name),
    ).fetchone()

    if not row:
        return 0

    word_id = row["word_id"]
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM WordVersions WHERE word_id = ?",
        (word_id,),
    ).fetchone()["c"]

    return count


def group_word_files(conn, word_files: list[str]) -> dict[tuple[int, str], list[str]]:
    """
    Group YAML files by (subject_id, word_name).

    Each file:
      - must have at least one topic
      - all its courses must resolve to the same subject
    """
    groups: dict[tuple[int, str], list[str]] = defaultdict(list)

    for path in word_files:
        data = load_word_file(path)
        if not data:
            continue

        word_name = (data.get("word") or "").strip()
        if not word_name:
            print(f"❌  File {os.path.basename(path)} has no 'word' field — skipping.")
            continue

        topics_entries = data.get("topics", [])
        if not topics_entries:
            print(
                f"⚠️  No topics found for word '{word_name}' in {os.path.basename(path)} — skipping."
            )
            continue

        course_names = sorted(
            {entry["course"].strip() for entry in topics_entries if entry.get("course")}
        )
        if not course_names:
            print(
                f"⚠️  No valid course names for word '{word_name}' in {os.path.basename(path)} — skipping."
            )
            continue

        subject_ids = set()
        all_courses_resolved = True

        for course_name in course_names:
            course_id, subject_id = get_course_by_name(conn, course_name)
            if not course_id:
                print(
                    f"⚠️  Course '{course_name}' not found for word '{word_name}' "
                    f"in {os.path.basename(path)} — skipping this file."
                )
                all_courses_resolved = False
                break
            subject_ids.add(subject_id)

        if not all_courses_resolved:
            continue

        if not subject_ids:
            print(
                f"⚠️  No subjects resolved for word '{word_name}' "
                f"in {os.path.basename(path)} — skipping."
            )
            continue

        if len(subject_ids) > 1:
            print(
                f"❌  Word '{word_name}' in {os.path.basename(path)} references "
                f"courses from multiple subjects {sorted(subject_ids)} — skipping."
            )
            continue

        subject_id = next(iter(subject_ids))
        groups[(subject_id, word_name)].append(path)

    return groups


def find_synonym_file_for_group(
    word_name: str,
    version_paths: list[str],
    synonym_files: list[str],
) -> str | None:
    """
    Find a matching synonym file for this (word, group of version files).

    Heuristic:
      - synonym file must live in the same directory as one of the version files
      - its YAML 'word' field must match word_name (case-sensitive)

    If multiple candidates are found, the first one is used and a warning is printed.
    """
    version_dirs = {os.path.dirname(p) for p in version_paths}
    candidate: str | None = None

    for syn_path in synonym_files:
        syn_dir = os.path.dirname(syn_path)
        if syn_dir not in version_dirs:
            continue

        data = load_word_file(syn_path)
        if not data:
            continue

        yaml_word = (data.get("word") or "").strip()
        if yaml_word != word_name:
            continue

        if candidate is None:
            candidate = syn_path
        else:
            # Multiple synonym files for same (dir, word) – warn and keep the first
            print(
                f"⚠️  Multiple synonym files found for word '{word_name}' "
                f"in directory '{syn_dir}'. Using '{os.path.basename(candidate)}', "
                f"ignoring '{os.path.basename(syn_path)}'."
            )

    return candidate


def import_synonyms(conn, subject_id: int, word_id: int, path: str) -> None:
    data = load_word_file(path)
    if not data:
        print(f"⚠️  Could not load synonym file {path}")
        return

    yaml_word = (data.get("word") or "").strip()
    if yaml_word.lower() != get_word_name(conn, word_id).lower():
        print(
            f"❌ Synonym file '{os.path.basename(path)}' has word '{yaml_word}', "
            f"but DB word='{get_word_name(conn, word_id)}'. Skipping."
        )
        return

    syns = data.get("synonyms", [])
    if not isinstance(syns, list):
        print(f"❌ 'synonyms' must be a list in {os.path.basename(path)} — skipping.")
        return

    synonyms_new = {s.strip() for s in syns if s.strip()}
    if not synonyms_new:
        print(
            f"❌ Synonym file '{os.path.basename(path)}' contains no synonyms. "
            "Refusing to wipe existing synonyms."
        )
        return

    # Existing in DB
    rows = conn.execute(
        "SELECT synonym FROM Synonyms WHERE word_id = ?",
        (word_id,),
    ).fetchall()
    synonyms_old = {row["synonym"] for row in rows}

    to_remove = synonyms_old - synonyms_new
    to_add = synonyms_new - synonyms_old

    # Delete obsolete
    for syn in to_remove:
        conn.execute(
            "DELETE FROM Synonyms WHERE word_id = ? AND synonym = ?",
            (word_id, syn),
        )

    # Insert new
    for syn in to_add:
        conn.execute(
            "INSERT INTO Synonyms (word_id, synonym) VALUES (?, ?)",
            (word_id, syn),
        )

    if to_add or to_remove:
        conn.commit()

    print(
        f"✓ Synonyms updated for '{yaml_word}': "
        f"+{len(to_add)} added, -{len(to_remove)} removed, "
        f"{len(synonyms_new)} total."
    )


def import_word_group(
    conn,
    subject_id: int,
    word_name: str,
    version_paths: list[str],
    synonym_path: str | None = None,
) -> None:
    """
    Import all YAML files for a single (subject, word).

    Steps:
      0. Create/get Word entry
      1. Import synonyms if a synonym file exists (authoritative)
      2. Import all WordVersion YAMLs (strict level-set rules)
      3. Attach topics to each version
      4. Prune obsolete superset versions (rule 8)
    """

    # 0️⃣ Ensure Word exists (slug-stable)
    word_id = get_or_create_word(conn, subject_id, word_name)

    # 1️⃣ Import authoritative synonyms first (optional)
    if synonym_path:
        import_synonyms(conn, subject_id, word_id, synonym_path)

    # 2️⃣ Now process each WordVersion YAML file
    for path in version_paths:
        data = load_word_file(path)
        if not data:
            continue

        # -------------------------------
        # Validate declared levels
        # -------------------------------
        declared = [l.strip() for l in data.get("levels", []) if l and l.strip()]
        if not declared:
            print(
                f"⚠️  No levels specified for '{word_name}' "
                f"in {os.path.basename(path)} — skipping."
            )
            continue

        declared_levels = set(declared)

        # -------------------------------
        # Validate topics
        # -------------------------------
        topics_entries = data.get("topics", [])
        if not topics_entries:
            print(
                f"⚠️  No topics found for '{word_name}' "
                f"in {os.path.basename(path)} — skipping."
            )
            continue

        course_names = sorted(
            {entry["course"].strip() for entry in topics_entries if entry.get("course")}
        )

        if not course_names:
            print(
                f"⚠️  No valid course names for '{word_name}' "
                f"in {os.path.basename(path)} — skipping."
            )
            continue

        # -------------------------------
        # Infer required levels from courses
        # -------------------------------
        inferred_levels = get_levels_for_courses(conn, course_names)

        # Missing inferred -> error
        missing = inferred_levels - declared_levels
        if missing:
            print(f"❌ Level mismatch in '{word_name}' ({os.path.basename(path)})")
            print(f"   Declared: {sorted(declared_levels)}")
            print(f"   Implied:  {sorted(inferred_levels)}")
            print(f"   Missing:  {sorted(missing)}")
            print("   → Fix YAML.")
            continue

        # Extra declared -> warning (allowed)
        extra = declared_levels - inferred_levels
        if extra and inferred_levels:
            print(
                f"⚠️  '{word_name}' ({os.path.basename(path)}) declares extra levels "
                f"{sorted(extra)} not implied by its topics."
            )

        # -------------------------------
        # Resolve level IDs
        # -------------------------------
        level_ids = []
        for lvl in declared_levels:
            lvl_id = get_level_id(conn, lvl)
            if not lvl_id:
                print(
                    f"❌ Level '{lvl}' not found in DB for '{word_name}' "
                    f"({os.path.basename(path)})."
                )
                break
            level_ids.append(lvl_id)

        if len(level_ids) != len(declared_levels):
            continue  # failed to resolve all levels

        # -------------------------------
        # Extract meaning fields
        # -------------------------------
        definition = (data.get("definition") or "").strip()
        characteristics = clean_list(data.get("characteristics", []))
        examples = clean_list(data.get("examples", []))
        non_examples = clean_list(data.get("non_examples", []))

        # -------------------------------
        # Create or reuse WordVersion
        # -------------------------------
        try:
            word_version_id = get_or_create_word_version_for_levels(
                conn,
                word_id=word_id,
                level_ids=level_ids,
                definition=definition,
                characteristics=characteristics,
                examples=examples,
                non_examples=non_examples,
            )
        except ValueError as e:
            print(
                f"❌ Conflict importing '{word_name}' from {os.path.basename(path)}:\n"
                f"   {e}\n"
                f"   → Fix YAML or DB. Skipping this file."
            )
            continue

        # -------------------------------
        # Attach topics to this version
        # -------------------------------
        attached_any = False

        for entry in topics_entries:
            course_name = entry["course"].strip()
            codes = [str(c).strip() for c in entry.get("codes", []) if str(c).strip()]

            if not codes:
                print(
                    f"⚠️  No topic codes for course '{course_name}' "
                    f"in '{word_name}' ({os.path.basename(path)})."
                )
                continue

            course_id, subj_id = get_course_by_name(conn, course_name)
            if not course_id or subj_id != subject_id:
                print(
                    f"⚠️  Course '{course_name}' not valid for subject {subject_id} "
                    f"in file {os.path.basename(path)}."
                )
                continue

            for code in codes:
                topic_id = get_topic_id(conn, course_id, code)
                if not topic_id:
                    print(
                        f"⚠️  Topic '{code}' not found in course '{course_name}' "
                        f"for '{word_name}'."
                    )
                    continue

                link_word_to_topic(conn, word_version_id, topic_id)
                attached_any = True

        if not attached_any:
            print(
                f"⚠️  No topics successfully attached for '{word_name}' "
                f"in {os.path.basename(path)} (version still created)."
            )
        else:
            print(f"✓ Imported version for '{word_name}' from {os.path.basename(path)}")

    # 3️⃣ After all YAMLs for this word: prune supersets
    prune_supersets_for_word(conn, word_id)
    print(f"✓ Finished '{word_name}' (subject_id={subject_id})")
