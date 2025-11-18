import streamlit as st
from app.services.search.search_models import SearchHit, SearchFilters
from app.core.repositories.search_repo import search_raw
from app.core.db import get_db


@st.cache_data
def get_subject_level_map() -> dict[int, set[str]]:
    """
    Returns a mapping: subject_id -> set of level names that actually appear
    in vw_SearchWordVersions.
    """
    db = get_db()

    rows = db.execute("""
        SELECT subject_id, level_names
        FROM vw_SearchWordVersions
        GROUP BY subject_id, level_names
    """).fetchall()

    mapping: dict[int, set[str]] = {}

    for r in rows:
        subject_id = r["subject_id"]
        level_names = r["level_names"].split(",") if r["level_names"] else []

        if subject_id not in mapping:
            mapping[subject_id] = set()

        mapping[subject_id].update(level_names)

    return mapping


def find_match_token(query: str, word: str, synonyms: list[str]) -> str | None:
    q = query.lower()

    # Check word tokens
    for token in word.split():
        if q in token.lower():
            return token

    # Check synonym tokens
    for syn in synonyms:
        for token in syn.split():
            if q in token.lower():
                return token

    return None


def search_words(query: str, filters: SearchFilters) -> list[SearchHit]:
    # Stage 1: raw SQL hits
    hits = search_raw(query, filters)

    # Stage 2: level filtering
    if filters.level:
        wanted = filters.level.name
        hits = [h for h in hits if wanted in h.level_names]

    # Stage 3: token matching
    for h in hits:
        h.matched_token = find_match_token(query, h.word, h.synonyms)

    return hits
