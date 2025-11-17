import streamlit as st
from app.core.models.word_models import Word, WordVersion
from app.services.search.search_models import SearchHit

VIEW_PAGE = "ui/pages/view.py"


def word_details_button(word: Word) -> None:
    """Create link button to view full details of given word"""
    if st.button(label="View full details →", key=f"details_{word.pk}"):
        st.session_state["view_word"] = word.slug
        st.session_state["view_subject"] = word.subject.slug
        st.switch_page(VIEW_PAGE)


def wordversion_details_button(wv: WordVersion, key_prefix: str = "") -> None:
    """Create link button to view full details of given wordversion"""
    if st.button(label="View full details →", key=f"details_{key_prefix}_{wv.pk}"):
        st.session_state["view_subject"] = wv.subject_slug
        st.session_state["view_word"] = wv.word_slug
        st.session_state["view_levels"] = wv.level_set_slug
        st.switch_page(VIEW_PAGE)


def searchhit_details_button(hit: SearchHit) -> None:
    if st.button(label="View full details →", key=hit.word_id):
        st.session_state["view_subject"] = hit.subject_slug
        st.session_state["view_word"] = hit.word_slug
        st.session_state["view_levels"] = hit.level_set_slug
        st.switch_page(VIEW_PAGE)
