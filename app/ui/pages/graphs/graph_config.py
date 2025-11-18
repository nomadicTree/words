import streamlit as st
from streamlit_agraph import Config
from app.ui.components.selection_helpers import cookie_manager

HEIGHT_SESSION_KEY = "graph_height"
HEIGHT_COOKIE_KEY = "fs_graph_height"


def get_graph_height():
    # Initialise session state from cookie
    if HEIGHT_SESSION_KEY not in st.session_state:
        saved = cookie_manager.get(HEIGHT_COOKIE_KEY)
        try:
            st.session_state[HEIGHT_SESSION_KEY] = int(saved)
        except (TypeError, ValueError):
            st.session_state[HEIGHT_SESSION_KEY] = 700  # default

    # Widget (always uses session value)
    graph_height = st.number_input(
        "Graph height (px)",
        min_value=200,
        max_value=5000,
        value=st.session_state[HEIGHT_SESSION_KEY],
        step=50,
        key="graph_height_widget",
    )

    # Sync changes back to session + cookie
    if graph_height != st.session_state[HEIGHT_SESSION_KEY]:
        st.session_state[HEIGHT_SESSION_KEY] = graph_height
        cookie_manager.set(
            HEIGHT_COOKIE_KEY, str(graph_height), key=f"{HEIGHT_COOKIE_KEY}_set"
        )

    return graph_height


def default_config(height):
    return Config(
        width="100%",
        height=height,
        directed=False,
        springLength=350,
        springStrength=0.002,
        centralGravity=0.0,
        gravity=0.0,
        damping=0.35,
        nodeHighlightBehavior=True,
        highlightColor="#000",
        edgeWeight=0.05,
        collapsible=False,
        physics=True,
        hierarchical=False,
    )
