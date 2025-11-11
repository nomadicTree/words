import streamlit as st
from app_lib.models import Word
from app_lib.repositories import (
    get_all_subjects_courses_topics,
    get_words_by_topic,
)
from app_lib.selection_helpers import select_subject, select_course
from app_lib.utils import render_frayer, page_header

PAGE_TITLE = "Topic Glossary"


def get_topics_with_words(data, subject, course):
    topics_with_words = []
    for row in data:
        if row["subject"] == subject and row["course"] == course:
            topic_id = row["topic_id"]
            words = sorted(
                get_words_by_topic(topic_id), key=lambda w: w["word"].lower()
            )
            if words:  # Only include topics with words
                topics_with_words.append(
                    {
                        "id": topic_id,
                        "code": row["code"],
                        "label": row["topic_label"],
                        "words": words,
                    }
                )

    if not topics_with_words:
        st.info("No words for this course.")
        st.stop()

    return topics_with_words


def display_sidebar_navigation(topics):
    for topic in topics:
        st.sidebar.markdown(
            f"""
            <a href="#{topic['code']}" style="
                text-decoration: none;
                color: inherit;
                display: block;
                font-size: 0.875rem;
            ">
                {topic['label']}
            </a>
            """,
            unsafe_allow_html=True,
        )


def display_topics_and_words(topics):
    for topic in topics:
        st.markdown(f"<a id='{topic['code']}'></a>", unsafe_allow_html=True)
        st.subheader(topic["label"])
        for w in topic["words"]:
            word_obj = Word(w)
            with st.expander(word_obj.word, expanded=False):
                render_frayer(word_obj.as_dict())


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
