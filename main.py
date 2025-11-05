import streamlit as st
import sqlite3
import json

from models import Word

DB_FILE = "data/words.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def search_words(query):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch basic word info + subject
    cursor.execute(
        """
        SELECT w.id, w.word, w.definition, w.characteristics, w.examples, w.non_examples,
               s.name AS subject_name
        FROM Word w
        LEFT JOIN Subject s ON w.subject_id = s.id
        WHERE w.word LIKE ?
        """,
        (f"%{query}%",),
    )
    words = cursor.fetchall()

    word_results = []

    for w in words:
        word_id = w["id"]

        # Fetch distinct courses
        cursor.execute(
            """
            SELECT DISTINCT c.name AS course_name
            FROM WordTopic wt
            JOIN Topic t ON wt.topic_id = t.id
            JOIN Course c ON t.course_id = c.id
            WHERE wt.word_id = ?
            ORDER BY c.name
            """,
            (word_id,),
        )
        courses_list = [row["course_name"] for row in cursor.fetchall()]
        courses = "|| ".join(courses_list)

        # Fetch distinct topics, format: code: name (course)
        cursor.execute(
            """
            SELECT t.code || ': ' || t.name || ' (' || c.name || ')' AS topic_info
            FROM WordTopic wt
            JOIN Topic t ON wt.topic_id = t.id
            JOIN Course c ON t.course_id = c.id
            WHERE wt.word_id = ?
            ORDER BY c.name, t.code
            """,
            (word_id,),
        )
        topics_list = [row["topic_info"] for row in cursor.fetchall()]
        topics = "|| ".join(
            topics_list
        )  # use a separator that won't conflict with commas

        word_results.append(
            {
                "id": word_id,
                "word": w["word"],
                "definition": w["definition"],
                "characteristics": w["characteristics"],
                "examples": w["examples"],
                "non_examples": w["non_examples"],
                "subject_name": w["subject_name"],
                "courses": courses,
                "topics": topics,
            }
        )

    conn.close()
    return word_results


def get_words_by_topic(topic_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT w.*
        FROM Word w
        JOIN WordTopic wt ON w.id = wt.word_id
        WHERE wt.topic_id = ?
    """,
        (topic_id,),
    )
    results = cursor.fetchall()
    conn.close()
    return results


def get_all_subjects_courses_topics():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT s.name as subject, c.name as course, t.id as topic_id, t.code, t.name as topic_name
        FROM Subject s
        JOIN Course c ON s.id = c.subject_id
        JOIN Topic t ON c.id = t.course_id
        ORDER BY s.name, c.name, t.code
    """
    )
    results = cursor.fetchall()
    conn.close()
    return results


def display_multiple_results(results):
    # Group words by subject
    subjects_dict = {}
    for row in results:
        w = Word(row)
        subjects_dict.setdefault(w.subject_name, []).append(w)

    # Display results grouped by subject
    for subject_name, words in subjects_dict.items():
        st.subheader(subject_name)
        for w in words:
            with st.expander(f"{w.word}", expanded=False):
                w.display_frayer(include_subject_info=True, show_topics=True)


def display_search_results(results, query):
    if results:
        display_multiple_results(results)
    elif query:
        st.info("No results found.")


def apply_styles():
    css = """
    <style>
        .frayer-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        border: 2px solid #999;
        border-radius: 6px;
        overflow: hidden;
        margin-bottom: 1rem;
    }
    .frayer-cell {
        border: 1px solid #aaa;
        padding: 12px 16px;
        vertical-align: top;
    }
    .frayer-title {
        font-weight: bold;
        margin-bottom: 6px;
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def search():
    # Initialize session state for search
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

    # Search input
    query = st.text_input(
        "Search for a word",
        value=st.session_state.search_query,
        key="search_input",
    )

    # Perform search only if the query changed
    if query != st.session_state.search_query:
        st.session_state.search_query = query
        if query:
            st.session_state.search_results = search_words(query)
        else:
            st.session_state.search_results = []

    # Display results
    results = st.session_state.search_results
    display_search_results(results, query)


def glossary():
    data = get_all_subjects_courses_topics()
    subjects = sorted(set(row["subject"] for row in data))

    # Subject selectbox with session state key
    subject = st.selectbox("Select subject", subjects, key="selected_subject")

    # Courses based on current subject
    courses = sorted(
        set(row["course"] for row in data if row["subject"] == subject)
    )
    course = st.selectbox("Select course", courses, key="selected_course")

    # Topics based on current subject + course
    topics = [
        {
            "id": row["topic_id"],
            "label": f"{row['code']}: {row['topic_name']}",
        }
        for row in data
        if row["subject"] == subject and row["course"] == course
    ]

    topic_ids = [t["id"] for t in topics]
    topic_labels = {t["id"]: t["label"] for t in topics}

    topic_selection = st.selectbox(
        "Select topic",
        topic_ids,
        key="selected_topic_id",
        format_func=lambda tid: topic_labels.get(tid, ""),
    )

    # Display words
    if topic_selection is not None:
        topic_id = topic_selection  # already an int
        words = get_words_by_topic(topic_id)
        if words:
            for w in words:
                word_obj = Word(w)
                with st.expander(word_obj.word, expanded=False):
                    word_obj.display_frayer()
        else:
            st.info("No words found for this topic.")


def main():

    st.title("Frayer Dictionary")
    apply_styles()
    st.set_page_config(page_title="Frayer Dictionary")
    tab1, tab2 = st.tabs(["Search", "Glossary"])
    with tab1:
        search()
    with tab2:
        glossary()


if __name__ == "__main__":
    main()
