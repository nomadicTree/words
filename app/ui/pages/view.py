import streamlit as st
from app.core.models.word_models import WordVersionChoice
from app.core.respositories.words_repo import get_word_full
from app.ui.components.page_header import page_header
from app.ui.components.selection_helpers import select_item
from app.ui.components.frayer import (
    render_frayer_model,
)


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

    choices = [WordVersionChoice(v) for v in word.versions]

    selected_choice = select_item(items=choices, key="level", label="Select level")

    # Retrieve the underlying WordVersion
    version = selected_choice.version

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
