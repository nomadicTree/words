from src.frayerstore.importer.import_subjects import import_subject


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
