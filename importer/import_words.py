import os
from importer.db_utils import (
    db_connection,
    get_course_by_name,
    get_topic_id,
    get_or_create_word,
    get_or_create_word_version,
    get_or_create_level,
    link_word_to_topic,
    link_wordversion_to_level,
    get_level_id,
    get_or_create_word_version_for_levels,
    prune_superset_word_versions,
)
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


def import_single_word(conn, path):
    """Import a single YAML file as a word entry (multi-level version schema)."""
    data = load_word_file(path)
    if not data:
        return

    word_name = data["word"].strip()
    levels = [l.strip() for l in data.get("levels", []) if l.strip()]
    if not levels:
        print(f"⚠️  No levels specified for '{word_name}' — skipping.")
        return

    definition = (data.get("definition") or "").strip()
    characteristics = clean_list(data.get("characteristics", []))
    examples = clean_list(data.get("examples", []))
    non_examples = clean_list(data.get("non_examples", []))
    topics_entries = data.get("topics", [])

    if not topics_entries:
        print(f"⚠️  No topics found for word '{word_name}' — skipping.")
        return

    # ✅ Resolve level IDs (must already exist)
    level_ids = []
    for name in levels:
        level_id = get_level_id(conn, name)
        if not level_id:
            print(
                f"❌ Level '{name}' not found in database. Run import_levels first."
            )
            return
        level_ids.append(level_id)

    # Per-subject caches so we don't recreate words/versions
    word_ids_by_subject: dict[int, int] = {}
    version_ids_by_subject: dict[int, int] = {}

    for entry in topics_entries:
        course_name = entry["course"].strip()
        codes = [str(c).strip() for c in entry.get("codes", [])]
        if not codes:
            print(
                f"⚠️  No topic codes for course '{course_name}' in '{word_name}'."
            )
            continue

        course_id, subject_id = get_course_by_name(conn, course_name)
        if not course_id:
            print(
                f"⚠️  Course '{course_name}' not found for '{word_name}'. Skipping."
            )
            continue

        # 1️⃣ Get or create the Word for this subject
        if subject_id not in word_ids_by_subject:
            word_id = get_or_create_word(conn, subject_id, word_name)
            word_ids_by_subject[subject_id] = word_id

            # 2️⃣ For this subject, create/get a version for this level set
            word_version_id = get_or_create_word_version_for_levels(
                conn,
                word_id,
                level_ids,
                definition,
                characteristics,
                examples,
                non_examples,
            )
            version_ids_by_subject[subject_id] = word_version_id
        else:
            word_id = word_ids_by_subject[subject_id]
            word_version_id = version_ids_by_subject[subject_id]

        # 3️⃣ Link this version to the topics for this course
        for code in codes:
            topic_id = get_topic_id(conn, course_id, code)
            if not topic_id:
                print(
                    f"⚠️  Topic '{code}' not found in '{course_name}' for '{word_name}'."
                )
                continue
            link_word_to_topic(conn, word_version_id, topic_id)

    prune_superset_word_versions(conn, word_id)
    print(f"✓ Imported word '{word_name}' ({os.path.basename(path)})")


def import_words(subjects_root, db_path):
    """Recursively import all YAML word files under any 'words' directory."""
    word_files = find_word_files(subjects_root)
    if not word_files:
        print(
            f"⚠️  No word YAML files found under any 'words' directory in {subjects_root}."
        )
        return

    with db_connection(db_path) as conn:
        for path in word_files:
            import_single_word(conn, path)
