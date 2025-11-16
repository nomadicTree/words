import streamlit as st

from app.core.models.course_model import Course
from app.core.models.subject_model import Subject


def _sync_global_qp(key, value):
    guard_key = f"qp_sync_guard_{key}"

    # Skip if this run already handled the sync
    if st.session_state.get(guard_key):
        st.session_state[guard_key] = False
        return

    # Only update & rerun when necessary
    if st.query_params.get(key) != value:
        st.query_params[key] = value
        st.session_state[guard_key] = True
        st.rerun()


def select_one(
    items: list,
    key: str,
    label: str,
    prefix: str = "global",
    default_item=None,
):
    """
    Single-select version aligned with select_items():
    - prefix="global": URL only initializes once; then session dominates.
    - prefix="view": ignores query params entirely.
    - Stores slugs, not PKs.
    """
    if not items:
        st.warning(f"No options available for '{label}'.")
        return None

    slug_map = {item.slug: item for item in items}
    session_key = f"{prefix}_{key}"

    # --- STEP 1: qp only used on first load (global)
    qp_slug = None
    if prefix == "global":
        qp = st.query_params.get(key)
        qp_slug = qp[0] if isinstance(qp, list) else qp

    # --- STEP 2: initialise session
    if session_key not in st.session_state:
        if qp_slug in slug_map:
            st.session_state[session_key] = qp_slug
        elif default_item:
            st.session_state[session_key] = default_item.slug
        else:
            st.session_state[session_key] = items[0].slug

    selected_slug = st.session_state[session_key]

    # --- STEP 3: clean stale
    if selected_slug not in slug_map:
        selected_slug = default_item.slug if default_item else items[0].slug
        st.session_state[session_key] = selected_slug

    # --- STEP 4: sync session → query params FIRST
    if prefix == "global":
        _sync_global_qp(key, selected_slug)

    selected_obj = slug_map[selected_slug]

    # --- STEP 5: render widget
    selected_from_widget = st.selectbox(
        label,
        items,
        index=items.index(selected_obj),
        format_func=lambda i: i.label,
        key=f"{prefix}_{key}_widget",
    )

    new_slug = selected_from_widget.slug

    if new_slug != selected_slug:
        st.session_state[session_key] = new_slug
        if prefix == "global":
            _sync_global_qp(key, new_slug)

    return selected_from_widget


def select_course(available_courses: list[Course]):
    subjects = sorted({c.subject for c in available_courses})
    subject = select_one(items=subjects, key="subject", label="Subject")

    levels = sorted({c.level for c in available_courses if c.subject == subject})
    level = select_one(levels, "levels", "Select level")

    filtered_courses = [
        c for c in available_courses if c.subject == subject and c.level == level
    ]
    course = select_one(filtered_courses, "course", "Select course")
    return course


def select_many(
    items: list,
    key: str,
    label: str,
    prefix: str = "global",
):
    """
    Multi-select selector for Model Maker.
    - prefix="global" means: URL only initialises state; session is authoritative.
    - Stores slugs, not PKs.
    """

    if not items:
        return []

    slug_map = {item.slug: item for item in items}
    session_key = f"{prefix}_{key}"

    # GLOBAL selectors may use query params only on 1st load
    query_value = st.query_params.get(key) if prefix == "global" else None

    # Parse ?levels=a,b,c → ["a", "b", "c"]
    if isinstance(query_value, list):
        query_slugs = query_value
    elif isinstance(query_value, str):
        query_slugs = [x.strip() for x in query_value.split(",") if x.strip()]
    else:
        query_slugs = []

    original_slugs = st.session_state.get(session_key)

    # 1. INITIALISE session state
    if original_slugs is None:
        valid_slugs = [s for s in query_slugs if s in slug_map]
        st.session_state[session_key] = valid_slugs
        st.session_state[session_key] = []
        original_slugs = valid_slugs

    cleaned_slugs = [s for s in original_slugs if s in slug_map]
    st.session_state[session_key] = cleaned_slugs
    selected_slugs = st.session_state[session_key]

    # 2. Remove stale slugs
    selected_slugs = [s for s in selected_slugs if s in slug_map]
    st.session_state[session_key] = selected_slugs

    selected_objs = [slug_map[s] for s in selected_slugs]

    # 3. Render widget (session-state drives selection)
    selected_from_widget = st.multiselect(
        label,
        items,
        default=selected_objs,
        format_func=lambda i: i.label,
        key=f"{prefix}_{key}_widget",
    )

    # 4. Widget → session
    new_slugs = [i.slug for i in selected_from_widget]
    if set(new_slugs) != set(selected_slugs):
        st.session_state[session_key] = new_slugs

        # Update URL only for prefix='global'
        if prefix == "global":
            st.query_params[key] = ",".join(new_slugs)

    return selected_from_widget


def select_courses(available_courses: list[Course]) -> (Subject, list[Course]):
    # 1. Select subject
    subjects = sorted({c.subject for c in available_courses})
    selected_subject = select_one(
        items=subjects,
        key="subjects",
        label="Select subject",
        prefix="maker",
    )

    # 2. Select levels (global multi-select)
    levels = sorted(
        {c.level for c in available_courses if c.subject == selected_subject}
    )
    selected_levels = select_many(
        items=levels,
        key="levels",
        label="Select levels",
        prefix="maker",
    )

    # Convert selected Level objects to level_id set
    if selected_levels:
        selected_level_ids = {l.pk for l in selected_levels}
        courses_after_level = [
            c
            for c in available_courses
            if c.subject == selected_subject and c.level.pk in selected_level_ids
        ]
    else:
        # No levels selected → no courses selected
        courses_after_level = []

    # 3. Multi-select courses
    filtered_courses = sorted(courses_after_level)
    selected_courses = select_many(
        items=filtered_courses,
        key="courses",
        label="Select courses",
        prefix="maker",
    )

    return selected_subject, selected_courses
