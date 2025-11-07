import streamlit as st
from app_lib.models import Word
from app_lib.repositories import search_words


PAGE_TITLE = "Search"


def search_query(query):
    word_rows = search_words(query)
    words = []
    for r in word_rows:
        words.append(Word(r))
    return words


def display_search_results(results, query):
    if results:
        expand_results = len(results) == 1
        for word in results:
            with st.expander(
                f"{word.word} – {word.subject_name}",
                expanded=expand_results,
            ):
                word.display_frayer(show_subject=True, show_topics=True)
    elif query:
        st.info("No results found.")


st.title(PAGE_TITLE)
st.set_page_config(page_title=f"FrayerStore", page_icon="🔎")


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
).strip()
st.divider()

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
