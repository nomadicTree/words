from app_lib.db import get_db


def search_words(query):
    query = query
    db = get_db()
    q = "SELECT * FROM Word WHERE word LIKE ?"
    rows = db.execute(q, (f"%{query}%",)).fetchall()
    db.close()
    return rows


def get_subject_name(subject_id):
    db = get_db()
    q = "SELECT name FROM Subject WHERE id = ?"
    row = db.execute(q, (subject_id,)).fetchone()
    subject_name = row["name"] if row else None
    db.close()
    return subject_name


def get_topics_for_word(word_id):
    db = get_db()
    q = """
    SELECT
        Topic.code,
        Topic.name AS topic_name,
        Course.name AS course_name
    FROM Topic
    JOIN WordTopic ON Topic.id = WordTopic.topic_id
    JOIN Course ON Topic.course_id = Course.id
    WHERE WordTopic.word_id = ?
    ORDER BY Course.name, Topic.code
    """
    rows = db.execute(q, (word_id,)).fetchall()
    db.close()
    return rows


def get_all_subjects_courses_topics():
    db = get_db()
    q = """
    SELECT
    Subject.name as subject,
    Course.name as course,
    Topic.id as topic_id,
    Topic.code, Topic.name as topic_name
    FROM Subject
    JOIN Course ON Subject.id = Course.subject_id
    JOIN Topic ON Course.id = Topic.course_id
    ORDER BY Subject.name, Course.name, Topic.code
    """
    rows = db.execute(q).fetchall()
    db.close()
    return rows


def get_words_by_topic(topic_id):
    db = get_db()
    q = """
        SELECT Word.*
        FROM Word
        JOIN WordTopic ON Word.id = WordTopic.word_id
        WHERE WordTopic.topic_id = ?
    """
    rows = db.execute(q, (topic_id,)).fetchall()
    db.close()
    return rows
