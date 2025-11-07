import streamlit as st


def get_subjects(data):
    return sorted(set(row["subject"] for row in data))


def get_courses(data, subject):
    return sorted(
        set(row["course"] for row in data if row["subject"] == subject)
    )


def select_subject(data):
    if "selected_subject" not in st.session_state:
        st.session_state["selected_subject"] = None

    subjects = get_subjects(data)
    if not subjects:
        st.info("No subjects available.")
        st.stop()

    # Ensure previous value is valid
    if st.session_state["selected_subject"] not in subjects:
        st.session_state["selected_subject"] = subjects[0]

    selected = st.selectbox(
        "Select subject",
        subjects,
        index=subjects.index(st.session_state["selected_subject"]),
    )
    st.session_state["selected_subject"] = selected
    return selected


def select_course(data, subject):
    if "selected_course" not in st.session_state:
        st.session_state["selected_course"] = None

    courses = get_courses(data, subject)
    if not courses:
        st.info("No courses for this subject.")
        st.stop()

    # Ensure previous value is valid
    if st.session_state["selected_course"] not in courses:
        st.session_state["selected_course"] = courses[0]

    selected = st.selectbox(
        "Select course",
        courses,
        index=courses.index(st.session_state["selected_course"]),
    )
    st.session_state["selected_course"] = selected
    return selected
