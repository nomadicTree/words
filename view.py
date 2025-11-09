import streamlit as st
from app_lib.models import Word
from app_lib.repositories import get_word_by_id
from app_lib.utils import page_header, render_frayer

query_params = st.query_params
id_param = query_params.get("id")  # returns a string or None

page_header()

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

    word = Word(word_row)
    related_words_exist = len(word.related_words) > 0

    with st.sidebar:
        st.header("Display Options")
        show_word = st.checkbox(
            "Word",
            value=True,
            key="show_word",
        )
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

        if related_words_exist:
            show_related_words = st.checkbox(
                "Related words", value=True, key="show_related_words"
            )
        else:
            show_related_words = False

        show_topics = st.checkbox(
            "Topics",
            value=True,
            key="show_topics",
        )
    render_frayer(
        word.as_dict(),
        show_subject=True,
        show_topics=show_topics,
        show_link=False,
        show_word=show_word,
        show_definition=show_definition,
        show_characteristics=show_characteristics,
        show_examples=show_examples,
        show_non_examples=show_non_examples,
        show_related_words=show_related_words,
    )
