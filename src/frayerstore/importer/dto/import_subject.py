from __future__ import annotations
from dataclasses import dataclass
from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportSubject(ImportItem):
    @classmethod
    def from_yaml(cls, data: dict) -> ImportSubject:
        if "name" not in data or not data["name"].strip():
            raise InvalidYamlStructure(
                "Subject definition missing required field 'name'."
            )
        name = data["name"].strip()
        slug = slugify(name)
        return cls(name=name, slug=slug)
