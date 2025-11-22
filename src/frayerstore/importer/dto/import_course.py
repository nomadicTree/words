from __future__ import annotations
from dataclasses import dataclass

from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportCourse(ImportItem):
    subject_pk: int
    level_pk: int

    @classmethod
    def from_yaml(cls, data: dict, *, subject_pk: int, level_pk: int) -> ImportCourse:
        if not isinstance(data, dict):
            raise InvalidYamlStructure("Course must be a mapping")

        name = data.get("name")
        if not name or not isinstance(name, str) or not name.strip():
            raise InvalidYamlStructure("Course missing required field 'name'")

        name = name.strip()
        slug = slugify(name)
        return cls(subject_pk=subject_pk, level_pk=level_pk, name=name, slug=slug)
