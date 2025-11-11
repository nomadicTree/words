from importer.yaml_utils import load_yaml
from importer.import_topics import import_topics
from importer.db_utils import (
    db_connection,
    get_or_create_course,
    get_or_create_level,
)


def import_course(conn, subject_id: int, course_path):
    """
    Imports a single course and its topics.
    """
    course_data = load_yaml(course_path)
    course_name = course_data["name"].strip()
    level_name = (course_data.get("level") or "").strip() or None
    topics = course_data.get("topics", [])

    # Resolve or create level_id
    level_id = None
    if level_name:
        level_id = get_or_create_level(conn, level_name)

    # Insert or retrieve course
    course_id = get_or_create_course(conn, subject_id, course_name, level_id)

    # Import topics
    import_topics(conn, course_id, topics)

    print(
        f"✓ Imported course '{course_name}' (level={level_name or 'N/A'}) with {len(topics)} topics."
    )
