import pytest
from frayerstore.importer.subjects import import_subject
from frayerstore.importer.exceptions import SubjectImportCollision
from frayerstore.importer.report import ImportReport


def test_import_single_subject(schema_db, subjects_path):
    subject_yaml = subjects_path / "computing.yaml"
    report = ImportReport()
    import_subject(schema_db, subject_yaml, report)
    row = schema_db.execute(
        "SELECT * FROM Subjects WHERE name = 'Computing';"
    ).fetchone()
    assert row is not None
    assert row["name"] == "Computing"
    assert row["slug"] == "computing"
    count = schema_db.execute("SELECT COUNT(*) FROM Subjects").fetchone()[0]
    assert count == 1
    assert len(report.subjects.created) == 1
    assert len(report.subjects.skipped) == 0
    assert len(report.subjects.errors) == 0


def test_import_multiple_subjects(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    report = ImportReport()

    a.write_text("subject: Computing")
    b.write_text("subject: Maths")

    import_subject(schema_db, a, report)
    import_subject(schema_db, b, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert names == {"Computing", "Maths"}
    assert len(report.subjects.created) == 2
    assert len(report.subjects.skipped) == 0
    assert len(report.subjects.errors) == 0


def test_subject_name_collision(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    report = ImportReport()

    a.write_text("subject: Computing")
    b.write_text("subject: Computing")

    import_subject(schema_db, a, report)
    import_subject(schema_db, b, report)
    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 1
    assert len(report.subjects.created) == 1
    assert len(report.subjects.skipped) == 1
    assert len(report.subjects.errors) == 0


def test_subject_slug_is_derived(schema_db, tmp_path):
    yaml = tmp_path / "sub.yaml"
    report = ImportReport()
    yaml.write_text("subject: Computer Science")

    import_subject(schema_db, yaml, report)

    row = schema_db.execute("SELECT slug FROM Subjects").fetchone()
    assert row["slug"] == "computer-science"


@pytest.mark.parametrize(
    "name, expected_slug",
    [
        ("Computing", "computing"),
        ("Computer Science", "computer-science"),
        ("  Data   Structures ", "data-structures"),
        ("AI & ML", "ai-ml"),
        ("C++ Programming", "c-programming"),
    ],
)
def test_slug_derivation_rules(schema_db, tmp_path, name, expected_slug):
    file = tmp_path / "sub.yaml"
    report = ImportReport()
    file.write_text(f"subject: {name}")

    import_subject(schema_db, file, report)
    slug = schema_db.execute("SELECT slug FROM Subjects").fetchone()["slug"]
    assert slug == expected_slug


def test_slug_collision(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"
    report = ImportReport()

    a.write_text("subject: Class")
    b.write_text("subject: class")

    import_subject(schema_db, a, report)
    with pytest.raises(SubjectImportCollision):
        import_subject(schema_db, b, report)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 1
    assert len(report.subjects.created) == 1
    assert len(report.subjects.skipped) == 0
    assert len(report.subjects.errors) == 1
