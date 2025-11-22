import pytest

from frayerstore.importer.dto.import_course import ImportCourse
from frayerstore.importer.exceptions import InvalidYamlStructure


def test_from_yaml_builds_course_and_slugifies_name():
    incoming = ImportCourse.from_yaml({"name": "  Intro to CS  "}, subject_pk=7, level_pk=3)

    assert incoming.name == "Intro to CS"
    assert incoming.slug == "intro-to-cs"
    assert incoming.subject_pk == 7
    assert incoming.level_pk == 3


def test_from_yaml_rejects_non_mapping():
    with pytest.raises(InvalidYamlStructure):
        ImportCourse.from_yaml("not a dict", subject_pk=1, level_pk=1)


def test_from_yaml_requires_non_empty_name():
    with pytest.raises(InvalidYamlStructure):
        ImportCourse.from_yaml({"name": "   "}, subject_pk=1, level_pk=1)

    with pytest.raises(InvalidYamlStructure):
        ImportCourse.from_yaml({}, subject_pk=1, level_pk=1)
