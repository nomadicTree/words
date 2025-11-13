import streamlit as st


def details_button(url: str) -> None:
    """Create link button to view full details at given url"""
    st.link_button(
        label="View full details",
        url=url,
        width="content",
    )
