import streamlit as st
from app.core.models.word_models import WordVersionChoice
from app.core.repositories.words_repo import (
    get_word_by_word_slug_and_subject_slug,
)
from app.ui.components.page_header import page_header
from app.ui.components.selection_helpers import select_one
from app.ui.components.frayer import render_frayer_model, render_related_words

PAGE_TITLE = "Model Viewer"


def safe_sync_qp(key: str, value: str | None) -> None:
    guard = f"_qp_guard_{key}"

    if st.session_state.get(guard):
        st.session_state[guard] = False
        return

    current = st.query_params.get(key)

    if value is None:
        if current is not None:
            st.query_params.pop(key, None)
            st.session_state[guard] = True
            st.rerun()
        return

    if current != value:
        st.query_params[key] = value
        st.session_state[guard] = True
        st.rerun()


# ---------------------------------------------------------------
# Load word based on slugs
# ---------------------------------------------------------------
def load_word_from_state():
    qp = st.query_params

    # ---------------------------------------------------
    # 1. QUERY PARAMS → SESSION (only if non-empty)
    # ---------------------------------------------------
    if "subject" in qp and qp["subject"]:
        st.session_state["view_subject"] = qp["subject"]

    if "word" in qp and qp["word"]:
        st.session_state["view_word"] = qp["word"]

    if "levels" in qp and qp["levels"]:
        st.session_state["view_levels"] = qp["levels"]

    # ---------------------------------------------------
    # 2. Now ensure session_state has the required fields
    # ---------------------------------------------------
    subject_slug = st.session_state.get("view_subject")
    word_slug = st.session_state.get("view_word")
    levels_slug = st.session_state.get("view_levels")

    if not subject_slug or not word_slug:
        st.error("No word selected.")
        st.stop()

    # ---------------------------------------------------
    # 3. SESSION → QUERY PARAMS (write but do NOT rerun)
    #    This keeps the URL in sync *after switch_page()*
    # ---------------------------------------------------
    if st.query_params.get("subject") != subject_slug:
        safe_sync_qp("subject", subject_slug)

    if st.query_params.get("word") != word_slug:
        safe_sync_qp("word", word_slug)

    if levels_slug:
        if st.query_params.get("levels") != levels_slug:
            safe_sync_qp("levels", levels_slug)
    else:
        if "levels" in st.query_params:
            safe_sync_qp("levels", None)

    # ---------------------------------------------------
    # 4. Lookup word by slug
    # ---------------------------------------------------

    word = get_word_by_word_slug_and_subject_slug(word_slug, subject_slug)
    if not word:
        st.error(f"Word not found: {word_slug} in {subject_slug}")
        st.stop()

    return word, levels_slug


def init_view_levels(choices: list["WordVersionChoice"], levels_slug: str | None):
    """
    Initialise view_levels if missing:
      1. URL slug (if valid for this word)
      2. global_levels (if valid for this word)
      3. first choice
    """
    if "view_levels" in st.session_state:
        return

    # 1. URL param
    if levels_slug and any(c.slug == levels_slug for c in choices):
        st.session_state["view_levels"] = levels_slug
        return

    # 2. global_levels
    global_level = st.session_state.get("global_levels")
    if global_level and any(c.slug == global_level for c in choices):
        st.session_state["view_levels"] = global_level
        return

    # 3. fallback
    st.session_state["view_levels"] = choices[0].slug


def sync_view_to_global_if_valid():
    """
    After rendering the widget:
    If the selected view-level is a *single* level (KS4/KS5),
    update global_levels to match.
    """
    view_level = st.session_state.get("view_levels")

    if view_level and "-" not in view_level:
        st.session_state["global_levels"] = view_level


def sync_global_to_view_if_valid(versions):
    """
    Before rendering the widget:
    If global and view differ, and global matches a version,
    set view = global.
    """
    global_level = st.session_state.get("global_levels")
    view_level = st.session_state.get("view_levels")

    if not global_level:
        return

    if view_level == global_level:
        return

    for v in versions:
        if v.slug == global_level:
            st.session_state["view_levels"] = global_level
            return


def choose_version_for_word(word, levels_slug):
    """
    Orchestrates:
      - init view_levels
      - sync global -> view
      - render selector (view-only)
      - sync view -> global
    Returns the chosen WordVersion.
    """
    choices = sorted([WordVersionChoice(v) for v in word.versions])

    # 1. initial view_level (from URL/global/first)
    init_view_levels(choices, levels_slug)

    # 2. global -> view (if compatible)
    sync_global_to_view_if_valid(choices)

    # 3. render selector (view namespace; ignores query params)
    selected_level = select_one(
        items=choices,
        key="levels",
        label="Select level",
        prefix="view",
    )

    # 4. persist chosen view_level + mirror in URL
    st.session_state["view_levels"] = selected_level.slug
    safe_sync_qp("levels", selected_level.slug)

    # 5. view -> global (if single-level)
    sync_view_to_global_if_valid()

    return selected_level.version


# ---------------------------------------------------------------
# Sidebar controls
# ---------------------------------------------------------------
def render_sidebar(word, levels_slug):
    """Return (version, display options)."""

    with st.sidebar:
        version = choose_version_for_word(word, levels_slug)
        # Update session state
        st.session_state["view_levels"] = version.level_set_slug
        sync_view_to_global_if_valid()

        with st.expander(label="Display Options", expanded=False):
            options = {
                "show_word": st.checkbox("Word", True),
                "show_definition": st.checkbox("Definition", True),
                "show_characteristics": st.checkbox("Characteristics", True),
                "show_examples": st.checkbox("Examples", True),
                "show_non_examples": st.checkbox("Non-examples", True),
                "show_topics": st.checkbox("Topics", True),
            }

        if word.related_words:
            with st.expander(label="Related Words", expanded=False):
                render_related_words(word.related_words)
        return version, options


# ---------------------------------------------------------------
# Main View
# ---------------------------------------------------------------
def main():
    word, levels_slug = load_word_from_state()

    page_header(PAGE_TITLE)

    version, view_opts = render_sidebar(word, levels_slug)

    render_frayer_model(
        version,
        show_word=view_opts["show_word"],
        related_words=word.related_words,
        show_topics=view_opts["show_topics"],
        show_definition=view_opts["show_definition"],
        show_characteristics=view_opts["show_characteristics"],
        show_examples=view_opts["show_examples"],
        show_non_examples=view_opts["show_non_examples"],
    )


if __name__ == "__main__":
    main()
