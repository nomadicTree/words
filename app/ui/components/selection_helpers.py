import streamlit as st

from app.core.models.course_model import Course


def select_item(items: list, key: str, label: str):
    """
    Generic selection helper that:
    - stores only PKs in session_state (safe across reloads)
    - rebuilds selected object from PK each run
    - handles stale PKs (when filters change after reload)
    - keeps query params in sync with the selection
    """

    if not items:
        st.warning(f"No options available for {label}.")
        return None

    # Build lookup maps
    pk_map = {item.pk: item for item in items}
    name_map = {item.name: item for item in items}

    session_key = f"selected_{key}_pk"
    query_value = st.query_params.get(key)

    # --- Sync query -> session ---
    if query_value and query_value in name_map:
        # URL value points to a valid item
        st.session_state[session_key] = name_map[query_value].pk

    elif session_key not in st.session_state:
        # No session yet -> initialise with the first item
        st.session_state[session_key] = items[0].pk

    # Resolve the PK we want to select
    selected_pk = st.session_state[session_key]

    # --- Handle stale PKs (hot reload or parent filter changed) ---
    if selected_pk not in pk_map:
        # If the previously selected item no longer exists under the new filter:
        st.session_state[session_key] = items[0].pk
        selected_obj = items[0]
    else:
        selected_obj = pk_map[selected_pk]

    # --- Render the selectbox ---
    selected_from_widget = st.selectbox(
        label,
        items,
        index=items.index(selected_obj),
        format_func=lambda i: i.name,
    )

    # --- Sync session -> query ---
    if query_value != selected_from_widget.name:
        st.session_state[session_key] = selected_from_widget.pk
        st.query_params[key] = selected_from_widget.name
        st.rerun()

    return selected_from_widget


def select_course(available_courses: list[Course]):
    subjects = sorted({c.subject for c in available_courses}, key=lambda s: s.name)
    subject = select_item(subjects, "subject", "Select subject")

    levels = sorted(
        {c.level for c in available_courses if c.subject == subject},
        key=lambda l: l.name,
    )
    level = select_item(levels, "level", "Select level")

    filtered_courses = [
        c for c in available_courses if c.subject == subject and c.level == level
    ]
    course = select_item(filtered_courses, "course", "Select course")
    return course


def select_items(items: list, key: str, label: str):
    """
    Multi-select version of select_item:
    - stores only PKs in session_state (list of PKs)
    - syncs to/from query params (comma-separated names)
    - handles stale/removal cases
    - returns list of selected objects
    """

    if not items:
        st.warning(f"No options available for {label}.")
        return []

    # Build lookup maps
    pk_map = {item.pk: item for item in items}
    name_map = {item.name: item for item in items}

    session_key = f"selected_{key}_pks"
    query_value = st.query_params.get(key)

    # Parse query string into a list of names
    if query_value:
        if isinstance(query_value, list):
            query_names = query_value
        else:
            query_names = query_value.split(",")
    else:
        query_names = []

    # --- Sync query -> session ---
    if query_names:
        valid_items = [name_map[n] for n in query_names if n in name_map]
        st.session_state[session_key] = [i.pk for i in valid_items]
    elif session_key not in st.session_state:
        st.session_state[session_key] = []

    selected_pks = st.session_state[session_key]

    # --- Handle stale PKs (removed or filtered out) ---
    selected_pks = [pk for pk in selected_pks if pk in pk_map]
    st.session_state[session_key] = selected_pks
    selected_objs = [pk_map[pk] for pk in selected_pks]

    # --- Render multi-select widget ---
    selected_from_widget = st.multiselect(
        label,
        items,
        default=selected_objs,
        format_func=lambda i: i.name,
    )

    # --- Sync widget -> session ---
    new_pks = [i.pk for i in selected_from_widget]
    if set(new_pks) != set(selected_pks):
        st.session_state[session_key] = new_pks
        st.query_params[key] = ",".join([i.name for i in selected_from_widget])
        st.rerun()

    return selected_from_widget


def select_courses(available_courses: list[Course]):
    # --- 1. Multi-select subjects ---
    all_subjects = sorted({c.subject for c in available_courses}, key=lambda s: s.name)
    selected_subjects = select_items(all_subjects, "subjects", "Select subjects")

    # If none selected, treat as "all subjects"
    if selected_subjects:
        subject_ids = {s.subject_id for s in selected_subjects}
        courses_after_subject = [
            c for c in available_courses if c.subject.subject_id in subject_ids
        ]
    else:
        courses_after_subject = available_courses

    # --- 2. Multi-select levels ---
    all_levels = sorted({c.level for c in courses_after_subject}, key=lambda l: l.name)
    selected_levels = select_items(all_levels, "levels", "Select levels")

    # If none selected, treat as "all levels"
    if selected_levels:
        level_ids = {l.level_id for l in selected_levels}
        courses_after_level = [
            c for c in courses_after_subject if c.level.level_id in level_ids
        ]
    else:
        courses_after_level = courses_after_subject

    # --- 3. Multi-select courses ---
    filtered_and_sorted = sorted(courses_after_level, key=lambda c: c.name)
    selected_courses = select_items(filtered_and_sorted, "courses", "Select courses")

    return selected_courses
