"""Streamlit page for searching the words database"""

from typing import List
import streamlit as st
from app_lib.models import Word
from app_lib.repositories import search_words
from app_lib.utils import apply_styles, render_frayer


PAGE_TITLE = "Search"


def search_query(query: str) -> List[Word]:
    """Wrapper for searching words and returning Word objects

    Args:
        query: search query

    Returns:
        Search results as Word objects
    """
    word_rows = search_words(query)
    words = []
    for r in word_rows:
        words.append(Word(r))
    return words


def display_search_results(results: List[Word], query: str) -> None:
    """Display all results as expandable Frayer Models

    Args:
        results: search results to display
        query: original search query
    """
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
    st.title(PAGE_TITLE)
    apply_styles()

    # Initialize session state for search
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "search_results" not in st.session_state:
        st.session_state.search_results = []

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
                st.session_state.search_results = search_query(query)
            else:
                st.session_state.search_results = []

        # Display results
        results = st.session_state.search_results
    display_search_results(results, query)


if __name__ == "__main__":
    main()
