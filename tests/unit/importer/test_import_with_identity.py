import pytest

from frayerstore.importer.identity import import_with_identity
from frayerstore.importer.subjects import ImportSubject
from frayerstore.importer.exceptions import SubjectImportCollision


def make_subj(id, name, slug):
    return ImportSubject(id=id, name=name, slug=slug)


def test_import_with_identity_returns_existing(schema_db, stage_report):
    incoming = make_subj(None, "Computing", "computing")
    existing = make_subj(1, "Computing", "computing")

    out = import_with_identity(
        schema_db,
        incoming,
        existing_by_slug=existing,
        existing_by_name=None,
        stage_report=stage_report,
        exception_type=SubjectImportCollision,
    )

    assert out == existing
    assert stage_report.skipped == [existing]
    assert stage_report.created == []


def test_import_with_identity_creates_new(schema_db, stage_report, monkeypatch):
    incoming = make_subj(None, "Computing", "computing")

    monkeypatch.setattr(
        ImportSubject,
        "create_in_db",
        classmethod(lambda cls, conn, inc: inc.with_id(42)),
    )

    out = import_with_identity(
        schema_db,
        incoming,
        existing_by_slug=None,
        existing_by_name=None,
        stage_report=stage_report,
        exception_type=SubjectImportCollision,
    )

    assert out.id == 42
    assert stage_report.created == [out]


def test_import_with_identity_raises_on_error(schema_db, stage_report):
    incoming = make_subj(None, "A", "a")
    existing = make_subj(1, "Different", "a")  # mismatched → error

    with pytest.raises(SubjectImportCollision):
        import_with_identity(
            schema_db,
            incoming,
            existing_by_slug=existing,
            existing_by_name=None,
            stage_report=stage_report,
            exception_type=SubjectImportCollision,
        )

    assert stage_report.errors  # error was recorded
