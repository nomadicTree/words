from app.core.db import get_db
from app.services.search.search_models import SearchHit, SearchFilters


def search_raw(query: str, filters: SearchFilters) -> list[SearchHit]:
    db = get_db()
    q = query.strip()

    if not q:
        return []

    sql = """
        SELECT
            word_id,
            word,
            word_slug,
            subject_slug,
            version_id,
            version_definition,
            level_names,
            synonyms,
            search_text
        FROM vw_SearchWordVersions
        WHERE search_text LIKE :q
    """

    params = {"q": f"%{q}%"}

    if filters.subject:
        sql += " AND subject_id = :subj"
        params["subj"] = filters.subject.pk

    sql += " ORDER BY word COLLATE NOCASE;"

    rows = db.execute(sql, params).fetchall()
    hits: list[SearchHit] = []

    for r in rows:
        synonyms = r["synonyms"].split(",") if r["synonyms"] else []
        levels = r["level_names"].split(",") if r["level_names"] else []

        hits.append(
            SearchHit(
                word_id=r["word_id"],
                word=r["word"],
                word_slug=r["word_slug"],
                subject_slug=r["subject_slug"],
                version_id=r["version_id"],
                version_definition=r["version_definition"],
                level_names=levels,
                synonyms=synonyms,
                search_text=r["search_text"],
                matched_token=None,  # service will fill this
            )
        )

    return hits
