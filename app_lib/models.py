import json
import streamlit as st
from app_lib.repositories import get_topics_for_word, get_subject_name
from app_lib.utils import list_to_md
import pandas as pd


class Word:
    def __init__(self, row):
        self.id = row["id"]
        self.word = row["word"]
        self.definition = (
            row["definition"] if "definition" in row.keys() else ""
        )
        self.characteristics = (
            json.loads(row["characteristics"])
            if "characteristics" in row.keys()
            else []
        )
        self.examples = (
            json.loads(row["examples"]) if "examples" in row.keys() else []
        )
        self.non_examples = (
            json.loads(row["non_examples"])
            if "non_examples" in row.keys()
            else []
        )
        self.subject_name = get_subject_name(row["subject_id"])

        topic_rows = get_topics_for_word(self.id)

        self.topics = [dict(r) for r in topic_rows]

    def display_topics(self):
        topics_frame = pd.DataFrame(self.topics)
        column_config = {
            "code": st.column_config.Column("Code", width="auto"),
            "topic_name": st.column_config.Column("Topic", width="auto"),
            "course_name": st.column_config.Column("Course"),
        }
        st.dataframe(
            topics_frame,
            hide_index=True,
            column_order=("course_name", "code", "topic_name"),
            column_config=column_config,
            key=f"topic_frame_{self.id}",
        )

    def display_frayer(self, include_subject_info=False, show_topics=False):
        st.subheader(self.word)

        # Optional subject/courses display
        if include_subject_info:
            st.caption(f"Subject: **{self.subject_name}**")

        col1, col2 = st.columns(2, border=True)
        with col1:
            st.markdown("#### Definition")
            st.write(self.definition)
        with col2:
            st.markdown("#### Characteristics")
            st.markdown(list_to_md(self.characteristics))

        col3, col4 = st.columns(2, border=True)
        with col3:
            st.markdown("#### Examples")
            st.markdown(list_to_md(self.examples))
        with col4:
            st.markdown("#### Non-examples")
            st.markdown(list_to_md(self.non_examples))

        if show_topics and self.topics:
            st.markdown("##### Topics:")
            self.display_topics()
