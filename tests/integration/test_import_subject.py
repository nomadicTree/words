import pytest
from frayerstore.importer.import_subjects import import_subject
from frayerstore.importer.exceptions import (
    SubjectImportError,
    SubjectImportCollision,
)


def test_import_single_subject(schema_db, subjects_path):
    subject_yaml = subjects_path / "computing.yaml"
    import_subject(schema_db, subject_yaml)
    row = schema_db.execute(
        "SELECT * FROM Subjects WHERE name = 'Computing';"
    ).fetchone()
    assert row is not None
    assert row["name"] == "Computing"
    assert row["slug"] == "computing"
    count = schema_db.execute("SELECT COUNT(*) FROM Subjects").fetchone()[0]
    assert count == 1


def test_import_multiple_subjects(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"

    a.write_text("name: Computing")
    b.write_text("name: Maths")

    import_subject(schema_db, a)
    import_subject(schema_db, b)

    rows = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert len(rows) == 2
    names = {r["name"] for r in rows}
    assert names == {"Computing", "Maths"}


def test_subject_name_collision(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"

    a.write_text("name: Computing")
    b.write_text("name: Computing")

    import_subject(schema_db, a)
    with pytest.raises(SubjectImportCollision):
        import_subject(schema_db, b)


def test_subject_slug_is_derived(schema_db, tmp_path):
    yaml = tmp_path / "sub.yaml"
    yaml.write_text("name: Computer Science")

    import_subject(schema_db, yaml)

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
    file.write_text(f"name: {name}")

    import_subject(schema_db, file)
    slug = schema_db.execute("SELECT slug FROM Subjects").fetchone()["slug"]
    assert slug == expected_slug


def test_slug_collision(schema_db, tmp_path):
    a = tmp_path / "a.yaml"
    b = tmp_path / "b.yaml"

    a.write_text("name: Class")
    b.write_text("name: class")

    import_subject(schema_db, a)

    with pytest.raises(SubjectImportCollision):
        import_subject(schema_db, b)
