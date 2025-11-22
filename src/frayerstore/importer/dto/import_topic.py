from __future__ import annotations
from dataclasses import dataclass
from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_item import ImportItem


@dataclass(frozen=True)
class ImportTopic(ImportItem):
    course_pk: int
    code: str

    @classmethod
    def from_yaml(cls, data: dict, *, course_pk: int) -> "ImportTopic":
        if not isinstance(data, dict):
            raise InvalidYamlStructure("Topic must be a mapping")

        code = data.get("code")
        if not isinstance(code, str) or not code.strip():
            raise InvalidYamlStructure("Topic missing required field 'code'")

        name = data.get("name")
        if not isinstance(name, str) or not name.strip():
            raise InvalidYamlStructure("Topic missing required field 'name'")
        name = name.strip()

        return cls(
            course_pk=course_pk,
            code=code.strip(),
            name=name,
            slug=slugify(name),
        )
