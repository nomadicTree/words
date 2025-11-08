import streamlit as st
from app_lib.models import Word
from app_lib.repositories import get_word_by_id
from app_lib.utils import apply_styles, render_frayer

PAGE_TITLE = "View"
apply_styles()
query_params = st.query_params
id_param = query_params.get("id")  # returns a string or None

if id_param is None:
    st.info("No id given in URL. Are you here accidentally?")
else:
    try:
        word_id = int(id_param)
    except ValueError:
        st.error("Invalid id in URL")
        st.stop()
    word_row = get_word_by_id(word_id)
    if word_row is None:
        st.error(f"No word found with id {word_id}")
        st.stop()

    with st.sidebar:
        show_definition = st.checkbox(
            "Definition",
            value=True,
            key="show_definition",
        )
        show_characteristics = st.checkbox(
            "Characteristics",
            value=True,
            key="show_characteristics",
        )
        show_examples = st.checkbox(
            "Examples",
            value=True,
            key="show_examples",
        )
        show_non_examples = st.checkbox(
            "Non-examples",
            value=True,
            key="show_non_examples",
        )
    word = Word(word_row)
    render_frayer(
        word.as_dict(),
        show_subject=True,
        show_topics=True,
        show_link=False,
        show_definition=show_definition,
        show_characteristics=show_characteristics,
        show_examples=show_examples,
        show_non_examples=show_non_examples,
    )
