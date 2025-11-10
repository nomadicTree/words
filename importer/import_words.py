import os
from importer.db_utils import (
    db_connection,
    get_course_by_name,
    get_topic_id,
    get_or_create_word,
    get_or_create_word_version,
    link_word_to_topic,
)
from importer.yaml_utils import load_word_file, clean_list


def find_word_files(subjects_root):
    """Return a list of YAML files inside any 'words' directory."""
    word_files = []
    for root, _, files in os.walk(subjects_root):
        if os.path.basename(root) != "words":
            continue
        for fname in files:
            if fname.endswith(".yaml"):
                word_files.append(os.path.join(root, fname))
    return word_files


def import_single_word(conn, path):
    """Import a single YAML file as a word entry."""
    data = load_word_file(path)
    if not data:
        return

    word_name = data["word"].strip()
    synonyms = ", ".join(s.strip() for s in data.get("synonyms", []))
    definition = (data.get("definition") or "").strip()
    characteristics = clean_list(data.get("characteristics", []))
    examples = clean_list(data.get("examples", []))
    non_examples = clean_list(data.get("non_examples", []))

    topics_entries = data.get("topics", [])
    if not topics_entries:
        print(f"⚠️  No topics found for word '{word_name}' — skipping.")
        return

    word_ids_by_subject = {}

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

        if subject_id not in word_ids_by_subject:
            word_id = get_or_create_word(conn, subject_id, word_name, synonyms)
            word_ids_by_subject[subject_id] = word_id
        else:
            word_id = word_ids_by_subject[subject_id]

        word_version_id = get_or_create_word_version(
            conn,
            word_id,
            course_id,
            definition,
            characteristics,
            examples,
            non_examples,
        )

        for code in codes:
            topic_id = get_topic_id(conn, course_id, code)
            if not topic_id:
                print(
                    f"⚠️  Topic '{code}' not found in '{course_name}' for '{word_name}'."
                )
                continue
            link_word_to_topic(conn, word_version_id, topic_id)

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
