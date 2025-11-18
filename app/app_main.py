from pathlib import Path
import streamlit as st
import sys
import os

# Add the parent directory of 'app' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Base directory for all Streamlit pages
# Always relative to this file’s directory
PAGES_DIR = Path(__file__).resolve().parent / "ui/pages"

pages = {
    "FrayerStore": [
        st.Page(
            PAGES_DIR / "search_words.py",
            title="Search",
            icon="🔎",
            default=True,
        ),
        st.Page(PAGES_DIR / "topic_glossary.py", title="Topic Glossary", icon="📄"),
        st.Page(
            PAGES_DIR / "course_glossary.py",
            title="Course Glossary",
            icon="📖",
        ),
        st.Page(
            PAGES_DIR / "graphs" / "relationship_graph.py",
            title="Relationship Graph",
            icon="👬",
        ),
        st.Page(PAGES_DIR / "view.py", title="Model Viewer", icon="🪟"),
    ],
    "Info": [
        st.Page(PAGES_DIR / "about.py", title="About", icon="ℹ️"),
        st.Page(PAGES_DIR / "ai_usage.py", title="AI Usage", icon="💻"),
        st.Page(PAGES_DIR / "license.py", title="Licensing", icon="⚖️"),
        st.Page(PAGES_DIR / "planned_words.py", title="Planned Words", icon="📝"),
    ],
    "Utilities": [
        st.Page(PAGES_DIR / "model_maker.py", title="Model Maker", icon="🛠️"),
    ],
}

pg = st.navigation(pages)
st.set_page_config(page_title="FrayerStore", layout="wide", page_icon="📖")
pg.run()
