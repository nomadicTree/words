import streamlit as st
import yaml
from dataclasses import dataclass
from app_lib.repositories import get_all_subjects_courses_topics
from app_lib.utils import render_frayer, safe_snake_case_filename, apply_styles


@dataclass
class Topic:
    code: str
    course: str
    name: str


# ----------------------------
# Data Helpers
# ----------------------------
def get_available_subjects(data):
    return sorted({row["subject"] for row in data})


def get_available_courses(data, selected_subjects):
    return sorted(
        {row["course"] for row in data if row["subject"] in selected_subjects}
    )


def get_topics_by_course(data, selected_courses):
    course_topics = {}
    for row in data:
        if row["course"] in selected_courses:
            course_topics.setdefault(row["course"], []).append(
                Topic(
                    code=row["code"],
                    course=row["course"],
                    name=row["topic_name"],
                )
            )
    return course_topics


# ----------------------------
# UI Components
# ----------------------------
def select_subject(data):
    subjects_available = get_available_subjects(data)
    if not subjects_available:
        st.info("No subjects available.")
        st.stop()
    selected_subject = st.selectbox("Select subject", subjects_available)
    return selected_subject


def select_courses(data, selected_subjects):
    courses_available = get_available_courses(data, selected_subjects)
    if not courses_available:
        st.info("No courses for the selected subjects.")
        st.stop()
    selected_courses = st.multiselect("Select courses", courses_available)
    return selected_courses


def select_topics(course_topics):
    """Return a dict mapping course -> list of selected topic codes"""
    selected_topics = {}
    for course, topics in course_topics.items():
        codes = st.multiselect(
            f"Select topics for {course}",
            options=[t.code for t in topics],
            format_func=lambda code: next(
                f"{t.code} {t.name}" for t in topics if t.code == code
            ),
        )
        selected_topics[course] = codes
    return selected_topics


def word_input_form():
    """Render input fields for word data and display YAML output."""

    word = st.text_input("Word")
    definition = st.text_area("Definition")
    characteristics = st.text_area("Characteristics (one per line)")
    examples = st.text_area("Examples (one per line)")
    non_examples = st.text_area("Non-examples (one per line)")
    yaml_data = {
        "word": word.strip(),
        "definition": definition.strip(),
        "characteristics": [
            c.strip() for c in characteristics.split("\n") if c.strip()
        ],
        "examples": [e.strip() for e in examples.split("\n") if e.strip()],
        "non_examples": [
            ne.strip() for ne in non_examples.split("\n") if ne.strip()
        ],
    }
    return yaml_data


# ----------------------------
# Main
# ----------------------------
def main():
    PAGE_TITLE = "Model Maker"
    st.title(PAGE_TITLE)
    apply_styles()
    data = get_all_subjects_courses_topics()

    selected_subjects = select_subject(data)
    selected_courses = select_courses(data, selected_subjects)
    course_topics = get_topics_by_course(data, selected_courses)
    st.divider()

    # Build YAML-ready topics

    word_data = word_input_form()

    selected_topics = select_topics(course_topics)
    yaml_topics = [
        {"course": course, "codes": sorted(codes)}
        for course, codes in selected_topics.items()
        if codes
    ]
    word_data["topics"] = yaml_topics

    st.subheader("YAML preview")
    word_yaml = yaml.dump(
        word_data,
        sort_keys=False,
        allow_unicode=True,
    )
    st.code(
        word_yaml,
        wrap_lines=True,
        language="yaml",
    )
    st.download_button(
        "Download YAML",
        word_yaml,
        file_name=safe_snake_case_filename(word_data["word"], "yaml"),
    )

    st.subheader("Frayer preview")
    word_data["id"] = 0  # Dummy ID for preview
    with st.expander(word_data["word"], expanded=True):
        render_frayer(
            word_data,
            show_link=False,
            show_subject=False,
            show_topics=False,
        )


if __name__ == "__main__":
    main()
