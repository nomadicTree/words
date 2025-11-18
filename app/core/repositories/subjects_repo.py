from app.core.db import get_db
from app.core.models.subject_model import Subject


def get_all_subjects():
    """Get all Subjects

    Returns:
        List of all Subjects
    """
    db = get_db()

    q = """
        SELECT * FROM Subjects
    """
    rows = db.execute(q).fetchall()

    subjects = [Subject(pk=r["id"], name=r["name"], slug=r["slug"]) for r in rows]

    return subjects
