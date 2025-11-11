import streamlit as st

from app.components.common import page_header
from app.components.selection_helpers import select_course, select_subject
from app.core.components.frayer import render_frayer_model
from app.core.models.word_models import Word
from app.core.respositories.topics_repo import (
    get_all_subjects_courses_topics,
    get_words_for_course as fetch_words_for_course,
)

PAGE_TITLE = "Course Glossary"

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


def load_words_for_course(data, subject, course):
    matching_rows = [
        row for row in data if row["subject"] == subject and row["course"] == course
    ]
    if not matching_rows:
        st.info("No topics available for this course.")
        st.stop()

    course_id = matching_rows[0]["course_id"]
    words = fetch_words_for_course(course_id)
    if not words:
        st.info("No words available for this course.")
        st.stop()

    return words


def display_words(words: list[Word]):
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
                    show_topics=True,
                )
                if index < len(word.versions) - 1:
                    st.divider()


def main():
    page_header(PAGE_TITLE)

    with st.spinner("Loading..."):
        data = get_all_subjects_courses_topics()
    subject = select_subject(data)
    course = select_course(data, subject)
    st.divider()

    with st.spinner("Loading..."):
        words = load_words_for_course(data, subject, course)
    display_words(words)


if __name__ == "__main__":
    main()
