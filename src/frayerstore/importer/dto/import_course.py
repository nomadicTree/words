from __future__ import annotations
from dataclasses import dataclass

from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.utils import missing_required_field_message
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportCourse(ImportItem):
    name: str
    subject_slug: str
    level_slug: str
    number: str

    @classmethod
    def from_yaml(cls, data: dict) -> ImportCourse:
        required_fields = ["name", "subject", "level", "topics"]

        for field in required_fields:
            message = missing_required_field_message("Course", field)
            value = data.get(field)
            if value is None:
                raise InvalidYamlStructure(message)

            if not isinstance(value, str):
                raise InvalidYamlStructure(message)

            if not value.strip():
                raise InvalidYamlStructure(message)

        name = str(data["name"]).strip()
        subject = str(data["subject"]).strip()
        level = str(data["level"]).strip()

        return cls(name=full_name, slug=slug, category=category, number=number)
