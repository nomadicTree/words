import streamlit as st
from app_lib.repositories import search_words


@st.cache_data
def get_word_object(row_dict):
    # ensures Word() creation is cached per unique row
    from app_lib.models import Word

    return Word(row_dict)


def search_query(query):
    word_rows = search_words(query)
    return [get_word_object(dict(r)) for r in word_rows]


def display_search_results(results, query):
    if results:
        for word in results:
            with st.expander(
                f"{word.word} – {word.subject_name}", expanded=False
            ):
                word.display_frayer(
                    include_subject_info=True, show_topics=True
                )
    elif query:
        st.info("No results found.")


st.set_page_config(page_title="FrayerStore")
st.title("Search")

# --- Step 1: Initialize session state once ---
if "search_query" not in st.session_state:
    # Use URL query if available, otherwise empty
    url_query = st.query_params.get("q", [""])[0]
    st.session_state.search_query = url_query
if "search_results" not in st.session_state:
    st.session_state.search_results = []

# --- Step 2: Text input bound to session state ---
query = st.text_input(
    "Search FrayerStore",
    value=st.session_state.search_query,
    key="search_input",  # binds directly to session_state
).strip()

# --- Step 3: Update results only if the input changed ---
if query != st.session_state.search_query:
    st.session_state.search_query = query
    st.session_state.search_results = search_query(query) if query else []

    # Update URL to match the session state
    st.query_params = {"q": [query]}  # triggers rerun safely

# --- Step 4: Display results ---
for word in st.session_state.search_results:
    with st.expander(f"{word.word} – {word.subject_name}", expanded=False):
        word.display_frayer(include_subject_info=True, show_topics=True)
