from __future__ import annotations
from dataclasses import dataclass

from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.utils import missing_required_field_message
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportLevel(ImportItem):
    category: str
    number: str

    @classmethod
    def from_yaml(cls, data: dict) -> ImportLevel:
        required_fields = ["category", "number"]

        for field in required_fields:
            message = missing_required_field_message("Level", field)
            value = data.get(field)
            if value is None:
                raise InvalidYamlStructure(message)

            if not isinstance(value, str):
                raise InvalidYamlStructure(message)

            if not value.strip():
                raise InvalidYamlStructure(message)

        category = str(data["category"]).strip()
        number = str(data["number"]).strip()

        full_name = f"{category} {number}"

        abbreviation = "".join(word[0] for word in category.split())
        short_label = f"{abbreviation}{number}"

        slug = short_label.lower()

        return cls(name=full_name, slug=slug, category=category, number=number)
