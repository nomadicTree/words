from typing import List
import streamlit as st
import yaml
from app.ui.components.selection_helpers import select_courses
from app.ui.components.page_header import page_header
from app.ui.components.frayer import render_frayer_model
from app.core.utils.strings import build_wordversion_filename
from app.core.repositories.courses_repo import get_courses
from app.core.repositories.topics_repo import get_topics_for_course
from app.core.models.topic_model import Topic
from app.core.models.word_models import WordVersion

PAGE_TITLE = "Model Maker"


def word_input_form():
    """Render input fields for word data and display YAML output."""

    word = st.text_input("Word")
    definition = st.text_area("Definition", height="content")

    characteristics = st.text_area(
        "Characteristics",
        help="Separate multiple characteristics with a line containing only ---",
        placeholder="Characteristic 1\n---\nCharacteristic 2",
        height="content",
    )

    examples = st.text_area(
        "Examples",
        help="Separate multiple examples with a line containing only ---",
        placeholder=("Example 1\n---\nExample 2"),
        height="content",
    )

    non_examples = st.text_area(
        "Non-examples",
        help="Separate multiple non-examples with a line containing only ---",
        placeholder="Non-example 1\n---\nNon-example 2",
        height="content",
    )

    yaml_data = {
        "word": word.strip(),
        "definition": definition.strip(),
        "characteristics": [
            c.strip() for c in characteristics.split("---") if c.strip()
        ],
        "examples": [e.strip() for e in examples.split("---") if e.strip()],
        "non_examples": [ne.strip() for ne in non_examples.split("---") if ne.strip()],
    }

    return yaml_data


def format_multiline_strings(items: List[str]) -> List[str]:
    """Format multiline inputs, preserving code blocks.

    Args:
        items: List of input strings, possibly containing code blocks.
    Returns:
        Formatted list of strings.
    """

    # --- Use a subclass of str and register a clean representer ---
    class LiteralString(str):
        pass

    def literal_presenter(dumper, data):
        """Force YAML literal style (|) for multiline strings."""
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")

    yaml.add_representer(LiteralString, literal_presenter)

    # Convert only multiline examples to literal block style
    formatted_items = []
    for i in items:
        if "\n" in i:
            # Remove trailing whitespace from each line, preserve leading spaces
            lines = [line.rstrip() for line in i.splitlines()]
            cleaned = "\n".join(lines).rstrip()  # also remove trailing blank lines
            formatted_items.append(LiteralString(cleaned))
        else:  # single line -> leave plain
            formatted_items.append(i)

    return formatted_items


def select_topics_for_course(course) -> list[Topic]:
    available_topics = get_topics_for_course(course)
    selected_topics = st.multiselect(
        f"Select topics for {course.name}",
        options=available_topics,
        format_func=lambda t: t.label,
    )
    return selected_topics


def select_topics(available_courses):
    """Return a dict mapping course -> list of selected topic codes"""
    return {c: select_topics_for_course(c) for c in available_courses}


# ----------------------------
# Main
# ----------------------------
def main():
    page_header(PAGE_TITLE)
    available_courses = get_courses()
    with st.sidebar:
        selected_subject, selected_courses = select_courses(available_courses)
        selected_topics = select_topics(selected_courses)

    # Build YAML-ready topics
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**Word data input**")
            word_data = word_input_form()

    yaml_levels = [course.level.name for course in selected_courses]
    word_data["levels"] = yaml_levels
    yaml_topics = [
        {"course": course.name, "codes": sorted(t.code for t in topics)}
        for course, topics in selected_topics.items()
        if topics
    ]
    word_data["topics"] = yaml_topics

    word_data["examples"] = format_multiline_strings(word_data["examples"])
    word_data["non_examples"] = format_multiline_strings(word_data["non_examples"])
    word_data["characteristics"] = format_multiline_strings(
        word_data["characteristics"]
    )

    word_yaml = yaml.dump(
        word_data, sort_keys=False, allow_unicode=True, width=float("inf")
    )

    with col2:
        with st.container(border=True):
            st.markdown("**YAML preview**")
            st.code(
                word_yaml,
                language="yaml",
            )
            st.download_button(
                "Download YAML",
                word_yaml,
                file_name=build_wordversion_filename(word_data["word"], yaml_levels),
            )

    preview_word = WordVersion(
        pk=0,
        word=word_data["word"],
        word_slug=None,
        subject_slug=None,
        definition=word_data["definition"],
        characteristics=word_data["characteristics"],
        examples=word_data["examples"],
        non_examples=word_data["non_examples"],
        topics=[],
        levels=[],
    )
    with st.expander("**Live preview**", expanded=False):
        render_frayer_model(
            preview_word,
            show_topics=False,
        )


if __name__ == "__main__":
    main()
