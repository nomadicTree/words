import streamlit as st


def apply_styles():
    st.html(
        """
    <style>
    [data-testid='stHeaderActionElements'] {display: none;}
    """
    )


def page_header(title: str = ""):
    st.title("FrayerStore")
    if title:
        st.header(title)
    apply_styles()



