import os
import sqlite3
import json
import shutil
import glob
from datetime import datetime
import yaml

DB_FILE = "data/words.db"
SCHEMA_FILE = "data/schema.sql"
TAXONOMY_FILE = "data/yaml/taxonomy.yaml"
WORDS_DIR = "data/yaml/words"
BACKUP_DIR = "data/backups"


# -------------------------------
# Helper Functions
# -------------------------------
def get_or_create_subject(cursor, name):
    cursor.execute("SELECT id FROM Subject WHERE name=?", (name,))
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute("INSERT INTO Subject(name) VALUES(?)", (name,))
    return cursor.lastrowid


def get_or_create_course(cursor, name, subject_id):
    cursor.execute(
        "SELECT id FROM Course WHERE name=? AND subject_id=?",
        (name, subject_id),
    )
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO Course(name, subject_id) VALUES(?, ?)",
        (name, subject_id),
    )
    return cursor.lastrowid


def get_or_create_topic(cursor, code, name, course_id):
    cursor.execute(
        "SELECT id FROM Topic WHERE code=? AND course_id=?",
        (code, course_id),
    )
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO Topic(code, name, course_id) VALUES(?, ?, ?)",
        (code, name, course_id),
    )
    return cursor.lastrowid


def get_or_create_word(cursor, word_data, subject_id):
    cursor.execute(
        "SELECT id FROM Word WHERE word=? AND subject_id=?",
        (word_data["word"], subject_id),
    )
    res = cursor.fetchone()

    characteristics = json.dumps(word_data.get("characteristics", []))
    examples = json.dumps(word_data.get("examples", []))
    non_examples = json.dumps(word_data.get("non-examples", []))

    if res:
        word_id = res[0]
        cursor.execute(
            """
            UPDATE Word SET
                definition=?,
                characteristics=?,
                examples=?,
                non_examples=?
            WHERE id=?
            """,
            (
                word_data.get("definition"),
                characteristics,
                examples,
                non_examples,
                word_id,
            ),
        )
        return word_id
    else:
        cursor.execute(
            """
            INSERT INTO Word(word, subject_id, definition, characteristics, examples, non_examples)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                word_data["word"],
                subject_id,
                word_data.get("definition"),
                characteristics,
                examples,
                non_examples,
            ),
        )
        return cursor.lastrowid


def link_word_to_topic(cursor, word_id, topic_id):
    cursor.execute(
        "SELECT 1 FROM WordTopic WHERE word_id=? AND topic_id=?",
        (word_id, topic_id),
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO WordTopic(word_id, topic_id) VALUES(?, ?)",
            (word_id, topic_id),
        )


def create_db_if_not_exists(db_path, schema_path):
    if not os.path.exists(db_path):
        print(f"Database not found, creating new DB at {db_path}")
        conn = sqlite3.connect(db_path)
        with open(schema_path) as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()


def backup_db(db_path):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(db_path)
    backup_filename = f"{base_name}_{timestamp}.bak"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")


# -------------------------------
# Import Function
# -------------------------------
def import_words_folder(
    words_dir=WORDS_DIR,
    taxonomy_file=TAXONOMY_FILE,
    db_file=DB_FILE,
    schema_file=SCHEMA_FILE,
):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    words_path = os.path.join(script_dir, words_dir)
    taxonomy_path = os.path.join(script_dir, taxonomy_file)
    db_path = os.path.join(script_dir, db_file)
    schema_path = os.path.join(script_dir, schema_file)

    create_db_if_not_exists(db_path, schema_path)
    backup_db(db_path)

    with open(taxonomy_path) as f:
        taxonomy = yaml.safe_load(f)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    topic_lookup = {}

    for subj in taxonomy["subjects"]:
        subject_id = get_or_create_subject(cursor, subj["name"])
        for course in subj["courses"]:
            course_id = get_or_create_course(
                cursor, course["name"], subject_id
            )
            for topic in course["topics"]:
                topic_id = get_or_create_topic(
                    cursor, topic["code"], topic["name"], course_id
                )
                topic_lookup[(course["name"], topic["code"])] = (
                    topic_id,
                    subject_id,
                )

    # Process each word file
    for file_path in glob.glob(
        os.path.join(words_path, "**", "*.yaml"), recursive=True
    ):
        print(f"Importing word from {file_path}")
        with open(file_path) as f:
            word_data = yaml.safe_load(f)

        for topic_ref in word_data.get("topics", []):
            course = topic_ref["course"]
            for code in topic_ref["codes"]:
                if (course, code) in topic_lookup:
                    topic_id, subject_id = topic_lookup[(course, code)]
                    word_id = get_or_create_word(cursor, word_data, subject_id)
                    link_word_to_topic(cursor, word_id, topic_id)

    conn.commit()
    conn.close()
    print("Word import complete.")


# -------------------------------
# Run import if main
# -------------------------------
if __name__ == "__main__":
    import_words_folder()
