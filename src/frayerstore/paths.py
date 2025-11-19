from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.toml"
DATA_DIR = PACKAGE_ROOT / "data"
DB_PATH = DATA_DIR / "frayerstore.db"
