import streamlit as st
from app.ui.components.page_header import page_header
from app.core.respositories.courses_repo import get_courses
from app.ui.components.selection_helpers import select_course
from app.core.respositories.words_repo import get_word_versions_for_course
from app.ui.components.frayer import render_frayer_model
from app.ui.components.buttons import wordversion_details_button

PAGE_TITLE = "Course Glossary"


def main():
    all_courses = get_courses()
    with st.sidebar:
        course = select_course(all_courses)

    page_header(PAGE_TITLE)

    course_word_versions = get_word_versions_for_course(course)
    course_word_versions.sort()

    for wv in course_word_versions:
        with st.expander(wv.word, expanded=False):
            render_frayer_model(wv)
            wordversion_details_button(wv)


if __name__ == "__main__":
    main()
