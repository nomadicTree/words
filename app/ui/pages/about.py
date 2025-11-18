import streamlit as st
from app.ui.components.page_header import page_header
from app.ui.components.frayer import render_frayer_model
from app.ui.components.buttons import wordversion_details_button
from app.core.repositories.words_repo import get_word_version_by_id

PAGE_TITLE = "About"
EXAMPLE_WORD_ID = 4  # concatenation


def main():
    page_header(PAGE_TITLE)

    st.markdown(
        """
    **FrayerStore** is a searchable database of **Frayer Models**.
    Think of it as a subject-specific dictionary, but, rather than just giving definitions, it presents words with Frayer Models.
    FrayerStore makes creating, sharing, and viewing Frayer Models easy.
    """
    )

    st.subheader("Frayer Models")
    st.markdown(
        """
        Frayer Models are graphical organisers for learning new vocabulary.
        They present words along with definitions, characteristics, examples, and non-examples.
        Frayer Models are particularly useful for learning 'tier three' vocabulary—words that are subject-specific and not commonly used in everyday language.
        """
    )
    with st.expander("Example Frayer Model", expanded=True):
        example_word = get_word_version_by_id(EXAMPLE_WORD_ID)
        render_frayer_model(
            example_word,
            example_word.word,
            show_topics=False,
            show_related_words=False,
        )
        wordversion_details_button(example_word)

    st.subheader("Why I am building this")
    st.markdown(
        """
        I had the idea for FrayerStore following an inset day at my school.
        The day focused on disciplinary literacy and strategies to help students improve their reading skills.
        We were encouraged to explore methods, like Frayer Models, to help students improve as readers and learn subject-specific vocabulary.

        Frayer Models are great, but I find the mechanics of making and sharing them tedious.

        FrayerStore solves my issues with making and using Frayer Models in the classroom. It provides:
        - A central, searchable place to store and share Frayer Models;
        - Filtering by course and topic;
        - Tools to create Frayer Models quickly.

        I hope you find it useful too!
        """
    )
    st.subheader("Current scope")
    st.markdown(
        """
        Right now, FrayerStore focuses on secondary Computer Science, specifically:
        - OCR J277 (GCSE Computer Science)
        - OCR H446 (A Level Computer Science)

        These are the courses that I teach, so I am starting with them.

        However, FrayerStore is **designed to support any subject**. If you would like your subject or course added, please raise an issue in the [GitHub repository](https://github.com/nomadicTree/FrayerStore).
        """
    )

    st.subheader("How you can contribute")
    st.markdown(
        """
        FrayerStore is an open-source project—contributions are welcome!
        For detailed information about licensing, see the [licensing page](./license).

        To contribute new Frayer Models, follow these steps:
        1. Create a Frayer Model using the [Model Maker](./model_maker).
        2. Download the YAML file.
        3. Submit it as a Pull request in the GitHub repository.

        Alternatively, if you spot an issue with an existing entry, feel free to:
        - Raise an issue, or
        - Fix it and submit a pull request.

        """
    )


if __name__ == "__main__":
    main()
