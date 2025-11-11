import streamlit as st

from app.components.common import page_header
from app.components.selection_helpers import select_course, select_subject
from app.core.components.frayer import render_frayer_model
from app.core.models.course_model import Course
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject
from app.core.models.topic_model import Topic
from app.core.models.word_models import Word
from app.core.respositories.topics_repo import (
    get_all_subjects_courses_topics,
    get_words_for_topic,
)

PAGE_TITLE = "Topic Glossary"


def build_topic(row: dict) -> Topic:
    subject = Subject(row["subject_id"], row["subject"])
    level = (
        Level(row["level_id"], row["level_name"], row["level_description"])
        if row["level_id"] is not None
        else None
    )
    course = Course(row["course_id"], row["course"], subject, level)
    return Topic(row["topic_id"], row["code"], row["topic_name"], course)


def get_topics_with_words(data, subject, course):
    topics_with_words: list[tuple[Topic, list[Word]]] = []
    for row in data:
        if row["subject"] != subject or row["course"] != course:
            continue

        topic = build_topic(row)
        words = get_words_for_topic(topic.topic_id)
        if words:
            topics_with_words.append((topic, words))

    if not topics_with_words:
        st.info("No words for this course.")
        st.stop()

    return topics_with_words


def display_sidebar_navigation(topics):
    for topic, _ in topics:
        st.sidebar.markdown(
            f"""
            <a href="#{topic.code}" style="
                text-decoration: none;
                color: inherit;
                display: block;
                font-size: 0.875rem;
            ">
                {topic.label}
            </a>
            """,
            unsafe_allow_html=True,
        )


def format_level_names(levels) -> str:
    names = [level.name for level in levels if level and level.name]
    names = list(dict.fromkeys(names))
    if not names:
        return "All levels"
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def display_topics_and_words(topics):
    for topic, words in topics:
        st.markdown(f"<a id='{topic.code}'></a>", unsafe_allow_html=True)
        st.subheader(topic.label)
        for word in words:
            with st.expander(word.word, expanded=False):
                for index, version in enumerate(word.versions):
                    st.caption(f"Levels: {format_level_names(version.levels)}")
                    render_frayer_model(
                        version,
                        word.word,
                        word_id=word.word_id,
                        show_word=False,
                        related_words=word.related_words,
                        show_topics=False,
                        show_related_words=False,
                    )
                    if index < len(word.versions) - 1:
                        st.divider()


# ----------------------------
# Main Page Logic
# ----------------------------
def main():
    page_header(PAGE_TITLE)

    with st.spinner("Loading..."):
        data = get_all_subjects_courses_topics()
    subject = select_subject(data)
    course = select_course(data, subject)
    st.divider()
    with st.spinner("Loading..."):
        topics_with_words = get_topics_with_words(data, subject, course)
    display_sidebar_navigation(topics_with_words)
    display_topics_and_words(topics_with_words)


if __name__ == "__main__":
    main()
