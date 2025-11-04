import json
import streamlit as st


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
        self.subject_name = (
            row["subject_name"] if "subject_name" in row.keys() else None
        )
        self.courses = (
            row["courses"].split(",") if "courses" in row.keys() else ""
        )
        self.topics = row["topics"] if "topics" in row.keys() else ""

    def display_frayer(self, include_subject_info=False, show_topics=False):
        from main import concise_html_list

        st.subheader(self.word)
        if include_subject_info:
            st.write(f"{self.subject_name} ({", ".join(self.courses)})")

        frayer_html = f"""
        <div class="frayer-grid">
            <div class="frayer-cell">
                <div class="frayer-title">Definition</div>
                {self.definition}
            </div>
            <div class="frayer-cell">
                <div class="frayer-title">Characteristics</div>
                <ul>{"".join(f"<li>{c}</li>" for c in self.characteristics)}</ul>
            </div>
            <div class="frayer-cell">
                <div class="frayer-title">Examples</div>
                <ul>{"".join(f"<li>{e}</li>" for e in self.examples)}</ul>
            </div>
            <div class="frayer-cell">
                <div class="frayer-title">Non-Examples</div>
                <ul>{"".join(f"<li>{n}</li>" for n in self.non_examples)}</ul>
            </div>
        </div>
        """
        st.markdown(frayer_html, unsafe_allow_html=True)

        if show_topics:
            st.divider()
            if self.topics:
                topics_list = self.topics.split(",")
                st.markdown("**Topics:**")
                st.markdown(
                    concise_html_list(topics_list), unsafe_allow_html=True
                )
                st.write("######")
