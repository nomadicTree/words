import pytest

from frayerstore.importer.dto.import_topic import ImportTopic
from frayerstore.importer.exceptions import InvalidYamlStructure


def test_from_yaml_builds_topic():
    incoming = ImportTopic.from_yaml({"code": "CS1", "name": "Intro"}, course_pk=5)

    assert incoming.course_pk == 5
    assert incoming.code == "CS1"
    assert incoming.name == "Intro"
    assert incoming.slug == "intro"


def test_from_yaml_strips_fields():
    incoming = ImportTopic.from_yaml({"code": "  CS1  ", "name": "  Intro  "}, course_pk=1)

    assert incoming.code == "CS1"
    assert incoming.name == "Intro"
    assert incoming.slug == "intro"


def test_from_yaml_rejects_invalid_structures():
    with pytest.raises(InvalidYamlStructure):
        ImportTopic.from_yaml("not a dict", course_pk=1)

    with pytest.raises(InvalidYamlStructure):
        ImportTopic.from_yaml({"name": "Intro"}, course_pk=1)

    with pytest.raises(InvalidYamlStructure):
        ImportTopic.from_yaml({"code": "CS1"}, course_pk=1)

    with pytest.raises(InvalidYamlStructure):
        ImportTopic.from_yaml({"code": "", "name": "Intro"}, course_pk=1)

    with pytest.raises(InvalidYamlStructure):
        ImportTopic.from_yaml({"code": "CS1", "name": "   "}, course_pk=1)
