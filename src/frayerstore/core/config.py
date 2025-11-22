from pathlib import Path

CONFIG_FILE = Path(__file__).resolve()
CORE_DIR = CONFIG_FILE.parent
PACKAGE_ROOT = CORE_DIR.parent
SRC_ROOT = PACKAGE_ROOT.parent
PROJECT_ROOT = SRC_ROOT.parent

DATA_DIR = PROJECT_ROOT / "data"
DB_DIR = DATA_DIR / "db"
YAML_DIR = DATA_DIR / "yaml"

DB_PATH = DB_DIR / "frayerstore.sqlite3"
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.toml"

SCHEMA_PATH = PACKAGE_ROOT / "db" / "migrations" / "schema.sql"
