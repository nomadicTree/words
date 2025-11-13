"""Streamlit page for searching the words database"""

import time
import streamlit as st
import streamlit_antd_components as sac
from app.core.respositories.words_repo import search_words, get_word_version_by_id
from app.core.utils.strings import format_time_text
from app.core.models.word_models import SearchResult
from app.ui.components.page_header import page_header
from app.ui.components.frayer import render_frayer_model
from app.ui.components.buttons import details_button

PAGE_TITLE = "Search"


@st.cache_data(show_spinner=False)
def search_query(query: str):
    """Return matching words and search duration."""
    start_time = time.perf_counter()
    results = search_words(query)
    elapsed = time.perf_counter() - start_time
    return results, elapsed


def display_search_result(result: "SearchResult") -> None:
    """Display a single search result with expanders for each WordVersion."""
    st.subheader(result.word)
    st.markdown(f"Subject: **{result.subject.name}**")

    for version in result.versions:
        word_version = get_word_version_by_id(version["word_version_id"])
        with st.expander(word_version.level_label, expanded=False):
            with st.spinner("Loading version details..."):
                if word_version:
                    render_frayer_model(word_version, show_word=False)
                else:
                    st.warning("Version details not found.")
    details_button(result.url)


def display_search_results(results: list[SearchResult], query: str, elapsed: float):
    if not query:
        return

    plural = "s" if len(results) != 1 else ""
    st.caption(
        f"Found {len(results)} result{plural} for {query!r} in {format_time_text(elapsed)}."
    )

    if not results:
        st.info(f"No results found for {query!r}.")
        return

    for r in results:
        display_search_result(r)
        st.divider()


def main():
    """Page contents including search bar and search results"""
    page_header()

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
    query = query.strip()

    with st.spinner("Searching..."):
        # Perform search only if the query changed
        if query and query != st.session_state.search_query:
            st.session_state.search_query = query
            if query:
                (
                    st.session_state.search_results,
                    st.session_state.elapsed_time,
                ) = search_query(query)

        # Display results
        results = st.session_state.search_results
        elapsed_time = st.session_state.elapsed_time
    display_search_results(results, st.session_state["search_query"], elapsed_time)


if __name__ == "__main__":
    main()
