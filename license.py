import streamlit as st
from pathlib import Path
from app_lib.utils import page_header, show_markdown_file

PAGE_TITLE = "Licensing"


def main():
    page_header(PAGE_TITLE)

    st.subheader("Content")
    show_markdown_file(Path("LICENSE_CONTENT.md"), in_container=True)
    st.subheader("Software")
    show_markdown_file(Path("LICENSE.md"), in_container=True)


if __name__ == "__main__":
    main()
