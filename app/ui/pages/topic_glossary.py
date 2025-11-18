import streamlit as st
from app.ui.components.page_header import page_header
from app.ui.components.selection_helpers import select_course
from app.core.repositories.courses_repo import get_courses
from app.core.repositories.topics_repo import get_topics_for_course
from app.core.repositories.words_repo import get_word_versions_for_topic
from app.ui.components.frayer import wordversion_expander

PAGE_TITLE = "Topic Glossary"


def main():
    all_courses = get_courses()
    with st.sidebar:
        course = select_course(all_courses)
    page_header(PAGE_TITLE)
    topics = get_topics_for_course(course, only_with_words=True)
    for i, topic in enumerate(topics):
        st.subheader(topic.label)
        topic_word_versions = get_word_versions_for_topic(topic)
        topic_word_versions.sort()
        for wv in topic_word_versions:
            wordversion_expander(wv, i)


if __name__ == "__main__":
    main()
