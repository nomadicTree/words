from app.core.db import get_db
from app.core.models.level_model import Level


def get_all_levels() -> list[Level]:
    """Get all Levels

    Returns:
        List of all Levels
    """
    db = get_db()

    q = """
        SELECT * FROM Levels
    """
    rows = db.execute(q).fetchall()

    levels = [
        Level(
            pk=r["id"],
            name=r["name"],
            description=r["description"],
        )
        for r in rows
    ]

    return levels


def get_levels_for_subject(subject_id) -> list[Level]:
    """Get all Levels that have at least one Course for the given subject."""
    db = get_db()

    q = """
        SELECT DISTINCT
            l.id,
            l.name,
            l.description
        FROM Levels AS l
        JOIN Courses AS c ON c.level_id = l.id
        WHERE c.subject_id = :subject_id
        ORDER BY l.name
    """

    rows = db.execute(q, {"subject_id": subject_id}).fetchall()

    return [
        Level(
            pk=r["id"],
            name=r["name"],
            description=r["description"],
        )
        for r in rows
    ]
