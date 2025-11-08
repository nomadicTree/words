"""Entry point for Streamlit app"""

import streamlit as st

pages = {
    "Frayer Models": [
        st.Page("search_words.py", title="Search", icon="🔎", default=True),
        st.Page("topic_index.py", title="Topic Index", icon="🗂️"),
        st.Page("glossary.py", title="Glossary", icon="📖"),
    ],
    "Utilities": [
        st.Page("model_maker.py", title="Model Maker", icon="🛠️"),
        st.Page("view.py", title="Model Viewer", icon="🪟"),
    ],
}

pg = st.navigation(pages)
pg.run()
