import streamlit as st
import pandas as pd
import re
import unicodedata


def list_to_md(items):
    """Convert a list of strings to a markdown bullet list."""
    return "\n".join(f"- {item}" for item in items)


def render_topics(topics, word_id):
    topics_frame = pd.DataFrame(topics)
    column_config = {
        "code": st.column_config.Column("Code", width="auto"),
        "topic_name": st.column_config.Column("Topic", width="auto"),
        "course_name": st.column_config.Column("Course"),
    }
    st.dataframe(
        topics_frame,
        hide_index=True,
        column_order=("course_name", "code", "topic_name"),
        column_config=column_config,
        key=f"topic_frame_{word_id}",
    )


def blank_box():
    st.markdown(
        """
        <div style="
            display: flex;
            justify-content: center; /* horizontal */
            align-items: center;    /* vertical */
            font-size: 6rem;       /* adjust size */
            padding-bottom: 24px;
        ">
            ❓
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_frayer(
    frayer_dict: dict,
    show_subject=False,
    show_topics=False,
    show_link=True,
    show_definition=True,
    show_examples=True,
    show_characteristics=True,
    show_non_examples=True,
):
    word_url = f"/view?id={frayer_dict['id']}"
    if show_link:
        st.markdown(
            f"""
            <div class="frayer-title">
                <h3>
                    <a href="{word_url}" target="_blank" class="word-link">
                        {frayer_dict['word']} <span class="open-link-icon">🔗</span>
                    </a>
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.subheader(frayer_dict["word"])
    # Optional subject/courses display
    if show_subject:
        st.caption(f"Subject: **{frayer_dict["subject_name"]}**")
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Definition")
        if show_definition:
            st.write(frayer_dict["definition"])
        else:
            blank_box()
    with col2:
        st.markdown("#### Characteristics")
        if show_characteristics:
            st.markdown(list_to_md(frayer_dict["characteristics"]))
        else:
            blank_box()
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Examples")
        if show_examples:
            st.markdown(list_to_md(frayer_dict["examples"]))
        else:
            blank_box()
    with col2:
        st.markdown("#### Non-examples")
        if show_non_examples:
            st.markdown(list_to_md(frayer_dict["non_examples"]))
        else:
            blank_box()

    if show_topics:
        st.markdown("##### Topics:")
        render_topics(frayer_dict["topics"], frayer_dict["id"])


def safe_snake_case_filename(s: str, extension) -> str:
    # Normalize unicode characters to ASCII equivalents
    s = (
        unicodedata.normalize("NFKD", s)
        .encode("ascii", "ignore")
        .decode("ascii")
    )

    # Replace illegal filename characters with underscore
    s = re.sub(r'[\/\\\:\*\?"<>\|]', "_", s)

    # Replace spaces, hyphens, and dots with underscore
    s = re.sub(r"[\s\-.]+", "_", s)

    # Add underscore before uppercase letters (CamelCase → snake_case)
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)

    # Lowercase everything
    s = s.lower()

    # Collapse multiple underscores
    s = re.sub(r"_+", "_", s)

    # Strip leading/trailing underscores
    return f"{s.strip("_")}.{extension}"


def apply_styles():
    st.html(
        """
    <style>
    [data-testid='stHeaderActionElements'] {display: none;}
    .open-link-icon {
        text-decoration: none !important;
        opacity: 0;
        transition: opacity 0.2s;
        cursor: pointer;
    }

    .frayer-title .word-link {
        text-decoration: none !important;
        color: inherit;
        position: relative;
    }

    .frayer-title:hover .open-link-icon {
        opacity: 1;
    }
    </style>
    """
    )
