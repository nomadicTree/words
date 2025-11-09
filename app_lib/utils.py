import re
import unicodedata
from pathlib import Path
from typing import List
import streamlit as st
import pandas as pd


def render_topics(topics, word_id):
    for t in topics:
        subject_name = t["subject_name"].replace(" ", "+")
        course_name = t["course_name"].replace(" ", "+")
        t["topic_url"] = (
            f"/topic_glossary?subject={subject_name}&course={course_name}#{t['code']}"
        )
    topics_frame = pd.DataFrame(topics)
    column_config = {
        "course_name": st.column_config.Column("Course", width="auto"),
        "topic_label": st.column_config.Column("Topic", width="auto"),
        "topic_url": st.column_config.LinkColumn(
            "Link", width="auto", display_text="Go to Topic Glossary"
        ),
    }
    st.dataframe(
        topics_frame,
        hide_index=True,
        column_order=("course_name", "topic_label", "topic_url"),
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


def render_frayer(
    frayer_dict: dict,
    show_subject=False,
    show_topics=False,
    show_link=True,
    show_word=True,
    show_definition=True,
    show_examples=True,
    show_characteristics=True,
    show_non_examples=True,
):
    if show_word:
        word = frayer_dict["word"]
    else:
        word = "❓"
    if show_link:
        word_url = f"/view?id={frayer_dict['id']}"
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
        st.subheader(word)
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
            render_list(frayer_dict["characteristics"])
        else:
            blank_box()
    col1, col2 = st.columns(2, border=True)
    with col1:
        st.markdown("#### Examples")
        if show_examples:
            render_list(frayer_dict["examples"])
        else:
            blank_box()
    with col2:
        st.markdown("#### Non-examples")
        if show_non_examples:
            render_list(frayer_dict["non_examples"])
        else:
            blank_box()

    if show_topics:
        st.markdown("##### Topics:")
        render_topics(frayer_dict["topics"], frayer_dict["id"])


def safe_snake_case_filename(s: str = "word", extension: str = "txt") -> str:
    # Normalize unicode characters to ASCII equivalents
    if len(s) == 0:
        s = "word"
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


def format_time_text(elapsed_time: float) -> str:
    """Format elapsed time into a human-readable string

    Args:
        time: elapsed time in seconds

    Returns:
        Formatted time string
    """
    if elapsed_time < 0.001:
        return f"{elapsed_time * 1_000_000:.1f} µs"
    else:
        return f"{elapsed_time * 1_000:.3f} ms"


def page_header(title: str = ""):
    st.title("FrayerStore")
    if title:
        st.header(title)
    apply_styles()


def show_markdown_file(file_path: Path, in_container: bool = False):
    md_text = Path(file_path).read_text(encoding="utf-8")
    if in_container:
        with st.container(border=True):
            st.markdown(md_text)
    else:
        st.markdown(md_text)
