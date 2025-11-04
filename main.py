import streamlit as st
import sqlite3
import json

DB_FILE = "data/words.db"


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def search_words(query):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT w.id,
               w.word,
               w.definition,
               w.characteristics,
               w.examples,
               w.non_examples,
               
               -- Distinct courses
               (SELECT GROUP_CONCAT(course_name, ', ')
                FROM (
                    SELECT DISTINCT c.name AS course_name
                    FROM WordTopic wt
                    JOIN Topic t ON wt.topic_id = t.id
                    JOIN Course c ON t.course_id = c.id
                    WHERE wt.word_id = w.id
                    ORDER BY c.name
                )
               ) AS courses,
               
               -- Distinct topics in format: code: name (course), sorted by course then code
               (SELECT GROUP_CONCAT(topic_info, ', ')
                FROM (
                    SELECT DISTINCT t.code || ': ' || t.name || ' (' || c.name || ')' AS topic_info, c.name AS course_sort, t.code AS code_sort
                    FROM WordTopic wt
                    JOIN Topic t ON wt.topic_id = t.id
                    JOIN Course c ON t.course_id = c.id
                    WHERE wt.word_id = w.id
                    ORDER BY course_sort, code_sort
                )
               ) AS topics
               
        FROM Word w
        WHERE w.word LIKE ?
        """,
        (f"%{query}%",),
    )
    results = cursor.fetchall()
    conn.close()
    return results


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


def display_frayer_model(word_row):
    word = word_row["word"]
    st.subheader(word_row["word"])
    characteristics = json.loads(word_row["characteristics"])
    examples = json.loads(word_row["examples"])
    non_examples = json.loads(word_row["non_examples"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Definition:**\n{word_row['definition']}")
        st.markdown("**Characteristics:**")
        characteristics_html = f"""<ul style="margin:0; padding-left:20px;">
            {''.join(f'<li>{c}</li>' for c in characteristics)}
        </ul>"""
        st.markdown(characteristics_html, unsafe_allow_html=True)
    with col2:
        st.markdown("**Examples:**")
        examples_html = f"""<ul style="margin:0; padding-left:20px;">
            {''.join(f'<li>{e}</li>' for e in examples)}
        </ul>"""
        st.markdown(examples_html, unsafe_allow_html=True)
        st.markdown("**Non-Examples:**")
        non_examples_html = f"""<ul style="margin:0; padding-left:20px;">
            {''.join(f'<li>{n}</li>' for n in non_examples)}
        </ul>"""
        st.markdown(non_examples_html, unsafe_allow_html=True)


def display_search_results(results, query):
    if results:
        for w in results:
            courses = w["courses"]
            if courses:
                courses_list = courses.split(",")
                courses = ", ".join(courses_list)
            else:
                courses = ""
            with st.expander(f"{w['word']} ({courses})", expanded=False):
                display_frayer_model(w)
                st.divider()
                topics = w["topics"]
                if topics:
                    topics_list = topics.split(",")
                    st.markdown("**Topics:**")
                    topics_html = f"""<ul style="margin:0; padding-left:20px;">
                        {''.join(f'<li>{t}</li>' for t in topics_list)}
                        </ul>"""
                    st.markdown(topics_html, unsafe_allow_html=True)
    elif query:
        st.info("No results found.")


def main():

    st.title("Key words")

    tab1, tab2 = st.tabs(["Search", "Glossary"])
    with tab1:
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

    with tab2:
        data = get_all_subjects_courses_topics()
        subjects = sorted(set([row["subject"] for row in data]))

        # Initialize session state if not set
        if "selected_subject" not in st.session_state:
            st.session_state.selected_subject = (
                subjects[0] if subjects else None
            )

        subject = st.selectbox(
            "Select subject",
            subjects,
            index=subjects.index(st.session_state.selected_subject),
        )
        st.session_state.selected_subject = subject

        # Courses
        courses = sorted(
            set([row["course"] for row in data if row["subject"] == subject])
        )
        if (
            "selected_course" not in st.session_state
            or st.session_state.selected_course not in courses
        ):
            st.session_state.selected_course = courses[0] if courses else None

        course = st.selectbox(
            "Select course",
            courses,
            index=(
                courses.index(st.session_state.selected_course)
                if st.session_state.selected_course in courses
                else 0
            ),
        )
        st.session_state.selected_course = course

        # Topics
        topics = [
            (row["topic_id"], f"{row['code']}: {row['topic_name']}")
            for row in data
            if row["subject"] == subject and row["course"] == course
        ]

        if "selected_topic_id" not in st.session_state:
            st.session_state.selected_topic_id = (
                topics[0][0] if topics else None
            )

        topic_selection = st.selectbox(
            "Select topic",
            topics,
            index=(
                next(
                    (
                        i
                        for i, t in enumerate(topics)
                        if t[0] == st.session_state.selected_topic_id
                    ),
                    0,
                )
                if topics
                else 0
            ),
            format_func=lambda x: x[1],
        )
        st.session_state.selected_topic_id = topic_selection[0]

        if topic_selection:
            topic_id = topic_selection[0]
            words = get_words_by_topic(topic_id)
            if words:
                for w in words:
                    with st.expander(w["word"], expanded=False):
                        display_frayer_model(w)
            else:
                st.info("No words found for this topic.")


if __name__ == "__main__":
    main()
