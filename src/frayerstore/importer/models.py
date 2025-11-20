from __future__ import annotations
from dataclasses import dataclass, replace
from abc import ABC, abstractmethod
import sqlite3
from frayerstore.core.utils.slugify import slugify
from .exceptions import InvalidYamlStructure


@dataclass(frozen=True)
class ImportItem(ABC):
    id: int | None
    name: str
    slug: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> ImportItem:
        return cls(id=row["id"], name=row["name"], slug=row["slug"])

    @classmethod
    @abstractmethod
    def from_yaml(cls, data: dict) -> ImportItem:
        pass

    @classmethod
    @abstractmethod
    def create_in_db(cls, conn: sqlite3.Row, incoming: ImportItem) -> ImportItem:
        pass

    def with_id(self, new_id: int) -> ImportItem:
        """Return a copy of this item with a new id."""
        return replace(self, id=new_id)


@dataclass(frozen=True)
class ImportSubject(ImportItem):
    @classmethod
    def from_yaml(cls, data: dict) -> ImportSubject:
        if "subject" not in data or not data["subject"].strip():
            raise InvalidYamlStructure(
                "Subject definition missing required field 'subject'."
            )
        name = data["subject"].strip()
        slug = slugify(name)
        return cls(id=None, name=name, slug=slug)

    @classmethod
    def create_in_db(cls, conn: sqlite3.Row, incoming: ImportSubject) -> ImportSubject:
        from .db import insert_subject

        new_id = insert_subject(conn, incoming)
        return incoming.with_id(new_id)
