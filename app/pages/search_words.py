"""Streamlit page for searching the words database."""

import time
from typing import List, Optional, Tuple

import streamlit as st

from app.components.common import page_header
from app.core.models.word_models import SearchResult
from app.core.respositories.topics_repo import get_all_subjects_courses_topics
from app.core.respositories.words_repo import search_words
from app.core.utils.strings import format_time_text


PAGE_TITLE = "Search"

SubjectOption = Tuple[Optional[int], str]
TopicOption = Tuple[Optional[int], str]


@st.cache_data(show_spinner=False)
def load_catalog() -> List[dict]:
    return get_all_subjects_courses_topics()


@st.cache_data(show_spinner=False)
def search_query(
    query: str, subject_id: Optional[int], topic_id: Optional[int]
):
    """Return matching words and search duration."""
    start_time = time.perf_counter()
    results = search_words(query, subject_id=subject_id, topic_id=topic_id)
    elapsed = time.perf_counter() - start_time
    return results, elapsed


def build_subject_options(data: List[dict]) -> List[SubjectOption]:
    seen = {}
    for row in data:
        seen[row["subject_id"]] = row["subject"]
    return sorted(seen.items(), key=lambda item: item[1])


def build_topic_options(
    data: List[dict], subject_id: Optional[int]
) -> List[TopicOption]:
    if subject_id is None:
        return []
    seen = {}
    for row in data:
        if row["subject_id"] == subject_id:
            seen[row["topic_id"]] = row["topic_label"]
    return sorted(seen.items(), key=lambda item: item[1])


def display_search_results(
    results: list[SearchResult],
    query: str,
    elapsed: Optional[float],
    subject_label: Optional[str],
    topic_label: Optional[str],
):
    if not query:
        return

    plural = "s" if len(results) != 1 else ""
    elapsed_text = format_time_text(elapsed) if elapsed is not None else "—"
    st.caption(
        f"Found {len(results)} result{plural} for {query!r} in {elapsed_text}."
    )

    filters = []
    if subject_label:
        filters.append(subject_label)
    if topic_label:
        filters.append(topic_label)
    if filters:
        st.caption("Filters: " + " → ".join(filters))

    if not results:
        st.info(f"No results found for {query!r}.")
        return

    for r in results:
        with st.container(border=True):
            st.markdown(f"#### [{r.word}]({r.url})")
            st.markdown(f"**{r.subject_name}**: {r.level_names or '—'}")


def main():
    """Page contents including search bar, filters, and search results."""
    page_header(PAGE_TITLE)

    with st.spinner("Loading filters..."):
        catalog = load_catalog()

    # Initialize session state for search
    st.session_state.setdefault("search_query", "")
    st.session_state.setdefault("search_results", [])
    st.session_state.setdefault("elapsed_time", None)
    st.session_state.setdefault("last_search_params", ("", None, None))
    st.session_state.setdefault("selected_subject_option", (None, "All subjects"))
    st.session_state.setdefault("selected_topic_option", (None, "All topics"))

    subject_options = [(None, "All subjects")] + build_subject_options(catalog)
    previous_subject = st.session_state["selected_subject_option"]
    if previous_subject not in subject_options:
        previous_subject = subject_options[0]
    subject_index = subject_options.index(previous_subject)
    selected_subject = st.selectbox(
        "Filter by subject",
        subject_options,
        index=subject_index,
        format_func=lambda opt: opt[1],
    )
    if selected_subject != st.session_state["selected_subject_option"]:
        st.session_state["selected_subject_option"] = selected_subject
        st.session_state["selected_topic_option"] = (None, "All topics")
    else:
        st.session_state["selected_subject_option"] = selected_subject

    topic_options = [(None, "All topics")] + build_topic_options(
        catalog, selected_subject[0]
    )
    previous_topic = st.session_state["selected_topic_option"]
    if previous_topic not in topic_options:
        previous_topic = topic_options[0]
    topic_index = topic_options.index(previous_topic)
    selected_topic = st.selectbox(
        "Filter by topic",
        topic_options,
        index=topic_index,
        format_func=lambda opt: opt[1],
    )
    st.session_state["selected_topic_option"] = selected_topic

    # Search input
    raw_query = st.text_input(
        "Search FrayerStore",
        value=st.session_state["search_query"],
        key="search_input",
    )
    query = raw_query.strip()
    st.divider()

    subject_id = selected_subject[0]
    topic_id = selected_topic[0]

    with st.spinner("Searching..."):
        if query:
            params = (query, subject_id, topic_id)
            if params != st.session_state["last_search_params"]:
                (
                    st.session_state["search_results"],
                    st.session_state["elapsed_time"],
                ) = search_query(query, subject_id, topic_id)
                st.session_state["last_search_params"] = params
                st.session_state["search_query"] = query
        else:
            st.session_state["search_results"] = []
            st.session_state["elapsed_time"] = None
            st.session_state["search_query"] = ""
            st.session_state["last_search_params"] = ("", subject_id, topic_id)

    display_search_results(
        st.session_state["search_results"],
        st.session_state["search_query"],
        st.session_state["elapsed_time"],
        selected_subject[1] if subject_id else None,
        selected_topic[1] if topic_id else None,
    )


if __name__ == "__main__":
    main()
