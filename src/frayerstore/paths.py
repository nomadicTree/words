from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.toml"
DATA_DIR = PACKAGE_ROOT / "data"
DB_DIR = DATA_DIR / "db"
YAML_DIR = DATA_DIR / "yaml"
DB_PATH = DB_DIR / "frayerstore.db"
SCHEMA_PATH = DB_DIR / "schema.sql"
