import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "db/Words.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

# ---------------------------------------------------------------------
# Load all words, subjects, and their latest WordVersion data
# ---------------------------------------------------------------------
df = pd.read_sql_query(
    """
    SELECT DISTINCT
        w.id AS word_id,
        w.word,
        s.id AS subject_id,
        s.name AS subject_name,
        v.definition,
        v.characteristics,
        v.examples,
        v.non_examples
    FROM Words w
    JOIN Subjects s ON w.subject_id = s.id
    JOIN WordVersions v ON w.id = v.word_id
    """,
    conn,
)

# ---------------------------------------------------------------------
# Load existing relationships to skip duplicates
# ---------------------------------------------------------------------
existing_df = pd.read_sql_query(
    "SELECT word_id1, word_id2 FROM WordRelationships", conn
)
existing_pairs = {
    tuple(sorted([r["word_id1"], r["word_id2"]]))
    for _, r in existing_df.iterrows()
}


# ---------------------------------------------------------------------
# Candidate-finding logic
# ---------------------------------------------------------------------
def find_candidate_relationships(
    df: pd.DataFrame, existing_pairs: set
) -> pd.DataFrame:
    relationships = set()

    # Group words by subject
    for subject_id, group in df.groupby("subject_id"):
        for i, row_i in group.iterrows():
            word_i = row_i["word"].lower()

            for j, row_j in group.iterrows():
                if i == j:
                    continue

                combined_text = " ".join(
                    str(row_j[col])
                    for col in group.columns
                    if col
                    not in ["word", "non_examples", "word_id", "subject_id"]
                ).lower()

                if word_i in combined_text:
                    a = (row_i["word_id"], row_i["word"].lower())
                    b = (row_j["word_id"], row_j["word"].lower())
                    pair = tuple(sorted([a, b], key=lambda x: x[0]))

                    ids_only = tuple(sorted([pair[0][0], pair[1][0]]))
                    if ids_only not in existing_pairs:
                        relationships.add((pair, row_i["subject_name"]))

    if not relationships:
        return pd.DataFrame(
            columns=["id1", "word1", "id2", "word2", "subject_name"]
        )

    return pd.DataFrame(
        [
            (a_id, a_word, b_id, b_word, subject)
            for ((a_id, a_word), (b_id, b_word)), subject in relationships
        ],
        columns=["id1", "word1", "id2", "word2", "subject_name"],
    )


# ---------------------------------------------------------------------
# Run candidate finder
# ---------------------------------------------------------------------
candidates_df = find_candidate_relationships(df, existing_pairs)

# ---------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------
st.title("Approve Word Relationships (by Subject)")

if candidates_df.empty:
    st.info("✅ No new candidate relationships found.")
else:
    approved_rows = []

    for _, row in candidates_df.iterrows():
        st.write(
            f"**{row['word1']} ↔ {row['word2']}** *(Subject: {row['subject_name']})*"
        )
        approve = st.radio(
            "Approve this relationship?",
            ("No", "Yes"),
            key=f"{row['id1']}_{row['id2']}_{row['subject_name']}",
            horizontal=True,
        )

        if approve == "Yes":
            approved_rows.append((row["id1"], row["id2"]))

    if st.button("💾 Save approved relationships"):
        inserted = 0
        with conn:
            for id1, id2 in approved_rows:
                word_id1, word_id2 = sorted((id1, id2))
                try:
                    c.execute(
                        """
                        INSERT INTO WordRelationships (word_id1, word_id2)
                        VALUES (?, ?)
                        """,
                        (word_id1, word_id2),
                    )
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass  # skip duplicates

        st.success(f"✅ {inserted} relationships saved successfully.")
