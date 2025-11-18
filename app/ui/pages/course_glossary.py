import streamlit as st
import string
from app.ui.components.page_header import page_header
from app.core.repositories.courses_repo import get_courses
from app.ui.components.selection_helpers import select_course
from app.core.repositories.words_repo import get_word_versions_for_course
from app.ui.components.frayer import wordversion_expander

PAGE_TITLE = "Course Glossary"


def main():
    page_header(PAGE_TITLE)
    all_courses = get_courses()
    with st.sidebar:
        course = select_course(all_courses)
    if course is None:
        st.error("No course selected—this is unexpected!")
        st.stop()

    course_word_versions = get_word_versions_for_course(course)
    course_word_versions.sort()

    groups = {letter: [] for letter in string.ascii_uppercase}
    groups["#"] = []  # for everything non-alphabetic

    for wv in course_word_versions:
        first = wv.word[0].upper()
        key = first if first in groups else "#"
        groups[key].append(wv)

    for letter in string.ascii_uppercase:
        items = groups[letter]
        if not items:
            continue

        st.subheader(letter)

        for wv in items:
            wordversion_expander(wv)

    if groups["#"]:
        st.subheader("#")
        for wv in groups["#"]:
            wordversion_expander(wv)


if __name__ == "__main__":
    main()
