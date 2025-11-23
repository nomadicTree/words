from pathlib import Path
import yaml

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


def build_subject_coordinator(conn):
    """Wire up real SQLite repos/services/coordinators for end-to-end import tests."""
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


def write_full_hierarchy_yaml(path: Path):
    data = {
        "subjects": [
            {
                "name": "Computing",
                "levels": [
                    {
                        "name": "KS4",
                        "courses": [
                            {
                                "name": "Algorithms",
                                "topics": [
                                    {"code": "A1", "name": "Arrays"},
                                    {"code": "A2", "name": "Loops"},
                                ],
                            },
                            {
                                "name": "Data Structures",
                                "topics": [
                                    {"code": "DS1", "name": "Trees"},
                                ],
                            },
                        ],
                    },
                    {
                        "name": "KS5",
                        "courses": [
                            {
                                "name": "Advanced CS",
                                "topics": [
                                    {"code": "AC1", "name": "Complexity"},
                                ],
                            }
                        ],
                    },
                ],
            },
            {
                "name": "Maths",
                "levels": [
                    {
                        "name": "KS4",
                        "courses": [
                            {
                                "name": "Algebra",
                                "topics": [
                                    {"code": "M1", "name": "Linear Equations"},
                                ],
                            }
                        ],
                    }
                ],
            },
        ]
    }
    path.write_text(yaml.safe_dump(data))


def run_full_import(conn, path: Path):
    coordinator = build_subject_coordinator(conn)
    report = ImportReport()
    data = yaml.safe_load(path.read_text())
    for subj in data["subjects"]:
        coordinator.import_subject(subj, report)
    return report


def test_full_import_pipeline_creates_hierarchy(schema_db, tmp_path):
    yaml_path = tmp_path / "full_import.yaml"
    write_full_hierarchy_yaml(yaml_path)

    report = run_full_import(schema_db, yaml_path)

    # Subjects
    subjects = schema_db.execute("SELECT * FROM Subjects").fetchall()
    assert {row["name"] for row in subjects} == {"Computing", "Maths"}

    # Levels
    levels = schema_db.execute("SELECT * FROM Levels").fetchall()
    assert {row["name"] for row in levels} == {"KS4", "KS5"}

    # Courses
    courses = schema_db.execute("SELECT id, name, slug, subject_id, level_id FROM Courses").fetchall()
    course_names = {row["name"] for row in courses}
    assert course_names == {"Algorithms", "Data Structures", "Advanced CS", "Algebra"}

    # Topics
    topics = schema_db.execute("SELECT code, name FROM Topics").fetchall()
    topic_codes = {row["code"] for row in topics}
    assert topic_codes == {"A1", "A2", "DS1", "AC1", "M1"}

    # Relationships: Algorithms topics belong to Algorithms course
    alg_course_id = next(r["id"] for r in courses if r["name"] == "Algorithms")
    alg_topics = schema_db.execute(
        "SELECT code FROM Topics WHERE course_id = ?", (alg_course_id,)
    ).fetchall()
    assert {r["code"] for r in alg_topics} == {"A1", "A2"}

    # Validate report tracking
    assert len(report.subjects.created) == 2
    assert len(report.levels.created) == 2  # KS4, KS5 (KS4 reused across subjects)
    assert len(report.levels.skipped) == 1  # second KS4 skipped
    assert len(report.courses.created) == 4
    assert len(report.topics.created) == 5
    assert not report.subjects.errors
    assert not report.levels.errors
    assert not report.courses.errors
    assert not report.topics.errors


def test_full_import_pipeline_is_idempotent(schema_db, tmp_path):
    yaml_path = tmp_path / "full_import.yaml"
    write_full_hierarchy_yaml(yaml_path)

    first = run_full_import(schema_db, yaml_path)
    second = run_full_import(schema_db, yaml_path)

    # Database counts stay the same after second import
    assert schema_db.execute("SELECT COUNT(*) FROM Subjects").fetchone()[0] == 2
    assert schema_db.execute("SELECT COUNT(*) FROM Levels").fetchone()[0] == 2
    assert schema_db.execute("SELECT COUNT(*) FROM Courses").fetchone()[0] == 4
    assert schema_db.execute("SELECT COUNT(*) FROM Topics").fetchone()[0] == 5

    # First run created everything, second run skipped everything
    assert len(first.subjects.created) == 2
    assert len(second.subjects.created) == 0
    assert len(second.subjects.skipped) == 2

    assert len(first.levels.created) == 2
    assert len(second.levels.created) == 0
    assert len(second.levels.skipped) == 3  # KS4 appears twice, KS5 once

    assert len(first.courses.created) == 4
    assert len(second.courses.created) == 0
    assert len(second.courses.skipped) == 4

    assert len(first.topics.created) == 5
    assert len(second.topics.created) == 0
    assert len(second.topics.skipped) == 5
