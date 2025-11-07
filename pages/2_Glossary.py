import streamlit as st
from app_lib.models import Word
from app_lib.repositories import (
    get_all_subjects_courses_topics,
    get_words_by_topic,
)
from app_lib.selection_helpers import select_subject, select_course


def get_words_for_course(data, subject, course):
    all_words = []
    all_words_set = set()
    for row in data:
        if row["subject"] == subject and row["course"] == course:
            topic_id = row["topic_id"]
            for w in get_words_by_topic(topic_id) or []:
                if w["word"] not in all_words_set:
                    all_words_set.add(w["word"])
                    all_words.append(Word(w))
    if not all_words:
        st.info("No words available for this course.")
        st.stop()
    return sorted(all_words, key=lambda w: w.word.lower())


def display_words(words):
    for w in words:
        with st.expander(w.word, expanded=False):
            w.display_frayer(show_topics=True)


# ----------------------------
# Main page logic
# ----------------------------
def main():
    PAGE_TITLE = "Glossary"
    st.set_page_config(
        page_title=f"FrayerStore | {PAGE_TITLE}", page_icon="🔎"
    )
    st.title(PAGE_TITLE)

    data = get_all_subjects_courses_topics()
    subject = select_subject(data)
    course = select_course(data, subject)
    words = get_words_for_course(data, subject, course)
    display_words(words)


if __name__ == "__main__":
    main()
