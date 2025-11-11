"""Streamlit page for searching the words database"""

import time
import streamlit as st
from app.core.respositories.words_repo import search_words
from app.core.utils.strings import format_time_text

# from app_lib.utils import apply_styles, render_frayer, format_time_text


PAGE_TITLE = "Search"


def search_query(query: str) -> list[dict]:
    start_time = time.perf_counter()
    found_words = search_words(query)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return found_words, elapsed_time


def display_search_results(
    results: list[dict], query: str, elapsed_time: float
) -> None:
    if elapsed_time is not None:
        plural = "s" if len(results) != 1 else ""
        formatted_time = format_time_text(elapsed_time)
        st.caption(
            f"Found {len(results)} result{plural} for {query!r} in {formatted_time}."
        )
    if results:
        for word in results:
            st.markdown(
                f"[{word["word"]} – {word["subject_name"]}](/view?id={word["word_id"]})"
            )
    elif query:
        st.info(f"No results found for {query!r}.")


def main():
    """Page contents including search bar and search results"""
    st.title("FrayerStore")
    # apply_styles()

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
        if query.strip() and query != st.session_state.search_query:
            st.session_state.search_query = query
            if query:
                (
                    st.session_state.search_results,
                    st.session_state.elapsed_time,
                ) = search_query(query)

        # Display results
        results = st.session_state.search_results
        elapsed_time = st.session_state.elapsed_time
    display_search_results(
        results, st.session_state["search_query"], elapsed_time
    )


if __name__ == "__main__":
    main()
