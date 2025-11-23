from pathlib import Path
import yaml

import shutil
import time

from frayerstore.importer.report import ImportReport
from frayerstore.importer.coordinators.subject_coordinator import (
    SubjectImportCoordinator,
)
from frayerstore.importer.coordinators.level_coordinator import LevelImportCoordinator
from frayerstore.importer.coordinators.course_coordinator import (
    CourseImportCoordinator,
)
from frayerstore.importer.coordinators.topic_coordinator import TopicImportCoordinator
from frayerstore.importer.services.import_services import (
    SubjectImportService,
    LevelImportService,
    CourseImportService,
)
from frayerstore.importer.services.topic_import_service import TopicImportService
from frayerstore.db.sqlite.subject_mapper import SubjectMapper
from frayerstore.db.sqlite.level_mapper import LevelMapper
from frayerstore.db.sqlite.course_mapper import CourseMapper
from frayerstore.db.sqlite.topic_mapper import TopicMapper
from frayerstore.db.sqlite.subject_repo_sqlite import SQLiteSubjectRepository
from frayerstore.db.sqlite.level_repo_sqlite import SQLiteLevelRepository
from frayerstore.db.sqlite.course_repo_sqlite import SQLiteCourseRepository
from frayerstore.db.sqlite.topic_repo_sqlite import SQLiteTopicRepository

from frayerstore.core.config.paths import SUBJECTS_YAML_PATH, DB_BACKUP_DIR, DB_PATH
from frayerstore.db.connection import get_db_uncached


def build_subject_coordinator(conn):
    """Wire up real SQLite repos/services/coordinators for end-to-end import."""
    subject_mapper = SubjectMapper()
    level_mapper = LevelMapper()
    course_mapper = CourseMapper(level_mapper)
    topic_mapper = TopicMapper()

    topic_repo = SQLiteTopicRepository(conn, topic_mapper)
    course_repo = SQLiteCourseRepository(conn, course_mapper, topic_repo)
    level_repo = SQLiteLevelRepository(conn, level_mapper)
    subject_repo = SQLiteSubjectRepository(conn, subject_mapper, course_repo)

    subject_service = SubjectImportService(subject_repo)
    level_service = LevelImportService(level_repo)
    course_service = CourseImportService(course_repo)
    topic_service = TopicImportService(topic_repo)

    topic_coord = TopicImportCoordinator(topic_service)
    course_coord = CourseImportCoordinator(course_service, topic_coord)
    level_coord = LevelImportCoordinator(level_service, course_coord)
    return SubjectImportCoordinator(subject_service, level_coord)


def run_full_import(conn, path: Path):
    coordinator = build_subject_coordinator(conn)
    report = ImportReport()
    data = yaml.safe_load(path.read_text())
    for subj in data["subjects"]:
        coordinator.import_subject(subj, report)
    return report


def main():
    DB_BACKUP_DIR.mkdir(exist_ok=True)

    # Timestamp for uniqueness
    timestamp = time.strftime("%Y%m%d-%H%M%S")

    # Move original DB to backups/
    archived_path = DB_BACKUP_DIR / f"frayerstore-{timestamp}.sqlite3"
    shutil.move(DB_PATH, archived_path)

    # Create a fresh working copy
    shutil.copy(archived_path, DB_PATH) 
    conn = get_db_uncached()
    try:
        run_full_import(conn, SUBJECTS_YAML_PATH)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
