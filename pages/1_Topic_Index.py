import streamlit as st
from app_lib.models import Word
from app_lib.repositories import (
    get_all_subjects_courses_topics,
    get_words_by_topic,
)

st.title("Topic Index")

# -----------------------------
# Load data
# -----------------------------
data = get_all_subjects_courses_topics()

# -----------------------------
# Subjects
# -----------------------------
subjects = sorted(set(row["subject"] for row in data))
if not subjects:
    st.info("No subjects available.")
    st.stop()

subject = st.selectbox("Select subject", subjects)

# -----------------------------
# Courses
# -----------------------------
courses = sorted(
    set(row["course"] for row in data if row["subject"] == subject)
)
if not courses:
    st.info("No courses for this subject.")
    st.stop()

course = st.selectbox("Select course", courses)

# -----------------------------
# Topics with words
# -----------------------------
topics_with_words = []
for row in data:
    if row["subject"] == subject and row["course"] == course:
        topic_id = row["topic_id"]
        words = get_words_by_topic(topic_id)
        if words:  # only include topics with words
            topics_with_words.append(
                {
                    "id": topic_id,
                    "label": f"{row['code']}: {row['topic_name']}",
                    "words": words,
                }
            )

if not topics_with_words:
    st.info("No words for this course.")
    st.stop()

# -----------------------------
# Sidebar navigation links
# -----------------------------
for topic in topics_with_words:
    st.sidebar.markdown(
        f"- [{topic['label']}](#topic-{topic['id']})", unsafe_allow_html=True
    )

# -----------------------------
# Display topics and words
# -----------------------------
for topic in topics_with_words:
    topic_id = topic["id"]
    topic_label = topic["label"]

    # Anchor for navigation
    st.markdown(f"<a id='topic-{topic_id}'></a>", unsafe_allow_html=True)
    st.subheader(topic_label)

    for w in topic["words"]:
        word_obj = Word(w)
        with st.expander(word_obj.word, expanded=False):
            word_obj.display_frayer()
