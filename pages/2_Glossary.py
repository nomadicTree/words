import streamlit as st
from app_lib.models import Word
from app_lib.repositories import (
    get_all_subjects_courses_topics,
    get_words_by_topic,
)

st.title("Glossary")

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
# Collect all words for the course
# -----------------------------
all_words = []
all_words_set = set()
for row in data:
    if row["subject"] == subject and row["course"] == course:
        topic_id = row["topic_id"]
        for w in get_words_by_topic(topic_id) or []:
            if w["word"] not in all_words_set:  # use word string as key
                all_words_set.add(w["word"])
                all_words.append(Word(w))

if not all_words:
    st.info("No words available for this course.")
    st.stop()

all_words = sorted(all_words, key=lambda w: w.word.lower())

# -----------------------------
# Display all words
# -----------------------------
for w in all_words:
    with st.expander(w.word, expanded=False):
        w.display_frayer(show_topics=True)
