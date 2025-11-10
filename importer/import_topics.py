from importer.db_utils import get_or_create_topic


def import_topics(conn, course_id: int, topics: list):
    """
    Inserts or updates topics for a given course.
    """
    if not topics:
        print(f"  ⚠️  No topics found for course_id {course_id}.")
        return

    for topic in topics:
        code = topic["code"].strip()
        name = (topic.get("name") or "").strip()
        get_or_create_topic(conn, course_id, code, name)

    print(f"  ✓ Imported {len(topics)} topics for course_id {course_id}.")
