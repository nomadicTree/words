import sqlite3
import pandas as pd
import streamlit as st

DB_FILE = "data/words.db"

conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
df = pd.read_sql_query("SELECT * FROM Word", conn)


def find_candidate_relationships(df):
    relationships = set()

    for i, row_i in df.iterrows():
        word_i = row_i["word"].lower()

        for j, row_j in df.iterrows():
            if i == j:
                continue

            # combine all text fields of row_j except 'word' and 'non_examples'
            combined_text = " ".join(
                str(row_j[col])
                for col in df.columns
                if col not in ["word", "non_examples"]
            ).lower()

            if word_i in combined_text:
                # Create a pair of tuples: (id, word)
                item1 = (row_i["id"], row_i["word"].lower())
                item2 = (row_j["id"], row_j["word"].lower())

                # Sort the pair by id (or word) to ensure uniqueness
                pair = tuple(sorted([item1, item2], key=lambda x: x[0]))

                relationships.add(pair)

    # Convert to DataFrame
    return pd.DataFrame(
        [
            (a_id, a_word, b_id, b_word)
            for (a_id, a_word), (b_id, b_word) in relationships
        ],
        columns=["id1", "word1", "id2", "word2"],
    )


candidates_df = find_candidate_relationships(df)

st.title("Approve Word Relationships")

approved_rows = []

for _, row in candidates_df.iterrows():
    st.write(f"**{row['word1']} ↔ {row['word2']}**")
    approve = st.radio(
        "Approve this relationship?",
        ("No", "Yes"),
        key=f"{row['id1']}_{row['id2']}",
    )

    if approve == "Yes":
        approved_rows.append((row["id1"], row["id2"]))

if st.button("Save approved relationships"):
    with conn:
        for id1, id2 in approved_rows:
            # Ensure correct ordering
            word_id1, word_id2 = sorted((id1, id2))
            try:
                c.execute(
                    """
                    INSERT INTO WordRelationship (word_id1, word_id2)
                    VALUES (?, ?)
                """,
                    (word_id1, word_id2),
                )
            except sqlite3.IntegrityError:
                # Skip duplicates or constraint violations
                pass
    st.success(f"{len(approved_rows)} relationships saved.")
