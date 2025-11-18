import streamlit as st
from extra_streamlit_components import CookieManager
from app.core.models.course_model import Course
from app.core.models.subject_model import Subject

cookie_manager = CookieManager()


def _sync_global_qp(key, value):
    # Normalize comparison because st.query_params may return list
    current = st.query_params.get(key)
    if isinstance(current, list):
        current = current[0] if current else None

    # Only update when actually different
    if current != value:
        st.query_params[key] = value


def select_one(
    items: list,
    key: str,
    label: str,
    prefix: str = "global",
    default_item=None,
):
    if not items:
        st.warning(f"No options for '{label}'.")
        return None

    slug_map = {item.slug: item for item in items}
    session_key = f"{prefix}_{key}"
    cookie_key = f"fs_{prefix}_{key}"
    # --- STEP 1: initialise from COOKIE (first load only)
    if session_key not in st.session_state:
        saved = cookie_manager.get(cookie_key)

        if saved in slug_map:
            st.session_state[session_key] = saved
        elif default_item:
            st.session_state[session_key] = default_item.slug
        else:
            st.session_state[session_key] = items[0].slug

        # Write cookie on first load
        cookie_manager.set(
            cookie_key,
            st.session_state[session_key],
            key=f"{cookie_key}_set_init",
        )
        st.rerun()
    selected_slug = st.session_state[session_key]

    # --- STEP 2: stale cleanup
    if selected_slug not in slug_map:
        selected_slug = default_item.slug if default_item else items[0].slug
        st.session_state[session_key] = selected_slug

        cookie_manager.set(
            cookie_key,
            selected_slug,
            key=f"{cookie_key}_set_stale",
        )

    selected_obj = slug_map[selected_slug]

    # --- STEP 3: widget
    selected_from_widget = st.selectbox(
        label,
        items,
        index=items.index(selected_obj),
        format_func=lambda i: i.label,
        key=f"{prefix}_{key}_widget",
    )

    new_slug = selected_from_widget.slug

    # --- STEP 4: widget → session → cookie
    if new_slug != selected_slug:
        st.session_state[session_key] = new_slug

        cookie_manager.set(
            cookie_key,
            new_slug,
            key=f"{cookie_key}_set_widget",
        )

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


def select_many(items, key, label, prefix="global"):
    if not items:
        return []

    slug_map = {item.slug: item for item in items}
    session_key = f"{prefix}_{key}"
    cookie_key = f"fs_{prefix}_{key}"

    # --- STEP 1: initialise from COOKIE (first load only)
    if session_key not in st.session_state:
        saved_csv = cookie_manager.get(cookie_key)

        if saved_csv:
            saved_slugs = [s.strip() for s in saved_csv.split(",") if s.strip()]
            valid = [s for s in saved_slugs if s in slug_map]
            st.session_state[session_key] = valid
        else:
            st.session_state[session_key] = []

        # Write cookie on first load
        cookie_manager.set(
            cookie_key,
            ",".join(st.session_state[session_key]),
            key=f"{cookie_key}_set_init",
        )
        st.rerun()
    # --- STEP 2: stale cleanup
    selected_slugs = [s for s in st.session_state[session_key] if s in slug_map]
    st.session_state[session_key] = selected_slugs

    cookie_manager.set(
        cookie_key,
        ",".join(selected_slugs),
        key=f"{cookie_key}_set_stale",
    )

    selected_objs = [slug_map[s] for s in selected_slugs]

    # --- STEP 3: widget
    selected_from_widget = st.multiselect(
        label,
        items,
        default=selected_objs,
        format_func=lambda i: i.label,
        key=f"{prefix}_{key}_widget",
    )

    # --- STEP 4: widget → session → cookie
    new_slugs = [i.slug for i in selected_from_widget]
    if set(new_slugs) != set(selected_slugs):
        st.session_state[session_key] = new_slugs

        cookie_manager.set(
            cookie_key,
            ",".join(new_slugs),
            key=f"{cookie_key}_set_widget",
        )

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
