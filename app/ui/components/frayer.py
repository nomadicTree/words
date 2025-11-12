import streamlit as st
import pandas as pd

from app.core.models.word_models import WordVersion, RelatedWord


def render_related_words(related_words: list[RelatedWord], word_id: int):
    related_word_data = [{"word": w.word, "url": w.url} for w in related_words]
    words_frame = pd.DataFrame(related_word_data)
    column_config = {
        "word": st.column_config.Column("Word", width="auto"),
        "url": st.column_config.LinkColumn(
            "Link", width="auto", display_text="Go to Frayer Model"
        ),
    }
    st.dataframe(
        words_frame,
        hide_index=True,
        column_order=("word", "url"),
        column_config=column_config,
        key=f"related_words_{word_id}",
    )


def render_topics(word_version: WordVersion):
    """Render the topics associated with a WordVersion using DataFrame display."""

    # Convert topic objects into a flat list of dicts for DataFrame
    topics_data = [
        {
            "course": t.course.name,
            "label": t.label,
            "topic_url": t.url,
        }
        for t in word_version.topics
    ]

    if not topics_data:
        st.info("No topics linked to this version.")
        return

    topics_frame = pd.DataFrame(topics_data)

    column_config = {
        "course": st.column_config.Column("Course", width="auto"),
        "label": st.column_config.Column("Topic", width="auto"),
        "topic_url": st.column_config.LinkColumn(
            "Link", width="auto", display_text="Go to Topic Glossary"
        ),
    }

    st.dataframe(
        topics_frame,
        hide_index=True,
        column_order=("course", "label", "topic_url"),
        column_config=column_config,
        key=f"topic_frame_{word_version.wv_id}",
    )


def blank_box():
    st.markdown(
        """
        <div style="
            display: flex;
            justify-content: center; /* horizontal */
            align-items: center;    /* vertical */
            font-size: 6rem;       /* adjust size */
            padding-bottom: 40px;
        ">
            ❓
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_list(items: list[str]) -> None:
    """Render a mixed list of Markdown text and code blocks nicely in Streamlit."""
    buffer = []  # collects consecutive text items

    def flush_buffer():
        if buffer:
            st.markdown("\n".join(f"- {x}" for x in buffer))
            buffer.clear()

    for item in items:
        item = item.strip()
        if item.startswith("```"):
            flush_buffer()
            lines = item.split("\n")
            first_line = lines[0].strip("`")
            language = first_line or None
            code_content = "\n".join(lines[1:-1])
            st.code(code_content, language=language)
        else:
            buffer.append(item)

    flush_buffer()


@st.dialog("Frayer Model", width="large")
def render_frayer_model_modal(word: WordVersion):
    render_frayer_model(word)


def render_frayer_model(
    word: WordVersion,
    show_word=True,
    related_words: list[RelatedWord] | None = None,
    show_topics=False,
    show_definition=True,
    show_examples=True,
    show_characteristics=True,
    show_non_examples=True,
    show_related_words=False,
):
    if show_word:
        st.subheader(word.word)
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Definition")
        if show_definition:
            st.write(word.definition)
        else:
            blank_box()
    with col2:
        st.markdown("#### Characteristics")
        if show_characteristics:
            render_list(word.characteristics)
        else:
            blank_box()
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Examples")
        if show_examples:
            render_list(word.examples)
        else:
            blank_box()
    with col2:
        st.markdown("#### Non-examples")
        if show_non_examples:
            render_list(word.non_examples)
        else:
            blank_box()

    if show_related_words and related_words:
        st.markdown("##### Related words:")
        render_related_words(related_words, word.word_id)

    if show_topics:
        st.markdown("##### Topics:")
        render_topics(word)
