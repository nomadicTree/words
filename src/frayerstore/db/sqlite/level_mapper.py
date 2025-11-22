import sqlite3
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate


class LevelMapper:
    def row_to_domain(self, row: sqlite3.Row) -> Level:
        return Level(
            pk=row["id"],
            name=row["name"],
            slug=row["slug"],
            category=row["category"],
            number=row["number"],
        )

    def create_to_params(self, data: LevelCreate) -> tuple:
        return (data.name, data.slug, data.category, data.number)
