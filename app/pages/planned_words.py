from app_lib.utils import page_header, show_markdown_file
from pathlib import Path
import streamlit as st

PAGE_TITLE = "Planned Words"


def main():
    page_header(PAGE_TITLE)
    st.markdown(
        """
        Each time I create a Frayer Model for a word, it raises new words that also need Frayer Models.
        This page contains my to-do list—in no particular order, and by no means complete.
        """
    )

    st.markdown(
        """
        If you would like to contribute to this list, please submit a pull request on GitHub adding words to the `TODO.md` file.
        If you would like to contribute Frayer Models for any of these words, please submit them as well!
        """
    )
    show_markdown_file(Path("TODO.md"))


if __name__ == "__main__":
    main()
