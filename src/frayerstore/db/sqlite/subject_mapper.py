import sqlite3
from frayerstore.models.subject import Subject


class SubjectMapper:
    def row_to_domain(self, row: sqlite3.Row) -> Subject:
        return Subject(pk=row["id"], name=row["name"], slug=row["slug"])

    def domain_to_params(self, subject: Subject) -> tuple:
        return (subject.name, subject.slug)
