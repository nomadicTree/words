from frayerstore.importer.models import ImportSubject


def test_import_item_with_id():
    item = ImportSubject(id=None, name="Computing", slug="computing")
    new_item = item.with_id(10)
    assert new_item.id == 10
    assert new_item.name == "Computing"
    assert new_item.slug == "computing"
