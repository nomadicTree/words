"""Streamlit page for searching the words database"""

import time
from typing import List
import streamlit as st
from app_lib.models import Word
from app_lib.repositories import search_words
from app_lib.utils import apply_styles, render_frayer, format_time_text


PAGE_TITLE = "Search"


def search_query(query: str) -> List[Word]:
    """Wrapper for searching words and returning Word objects

    Args:
        query: search query

    Returns:
        Search results as Word objects
    """
    start_time = time.perf_counter()
    word_rows = search_words(query)
    words = []
    for r in word_rows:
        words.append(Word(r))
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return words, elapsed_time


def display_search_results(
    results: List[Word], query: str, elapsed_time: float
) -> None:
    """Display all results as expandable Frayer Models

    Args:
        results: search results to display
        query: original search query
    """
    if elapsed_time is not None:
        plural = "s" if len(results) != 1 else ""
        formatted_time = format_time_text(elapsed_time)
        st.caption(
            f"Found {len(results)} result{plural} for {query!r} in {formatted_time}."
        )
    if results:
        expand_results = len(results) == 1  # Expand if only one result
        for word in results:
            with st.expander(
                f"{word.word} – {word.subject_name}",
                expanded=expand_results,
            ):
                render_frayer(
                    word.as_dict(),
                    show_subject=True,
                    show_topics=True,
                )
    elif query:
        st.info(f"No results found for {query!r}.")


def main():
    """Page contents including search bar and search results"""
    st.title("FrayerStore")
    apply_styles()

    # Initialize session state for search
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = []
    if "elapsed_time" not in st.session_state:
        st.session_state.elapsed_time = None

    # Search input
    query = st.text_input(
        "Search FrayerStore",
        value=st.session_state.search_query,
        key="search_input",
    )
    st.divider()

    with st.spinner("Searching..."):

        # Perform search only if the query changed
        if query != st.session_state.search_query:
            st.session_state.search_query = query
            if query:
                (
                    st.session_state.search_results,
                    st.session_state.elapsed_time,
                ) = search_query(query)
            else:
                st.session_state.search_results = []

        # Display results
        results = st.session_state.search_results
        elapsed_time = st.session_state.elapsed_time
    display_search_results(results, query, elapsed_time)


if __name__ == "__main__":
    main()
