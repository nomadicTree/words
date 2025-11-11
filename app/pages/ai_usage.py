import streamlit as st
from app_lib.utils import page_header

PAGE_TITLE = "AI Usage"


def main():
    page_header(PAGE_TITLE)

    st.markdown(
        """
        In the creation of this website, I made extensive use of AI tools to support both development and content creation.
        """
    )
    st.markdown(
        """
        I am committed to transparency and honesty in my work and aim to model responsible and honest practice when using AI as a tool.
        While AI has contributed significantly, all final decisions on code integration, content, and presentation have been made by me.
        """
    )
    st.subheader("Code development")
    st.markdown(
        """
        I relied heavily on AI to generate and refine Python code and SQL queries, accelerating the development of this website and helping me work effectively with tools and libraries that are otherwise new to me.
        """
    )

    st.subheader("Content creation")
    st.markdown(
        """
        AI was used to draft, edit, and refine many of the Frayer Models presented on the website, supporting clarity, accuracy, and completeness of explanations.
        """
    )


if __name__ == "__main__":
    main()
