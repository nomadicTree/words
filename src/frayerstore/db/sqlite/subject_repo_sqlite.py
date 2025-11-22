from __future__ import annotations
import sqlite3
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate
from frayerstore.db.interfaces.subject_repo import SubjectRepository
from frayerstore.db.sqlite.subject_mapper import SubjectMapper


class SQLiteSubjectRepository(SubjectRepository):
    def __init__(
        self, conn: sqlite3.Connection, mapper: SubjectMapper
    ) -> SQLiteSubjectRepository:
        self.conn = conn
        self.mapper = mapper

    def get_by_slug(self, slug: str) -> Subject:
        q = """
        SELECT * FROM Subjects WHERE slug=?
        """
        row = self.conn.execute(q, (slug,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_name(self, name: str) -> Subject:
        q = """
        SELECT * FROM Subjects WHERE name=?
        """
        row = self.conn.execute(q, (name,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_id(self, id: int) -> Subject:
        q = """
        SELECT * FROM Subjects WHERE id=?
        """
        row = self.conn.execute(q, (id,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def create(self, data: SubjectCreate) -> Subject:
        params = self.mapper.create_to_params(data)
        q = """
        INSERT INTO Subjects (name, slug)
        VALUES (?, ?)
        RETURNING id, name, slug
        """
        row = self.conn.execute(q, params).fetchone()
        return self.mapper.row_to_domain(row)
