import streamlit as st
from dataclasses import dataclass
from collections import defaultdict
from app_lib.repositories import get_all_subjects_courses_topics
import yaml

PAGE_TITLE = "Model Maker"


# ----------------------------
# Dataclass for topics
# ----------------------------
@dataclass(frozen=True)
class Topic:
    code: str
    course: str
    name: str


# ----------------------------
# Helper functions
# ----------------------------
def init_session_state():
    """Initialize session state for selections and word inputs."""
    if "selected_subjects" not in st.session_state:
        st.session_state.selected_subjects = []

    if "selected_courses" not in st.session_state:
        st.session_state.selected_courses = []

    if "selected_topics_by_course" not in st.session_state:
        st.session_state.selected_topics_by_course = defaultdict(list)

    for key in [
        "word",
        "definition",
        "characteristics",
        "examples",
        "non_examples",
    ]:
        if key not in st.session_state:
            st.session_state[key] = ""


def select_subjects(data):
    subjects_available = sorted(set(row["subject"] for row in data))
    if not subjects_available:
        st.info("No subjects available.")
        st.stop()

    selected_subjects = st.multiselect(
        "Select subjects",
        subjects_available,
        default=st.session_state.selected_subjects,
    )
    if not selected_subjects:
        st.info("Select at least one subject.")
        st.stop()

    st.session_state.selected_subjects = selected_subjects
    return selected_subjects


def select_courses(data, selected_subjects):
    courses_available = sorted(
        set(
            row["course"]
            for row in data
            if row["subject"] in selected_subjects
        )
    )
    if not courses_available:
        st.info("No courses available for the selected subjects.")
        st.stop()

    selected_courses = st.multiselect(
        "Select courses",
        courses_available,
        default=st.session_state.selected_courses,
    )
    if not selected_courses:
        st.info("Select at least one course.")
        st.stop()

    st.session_state.selected_courses = selected_courses
    return selected_courses


def select_topics(data, selected_courses):
    for course in selected_courses:
        topics_available = [
            Topic(row["code"], row["course"], row["topic_name"])
            for row in data
            if row["course"] == course
        ]

        topic_key_map = {
            f"{t.course}|{t.code}|{t.name}": t for t in topics_available
        }

        previous_keys = [
            f"{t.course}|{t.code}|{t.name}"
            for t in st.session_state.selected_topics_by_course.get(course, [])
        ]

        selected_keys = st.multiselect(
            f"Select topics for {course}",
            options=list(topic_key_map.keys()),
            default=previous_keys,
            format_func=lambda k: f"{topic_key_map[k].code}: {topic_key_map[k].name}",
            key=f"topics_{course}",
        )

        st.session_state.selected_topics_by_course[course] = [
            topic_key_map[k] for k in selected_keys
        ]

    # Build YAML-ready structure
    yaml_topics = [
        {"course": course, "codes": sorted([t.code for t in topics])}
        for course, topics in st.session_state.selected_topics_by_course.items()
        if topics
    ]
    return yaml_topics


def word_input():
    st.session_state.word = st.text_input(
        "Word *", value=st.session_state.word
    )
    st.session_state.definition = st.text_area(
        "Definition *", value=st.session_state.definition
    )
    st.session_state.characteristics = st.text_area(
        "Characteristics (one per line)",
        value=st.session_state.characteristics,
    )
    st.session_state.examples = st.text_area(
        "Examples (one per line)", value=st.session_state.examples
    )
    st.session_state.non_examples = st.text_area(
        "Non-Examples (one per line)", value=st.session_state.non_examples
    )


def generate_yaml(yaml_topics):
    save_btn = st.button("Generate YAML")
    if save_btn:
        if not st.session_state.word or not st.session_state.definition:
            st.error("Word and definition are required.")
        else:
            yaml_data = {
                "word": st.session_state.word,
                "definition": st.session_state.definition,
                "characteristics": [
                    c.strip()
                    for c in st.session_state.characteristics.split("\n")
                    if c.strip()
                ],
                "examples": [
                    e.strip()
                    for e in st.session_state.examples.split("\n")
                    if e.strip()
                ],
                "non-examples": [
                    ne.strip()
                    for ne in st.session_state.non_examples.split("\n")
                    if ne.strip()
                ],
                "topics": yaml_topics,
            }

            st.code(yaml.dump(yaml_data, sort_keys=False, allow_unicode=True))


def main():
    st.set_page_config(
        page_title=f"FrayerStore | {PAGE_TITLE}", page_icon="🔎"
    )
    st.title(PAGE_TITLE)
    st.write("Generate YAML for a new word.")

    init_session_state()

    data = get_all_subjects_courses_topics()

    selected_subjects = select_subjects(data)
    selected_courses = select_courses(data, selected_subjects)
    yaml_topics = select_topics(data, selected_courses)

    word_input()
    generate_yaml(yaml_topics)


if __name__ == "__main__":
    main()
