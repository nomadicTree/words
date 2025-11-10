import yaml
import json
import os
from pathlib import Path


def resolve_path(root, relative_path):
    return Path(root, relative_path)


# ---------- basic YAML file helpers ---------- #


def load_yaml(path):
    """Safely load a YAML file and return its contents as a dict."""
    if not os.path.exists(path):
        print(f"⚠️  YAML file not found: {path}")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            if data is None:
                data = {}
            return data
    except yaml.YAMLError as e:
        print(f"⚠️  YAML parse error in {path}: {e}")
        return {}
    except Exception as e:
        print(f"⚠️  Error reading {path}: {e}")
        return {}


def load_word_file(path):
    """Load a single word YAML file and ensure it has a 'word' key."""
    data = load_yaml(path)
    if not data or "word" not in data:
        print(f"⚠️  Skipping invalid YAML (missing 'word'): {path}")
        return None
    return data


# ---------- data cleaning helpers ---------- #


def clean_list(items):
    """Convert a list of strings/numbers to a JSON string of stripped values."""
    return json.dumps(
        [
            str(i).strip()
            for i in (items or [])
            if isinstance(i, (str, int, float))
        ]
    )
