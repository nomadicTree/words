from src.frayerstore import paths
from src.frayerstore.core.db import open_db_at


def main():
    schema_path = paths.SCHEMA_PATH
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    db_path = paths.DB_PATH
    if db_path.exists():
        raise FileExistsError(f"Database already exists: {db_path}")

    print(f"Creating DB at {db_path}")
    print(f"Using schema from {schema_path}")

    conn = open_db_at(db_path)
    schema_sql = schema_path.read_text()
    conn.executescript(schema_sql)
    conn.close()

    print("Done")


if __name__ == "__main__":
    main()
