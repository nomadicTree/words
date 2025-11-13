from dataclasses import dataclass
from typing import List
import streamlit as st
import yaml
from app.ui.components.selection_helpers import select_courses
from app.ui.components.page_header import page_header
from app.ui.components.frayer import render_frayer_model
from app.core.utils.strings import safe_snake_case_filename
from app.core.respositories.courses_repo import get_courses

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


def select_topics(course_topics):
    """Return a dict mapping course -> list of selected topic codes"""
    selected_topics = {}
    for course, topics in course_topics.items():
        codes = st.multiselect(
            f"Select topics for {course}",
            options=[t.code for t in topics],
            format_func=lambda code: next(
                f"{t.code} {t.name}" for t in topics if t.code == code
            ),
        )
        selected_topics[course] = codes
    return selected_topics


# ----------------------------
# Main
# ----------------------------
def main():
    page_header(PAGE_TITLE)
    available_courses = get_courses()
    courses = select_courses(available_courses)

    selected_topics = None
    st.divider()

    # Build YAML-ready topics
    col1, col2 = st.columns([1, 1])
    with col1:
        st.header("Word data input")
        word_data = word_input_form()

    yaml_topics = [
        {"course": course, "codes": sorted(codes)}
        for course, codes in selected_topics.items()
        if codes
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
        st.header("YAML preview")
        st.code(
            word_yaml,
            language="yaml",
        )
        st.download_button(
            "Download YAML",
            word_yaml,
            file_name=safe_snake_case_filename(word_data["word"], "yaml"),
        )

    st.subheader("Frayer preview")
    word_data["id"] = 0  # Dummy ID for preview
    with st.expander(word_data["word"], expanded=False):
        render_frayer_model(
            word_data,
            show_link=False,
            show_subject=False,
            show_topics=False,
            show_related_words=False,
        )


if __name__ == "__main__":
    main()
