import os
from importer.yaml_utils import load_yaml
from importer.import_courses import import_course
from importer.db_utils import db_connection, get_or_create_subject


def import_subjects(subjects_yaml_path, subjects_root, db_path):
    """
    Imports subjects and their courses (and topics) from YAML.
    """
    data = load_yaml(subjects_yaml_path)
    subjects = data.get("subjects", [])
    if not subjects:
        print("⚠️  No subjects found in YAML.")
        return

    with db_connection(db_path) as conn:
        for subj in subjects:
            subject_name = subj["name"].strip()
            subject_id = get_or_create_subject(conn, subject_name)
            print(f"✓ Imported subject '{subject_name}'")

            for course_ref in subj.get("courses", []):
                rel_path = course_ref["file"].strip()
                course_path = os.path.join(subjects_root, rel_path)
                if not os.path.exists(course_path):
                    print(f"⚠️  Missing course file: {course_path}")
                    continue

                # ✅ pass the existing connection instead of db_path
                import_course(conn, subject_id, course_path)
