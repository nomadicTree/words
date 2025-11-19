import pytest
import sqlite3
from pathlib import Path

import sys

# Point Python at the src/ directory so `import frayerstore` works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


@pytest.fixture
def empty_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture
def schema_db(empty_db):
    import frayerstore.paths as paths

    schema_sql = (paths.DB_DIR / "schema.sql").read_text()
    empty_db.executescript(schema_sql)
    return empty_db


@pytest.fixture
def fixtures_path():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def subjects_path(fixtures_path):
    return Path(fixtures_path / "subjects")
