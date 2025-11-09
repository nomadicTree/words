"""Entry point for Streamlit app"""

import streamlit as st

pages = {
    "Frayer Models": [
        st.Page("search_words.py", title="Search", icon="🔎", default=True),
        st.Page("topic_glossary.py", title="Topic Glossary", icon="📄"),
        st.Page("course_glossary.py", title="Course Glossary", icon="📖"),
    ],
    "Info": [
        st.Page("about.py", title="About", icon="ℹ️"),
        st.Page("license.py", title="Licensing", icon="⚖️"),
        st.Page("planned_words.py", title="Planned Words", icon="📝"),
    ],
    "Utilities": [
        st.Page("model_maker.py", title="Model Maker", icon="🛠️"),
        st.Page("view.py", title="Model Viewer", icon="🪟"),
    ],
}

pg = st.navigation(pages)
st.set_page_config(page_title="FrayerStore", layout="wide")
pg.run()
