import os
import sqlite3
import yaml
import json

DB_FILE = "data/words.db"
YAML_FILE = "data/words.yaml"

# -------------------------------
# Helper functions for each table
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
        "INSERT INTO Course(name, subject_id) VALUES(?, ?)", (name, subject_id)
    )
    return cursor.lastrowid


def get_or_create_topic(cursor, code, name, course_id):
    cursor.execute(
        "SELECT id FROM Topic WHERE code=? AND course_id=?", (code, course_id)
    )
    res = cursor.fetchone()
    if res:
        return res[0]
    cursor.execute(
        "INSERT INTO Topic(code, name, course_id) VALUES(?, ?, ?)",
        (code, name, course_id),
    )
    return cursor.lastrowid


def get_or_create_word(cursor, word_data):
    cursor.execute("SELECT id FROM Word WHERE word=?", (word_data["word"],))
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
            INSERT INTO Word(word, definition, characteristics, examples, non_examples)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                word_data["word"],
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


# -------------------------------
# Main import function
# -------------------------------
def import_words_yaml(yaml_file=YAML_FILE, db_file=DB_FILE):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(script_dir, yaml_file)

    with open(yaml_path) as f:
        data = yaml.safe_load(f)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    # -----------------------------
    # Lookup dictionaries (for linking)
    # -----------------------------
    topic_lookup = {}

    # -----------------------------
    # Insert Subjects, Courses, Topics
    # -----------------------------
    for subj in data["subjects"]:
        subject_id = get_or_create_subject(cursor, subj["name"])
        for course in subj["courses"]:
            course_id = get_or_create_course(
                cursor, course["name"], subject_id
            )
            for topic in course["topics"]:
                topic_id = get_or_create_topic(
                    cursor, topic["code"], topic["name"], course_id
                )
                topic_lookup[(course["name"], topic["code"])] = topic_id

    # -----------------------------
    # Insert Words and link to topics
    # -----------------------------
    for word in data["words"]:
        word_id = get_or_create_word(cursor, word)

        for topic_ref in word.get("topics", []):
            course_name = topic_ref["course"]
            for code in topic_ref["codes"]:
                topic_id = topic_lookup.get((course_name, code))
                if topic_id:
                    link_word_to_topic(cursor, word_id, topic_id)

    conn.commit()
    conn.close()
    print("Import complete. All data updated successfully.")


# -------------------------------
# Run script
# -------------------------------
if __name__ == "__main__":
    import_words_yaml()
