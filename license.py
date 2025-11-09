import streamlit as st
from pathlib import Path
from app_lib.utils import page_header

PAGE_TITLE = "Licensing"


def show_markdown_file(file_path: Path):
    md_text = Path(file_path).read_text(encoding="utf-8")
    st.code(md_text, language="markdown")


def main():
    page_header(PAGE_TITLE)

    st.subheader("Content")
    show_markdown_file(Path("LICENSE_CONTENT.md"))
    st.subheader("Software")
    show_markdown_file(Path("LICENSE.md"))


if __name__ == "__main__":
    main()
