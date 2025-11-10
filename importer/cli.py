import argparse
import os
from importer import (
    import_levels,
    import_subjects,
    import_words,
)
from importer.config import CONFIG


def main():
    parser = argparse.ArgumentParser(
        description="Import data into the Words database."
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("levels", help="Import levels from levels.yaml")
    subparsers.add_parser(
        "subjects", help="Import subjects, courses, and topics"
    )
    subparsers.add_parser(
        "words",
        help="Import words recursively from each subject's 'words' directory",
    )
    subparsers.add_parser(
        "all", help="Run all imports in sequence (levels, subjects, words)"
    )

    args = parser.parse_args()

    db_path = CONFIG["database"]
    data_root = CONFIG["data_root"]
    subjects_root = CONFIG["subjects_root"]

    if not os.path.exists(db_path):
        print(f"⚠️  Database not found at: {db_path}")
        return

    if args.command == "levels":
        levels_path = os.path.join(data_root, "levels.yaml")
        if not os.path.exists(levels_path):
            print(f"⚠️  levels.yaml not found in {data_root}")
            return
        import_levels.import_levels(levels_path, db_path)

    elif args.command == "subjects":
        subjects_yaml_path = os.path.join(data_root, "subjects.yaml")
        if not os.path.exists(subjects_yaml_path):
            print(f"⚠️  subjects.yaml not found in {data_root}")
            return
        import_subjects.import_subjects(
            subjects_yaml_path, subjects_root, db_path
        )

    elif args.command == "words":
        if not os.path.exists(subjects_root):
            print(f"⚠️  Subjects root not found at: {subjects_root}")
            return
        import_words.import_words(subjects_root, db_path)

    elif args.command == "all":
        print("🧩 Importing all data...")
        levels_path = os.path.join(data_root, "levels.yaml")
        subjects_yaml_path = os.path.join(data_root, "subjects.yaml")

        import_levels.import_levels(levels_path, db_path)
        import_subjects.import_subjects(
            subjects_yaml_path, subjects_root, db_path
        )
        import_words.import_words(subjects_root, db_path)
        print("✅ All imports completed.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
