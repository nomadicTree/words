import pytest
import sqlite3
from pathlib import Path
from frayerstore.importer.report import ImportReport, ImportStageReport
from frayerstore.importer.exceptions import SubjectImportCollision


@pytest.fixture
def empty_db():
    """A completely blank in-memory SQLite database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def schema_db(empty_db):
    """
    A fresh in-memory DB with the full schema loaded.
    """
    import frayerstore.paths as paths

    schema_sql = (paths.DB_DIR / "schema.sql").read_text()
    empty_db.executescript(schema_sql)
    return empty_db


@pytest.fixture
def fixtures_path():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def subjects_path(fixtures_path):
    return Path(fixtures_path / "subjects")


@pytest.fixture
def report():
    """Full multi-stage importer report (subjects, courses, topics, words)."""
    return ImportReport()


@pytest.fixture
def stage_report():
    """Single-stage report, most commonly used in importer unit tests."""
    return ImportStageReport("TestStage")


@pytest.fixture
def subject_exception():
    """The exception that should be raised by subject importer tests."""
    return SubjectImportCollision
