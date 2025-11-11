import streamlit as st
from pathlib import Path
from app_lib.utils import page_header, show_markdown_file

PAGE_TITLE = "Licensing"


def main():
    page_header(PAGE_TITLE)

    st.subheader("Content")
    with st.expander(
        "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
        expanded=True,
    ):
        show_markdown_file(Path("LICENSE_CONTENT.md"))
    st.subheader("Software")
    with st.expander("MIT License", expanded=True):
        show_markdown_file(Path("LICENSE.md"))


if __name__ == "__main__":
    main()
