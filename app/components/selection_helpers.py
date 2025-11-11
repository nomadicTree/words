import streamlit as st


def get_subjects(data):
    return sorted(set(row["subject"] for row in data))


def get_courses(data, subject):
    return sorted(
        set(row["course"] for row in data if row["subject"] == subject)
    )


def select_subject(data):
    subjects = get_subjects(data)
    if not subjects:
        st.info("No subjects available.")
    else:
        # Check query_params for a subject
        query_subject = st.query_params.get("subject", None)
        if query_subject and query_subject in subjects:
            st.session_state["selected_subject"] = query_subject

        # Check session_state for a subject
        if "selected_subject" not in st.session_state:
            st.session_state["selected_subject"] = None

        # Ensure session state's value is valid
        if st.session_state["selected_subject"] not in subjects:
            st.session_state["selected_subject"] = subjects[0]

        selected = st.selectbox(
            "Select subject",
            subjects,
            index=subjects.index(st.session_state["selected_subject"]),
        )
        st.session_state["selected_subject"] = selected

    # Update query_params to reflect the selected subject
    if query_subject != selected:
        st.query_params["subject"] = selected
        st.rerun()
    return st.session_state["selected_subject"]


def select_course(data, subject):
    courses = get_courses(data, subject)
    if not courses:
        st.info("No courses for this subject.")
    else:
        # Check query_params for a course
        query_course = st.query_params.get("course", None)
        if query_course and query_course in courses:
            st.session_state["selected_course"] = query_course
        elif "selected_course" not in st.session_state:
            st.session_state["selected_course"] = courses[0]

        selected = st.selectbox(
            "Select course",
            courses,
            index=courses.index(st.session_state["selected_course"]),
        )
        st.session_state["selected_course"] = selected

    # Update query_params to reflect the selected course
    if query_course != selected:
        st.query_params["course"] = selected
        st.rerun()
    return st.session_state["selected_course"]
