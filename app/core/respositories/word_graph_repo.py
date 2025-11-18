import pandas as pd
from app.core.db import get_db


def load_words_and_rels():
    conn = get_db()

    df_words = pd.read_sql_query(
        """
        SELECT
            w.id   AS word_id,
            w.word AS word,
            w.subject_id
        FROM Words w
        """,
        conn,
    )

    df_rels = pd.read_sql_query(
        "SELECT word_id1 AS a, word_id2 AS b FROM WordRelationships",
        conn,
    )
    return df_words, df_rels


def load_word_levels():
    conn = get_db()
    df = pd.read_sql_query(
        """
        SELECT wv.word_id, wvl.level_id
        FROM WordVersions wv
        JOIN WordVersionLevels wvl ON wvl.word_version_id = wv.id
        """,
        conn,
    )
    return df


def load_word_courses():
    conn = get_db()
    df = pd.read_sql_query(
        """
        SELECT wv.word_id, c.id AS course_id
        FROM WordVersions wv
        JOIN WordVersionContexts wvc ON wvc.word_version_id = wv.id
        JOIN Topics t ON t.id = wvc.topic_id
        JOIN Courses c ON c.id = t.course_id
        """,
        conn,
    )
    return df
