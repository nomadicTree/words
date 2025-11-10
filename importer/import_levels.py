from importer.yaml_utils import load_yaml
from importer.db_utils import db_connection, get_or_create_level


def import_levels(levels_path, db_path):
    """
    Imports all levels from YAML into the Levels table.
    """
    levels_data = load_yaml(levels_path).get("levels", [])
    if not levels_data:
        print("⚠️  No levels found in YAML.")
        return

    with db_connection(db_path) as conn:
        for level in levels_data:
            name = level["name"].strip()
            description = (level.get("description") or "").strip()
            get_or_create_level(conn, name, description)

    print(f"✓ Imported {len(levels_data)} levels.")
