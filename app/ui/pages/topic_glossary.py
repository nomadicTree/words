import streamlit as st
from app.ui.components.page_header import page_header
from app.ui.components.selection_helpers import select_course
from app.core.respositories.courses_repo import get_courses
from app.core.respositories.topics_repo import get_topics_for_course
from app.core.respositories.words_repo import get_word_versions_for_topic
from app.ui.components.frayer import render_frayer_model
from app.ui.components.buttons import wordversion_details_button

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
            with st.expander(wv.word, expanded=False):
                render_frayer_model(wv)
                wordversion_details_button(wv, key_prefix=i)


if __name__ == "__main__":
    main()
