from __future__ import annotations
import sqlite3
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate
from frayerstore.db.interfaces.level_repo import LevelRepository
from frayerstore.db.sqlite.level_mapper import LevelMapper


class SQLiteLevelRepository(LevelRepository):
    def __init__(
        self, conn: sqlite3.Connection, mapper: LevelMapper
    ) -> SQLiteLevelRepository:
        self.conn = conn
        self.mapper = mapper

    def get_by_slug(self, slug: str) -> Level:
        q = """
        SELECT * FROM Levels WHERE slug=?
        """
        row = self.conn.execute(q, (slug,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_name(self, name: str) -> Level:
        q = """
        SELECT * FROM Levels WHERE name=?
        """
        row = self.conn.execute(q, (name,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def get_by_id(self, id: str) -> Level:
        q = """
        SELECT * FROM Levels WHERE id=?
        """
        row = self.conn.execute(q, (id,)).fetchone()
        return self.mapper.row_to_domain(row) if row else None

    def create(self, data: LevelCreate) -> Level:
        params = self.mapper.create_to_params(data)
        q = """
        INSERT INTO Levels (name, slug, category, number)
        VALUES (?, ?, ?, ?)
        RETURNING id, name, slug, category, number
        """
        row = self.conn.execute(q, params).fetchone()
        return self.mapper.row_to_domain(row)
