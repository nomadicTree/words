import sqlite3
from pathlib import Path
from .yaml_utils import load_yaml
from .exceptions import SubjectImportError, SubjectImportCollision
from .db import get_subject_by_name, get_subject_by_slug
from .models import ImportSubject
from .report import ImportReport
from .identity import import_with_identity


def import_subject(
    conn: sqlite3.Connection, yaml_path: Path, report: ImportReport
) -> ImportSubject:
    """Import a unique subject to the database"""
    data = load_yaml(yaml_path)
    incoming = ImportSubject.from_yaml(data)

    # Fetch DB matches
    slug_row = get_subject_by_slug(conn, incoming.slug)
    name_row = get_subject_by_name(conn, incoming.name)

    existing_by_slug = ImportSubject.from_row(slug_row) if slug_row else None
    existing_by_name = ImportSubject.from_row(name_row) if name_row else None

    return import_with_identity(
        conn,
        incoming,
        existing_by_slug=existing_by_slug,
        existing_by_name=existing_by_name,
        stage_report=report.subjects,
        exception_type=SubjectImportCollision,
    )
