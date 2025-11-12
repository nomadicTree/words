import re
from urllib.parse import quote_plus
import streamlit as st
from app.core.models.word_models import (
    WordVersion,
)  # adjust import paths as needed
from app.core.respositories.words_repo import get_word_full
from app.ui.components.page_header import page_header
from app.ui.components.frayer import (
    render_frayer_model,
)  # your rendering function


# --------------------------------------------------------------------
# Query parameter utilities
# --------------------------------------------------------------------
def get_word_from_query_params():
    """Extract the 'id' parameter from the query string and return the Word object."""
    id_param = st.query_params.get("id")

    if id_param is None:
        st.info("No id given in URL. Are you here accidentally?")
        return None

    try:
        word_id = int(id_param)
    except ValueError:
        st.error("Invalid id in URL")
        st.stop()

    word = get_word_full(word_id)
    if word is None:
        st.error(f"No word found with id {word_id}")
        st.stop()

    return word


def get_query_param_single(name: str) -> str | None:
    """Safely extract a single value from Streamlit's query parameters."""
    value = st.query_params.get(name)
    if isinstance(value, list):
        return value[0]
    return value


# --------------------------------------------------------------------
# Label + URL helpers
# --------------------------------------------------------------------
def label_for_version(v: WordVersion) -> str:
    """Return a human-readable label for a WordVersion’s levels."""
    levels = [l.name for l in v.levels]
    if not levels:
        return "All levels"
    if len(levels) == 1:
        return levels[0]
    if len(levels) == 2:
        return " and ".join(levels)
    return ", ".join(levels[:-1]) + f", and {levels[-1]}"


def slugify_label(label: str) -> str:
    """Convert a human-readable label into a clean, URL-safe slug."""
    slug = re.sub(r"[ ,]+and[ ,]+", "-", label.lower())
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return quote_plus(slug)


# --------------------------------------------------------------------
# Sidebar rendering
# --------------------------------------------------------------------
def render_sidebar(word) -> dict:
    """Render sidebar controls and return user display preferences."""
    with st.sidebar:
        st.header("Display Options")

        options = {
            "show_word_title": st.checkbox("Word", value=True, key="show_word"),
            "show_definition": st.checkbox(
                "Definition", value=True, key="show_definition"
            ),
            "show_characteristics": st.checkbox(
                "Characteristics", value=True, key="show_characteristics"
            ),
            "show_examples": st.checkbox("Examples", value=True, key="show_examples"),
            "show_non_examples": st.checkbox(
                "Non-examples", value=True, key="show_non_examples"
            ),
            # placeholders; will fill below
            "show_related_words": False,
            "show_topics": False,
        }

        # --- Related words BEFORE Topics ---
        if word.related_words:
            options["show_related_words"] = st.checkbox(
                "Related words",
                value=True,
                key="show_related_words",
            )

        options["show_topics"] = st.checkbox(
            "Topics",
            value=True,
            key="show_topics",
        )

        return options


# --------------------------------------------------------------------
# Main view
# --------------------------------------------------------------------
def main():
    page_header()
    word = get_word_from_query_params()
    if word is None:
        st.stop()

    opts = render_sidebar(word)

    # --- word header ---
    st.header(word.word if opts["show_word_title"] else "❓")
    st.markdown(f"Subject: **{word.subject.name}**")

    # --- determine selected key stage (from query param) ---
    query_ks = get_query_param_single("ks")

    tab_labels = [label_for_version(v) for v in word.versions]
    tab_slugs = [slugify_label(lbl) for lbl in tab_labels]

    default_index = 0
    if query_ks and query_ks in tab_slugs:
        default_index = tab_slugs.index(query_ks)

    selected_label = st.radio(
        "Key stage:",
        tab_labels,
        horizontal=True,
        index=default_index,
        key="level_tabs",
    )

    # --- sync back to query params ---
    st.query_params["ks"] = tab_slugs[tab_labels.index(selected_label)]

    # --- find selected version ---
    version = next(
        (v for v in word.versions if label_for_version(v) == selected_label),
        None,
    )

    # --- render the selected version ---
    if version:
        render_frayer_model(
            version,
            show_word=False,
            related_words=word.related_words,
            show_topics=opts["show_topics"],
            show_definition=opts["show_definition"],
            show_characteristics=opts["show_characteristics"],
            show_examples=opts["show_examples"],
            show_non_examples=opts["show_non_examples"],
            show_related_words=opts["show_related_words"],
        )


if __name__ == "__main__":
    main()
