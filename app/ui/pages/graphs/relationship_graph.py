import streamlit as st

from app.core.repositories.word_graph_repo import (
    load_words_and_rels,
    load_word_levels,
    load_word_courses,
)
from app.core.repositories.courses_repo import get_courses
from app.ui.components.selection_helpers import select_course
from app.ui.pages.graphs.graph_filters import filter_words
from app.ui.pages.graphs.graph_builder import build_graph
from app.ui.pages.graphs.graph_config import get_graph_height, default_config

from streamlit_agraph import agraph


def main():
    st.title("Relationship Graph")

    df_words, df_rels = load_words_and_rels()
    df_levels = load_word_levels()
    df_courses = load_word_courses()

    # sidebar
    with st.sidebar:
        available_courses = get_courses()
        selected_course = select_course(available_courses)
        if not selected_course:
            return

        subject_id = selected_course.subject.pk
        level_id = selected_course.level.pk
        course_id = selected_course.pk

        graph_height = get_graph_height()

    # filtering
    df_words_filt, df_rel_filt = filter_words(
        df_words,
        df_rels,
        df_levels,
        df_courses,
        subject_id,
        level_id,
        course_id,
    )

    if df_words_filt.empty:
        st.warning("No words match the selected filters.")
        return

    st.caption(f"{len(df_words_filt)} words, {len(df_rel_filt)} relationships")

    # build graph
    nodes, edges = build_graph(df_words_filt, df_rel_filt)

    # render
    config = default_config(graph_height)
    with st.container(border=True):
        agraph(nodes=nodes, edges=edges, config=config)


if __name__ == "__main__":
    main()
