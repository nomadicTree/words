import streamlit as st
import yaml
from dataclasses import dataclass
from app_lib.repositories import get_all_subjects_courses_topics

PAGE_TITLE = "Model Maker"
PAGE_PREFIX = "modelmaker_"  # Session state prefix for this page

st.set_page_config(page_title=f"FrayerStore | {PAGE_TITLE}", page_icon="🔎")
st.title(PAGE_TITLE)


@dataclass
class Topic:
    code: str
    course: str
    name: str


# ----------------------------
# Session State Initialization
# ----------------------------
def init_session_state():
    """Initialize session state variables for this page."""
    st.session_state.setdefault(f"{PAGE_PREFIX}selected_subjects", [])
    st.session_state.setdefault(f"{PAGE_PREFIX}selected_courses", [])
    st.session_state.setdefault(
        f"{PAGE_PREFIX}selected_topics", {}
    )  # course -> list of codes

    # Word input fields
    st.session_state.setdefault(f"{PAGE_PREFIX}word", "")
    st.session_state.setdefault(f"{PAGE_PREFIX}definition", "")
    st.session_state.setdefault(f"{PAGE_PREFIX}characteristics", "")
    st.session_state.setdefault(f"{PAGE_PREFIX}examples", "")
    st.session_state.setdefault(f"{PAGE_PREFIX}non_examples", "")


# ----------------------------
# Data Access Helpers
# ----------------------------
def get_available_subjects(data):
    return sorted({row["subject"] for row in data})


def get_available_courses(data, selected_subjects):
    return sorted(
        {row["course"] for row in data if row["subject"] in selected_subjects}
    )


def get_topics_by_course(data, selected_courses):
    """Return a dict: course -> list of Topic objects."""
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
def select_subjects(data):
    subjects = get_available_subjects(data)
    if not subjects:
        st.info("No subjects available.")
        st.stop()

    selected = st.multiselect(
        "Select subjects",
        options=subjects,
        default=st.session_state[f"{PAGE_PREFIX}selected_subjects"],
    )

    if not selected:
        st.info("Select at least one subject.")
        st.stop()

    st.session_state[f"{PAGE_PREFIX}selected_subjects"] = selected
    return selected


def select_courses(data, selected_subjects):
    courses = get_available_courses(data, selected_subjects)
    if not courses:
        st.info("No courses for the selected subjects.")
        st.stop()

    selected = st.multiselect(
        "Select courses",
        options=courses,
        default=st.session_state[f"{PAGE_PREFIX}selected_courses"],
    )

    if not selected:
        st.info("Select at least one course.")
        st.stop()

    st.session_state[f"{PAGE_PREFIX}selected_courses"] = selected
    return selected


def select_topics(course_topics):
    """Create one multiselect per course and store selections in session state."""
    st.session_state[f"{PAGE_PREFIX}selected_topics"] = {}
    for course, topics in course_topics.items():
        default_codes = st.session_state[f"{PAGE_PREFIX}selected_topics"].get(
            course, []
        )
        selected_codes = st.multiselect(
            f"Select topics for {course}",
            options=[t.code for t in topics],
            format_func=lambda code: next(
                f"{t.code} {t.name}" for t in topics if t.code == code
            ),
            default=default_codes,
        )
        st.session_state[f"{PAGE_PREFIX}selected_topics"][
            course
        ] = selected_codes


def build_yaml_topics():
    """Convert session state topic selections into YAML-ready structure."""
    return [
        {"course": course, "codes": sorted(codes)}
        for course, codes in st.session_state[
            f"{PAGE_PREFIX}selected_topics"
        ].items()
        if codes
    ]


def word_input_form(yaml_topics):
    """Render word input fields and display YAML output."""
    word = st.text_input(
        "Word *",
        value=st.session_state[f"{PAGE_PREFIX}word"],
        key=f"{PAGE_PREFIX}word",
    )
    definition = st.text_area(
        "Definition *",
        value=st.session_state[f"{PAGE_PREFIX}definition"],
        key=f"{PAGE_PREFIX}definition",
    )
    characteristics = st.text_area(
        "Characteristics (one per line)",
        value=st.session_state[f"{PAGE_PREFIX}characteristics"],
        key=f"{PAGE_PREFIX}characteristics",
    )
    examples = st.text_area(
        "Examples (one per line)",
        value=st.session_state[f"{PAGE_PREFIX}examples"],
        key=f"{PAGE_PREFIX}examples",
    )
    non_examples = st.text_area(
        "Non-Examples (one per line)",
        value=st.session_state[f"{PAGE_PREFIX}non_examples"],
        key=f"{PAGE_PREFIX}non_examples",
    )

    if st.button("Generate YAML"):
        if not word or not definition:
            st.error("Word and definition are required.")
        else:
            yaml_data = {
                "word": word,
                "definition": definition,
                "characteristics": [
                    c.strip() for c in characteristics.split("\n") if c.strip()
                ],
                "examples": [
                    e.strip() for e in examples.split("\n") if e.strip()
                ],
                "non-examples": [
                    ne.strip() for ne in non_examples.split("\n") if ne.strip()
                ],
                "topics": yaml_topics,
            }
            st.subheader("YAML Preview")
            st.code(yaml.dump(yaml_data, sort_keys=False, allow_unicode=True))


# ----------------------------
# Main
# ----------------------------
def main():
    data = get_all_subjects_courses_topics()
    init_session_state()

    selected_subjects = select_subjects(data)
    selected_courses = select_courses(data, selected_subjects)
    course_topics = get_topics_by_course(data, selected_courses)
    select_topics(course_topics)
    yaml_topics = build_yaml_topics()
    word_input_form(yaml_topics)


if __name__ == "__main__":
    main()
