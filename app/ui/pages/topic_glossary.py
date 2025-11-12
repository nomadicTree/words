import streamlit as st
from app.ui.components.page_header import page_header
from app.ui.components.selection_helpers import select_item
from app.core.respositories.courses_repo import get_courses
from app.core.respositories.topics_repo import get_topics_for_course
from app.core.respositories.words_repo import get_word_versions_for_topic
from app.core.models.course_model import Course
from app.ui.components.frayer import render_frayer_model

PAGE_TITLE = "Topic Glossary"


def select_course(available_courses: list[Course]):
    subjects = sorted({c.subject for c in available_courses}, key=lambda s: s.name)
    subject = select_item(subjects, "subject", "Select subject")

    levels = sorted(
        {c.level for c in available_courses if c.subject == subject},
        key=lambda l: l.name,
    )
    level = select_item(levels, "level", "Select level")

    filtered_courses = [
        c for c in available_courses if c.subject == subject and c.level == level
    ]
    course = select_item(filtered_courses, "course", "Select course")
    return course


def main():
    page_header(PAGE_TITLE)
    all_courses = get_courses()
    course = select_course(all_courses)
    topics = get_topics_for_course(course, has_words=True)
    for topic in topics:
        st.subheader(topic.label)
        word_versions = get_word_versions_for_topic(topic)
        word_versions.sort()
        for wv in word_versions:
            with st.expander(wv.word, expanded=False):
                render_frayer_model(wv)
                st.divider()
                st.link_button("View full details", wv.build_url(level=wv.level_slug()))


if __name__ == "__main__":
    main()
