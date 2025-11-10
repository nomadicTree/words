import os

# Resolve paths relative to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG = {
    "database": os.path.join(PROJECT_ROOT, "db", "Words.db"),
    "data_root": os.path.join(PROJECT_ROOT, "yaml_data"),
    "subjects_root": os.path.join(PROJECT_ROOT, "yaml_data", "subjects"),
}

# Optional sanity check (helpful if paths change)
for key, path in CONFIG.items():
    if not os.path.exists(os.path.dirname(path)):
        print(
            f"⚠️  Warning: directory for {key} does not exist → {os.path.dirname(path)}"
        )
