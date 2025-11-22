from __future__ import annotations
from frayerstore.importer.exceptions import (
    LevelImportError,
    SubjectImportError,
    CourseImportError,
)
from frayerstore.importer.dto.import_level import ImportLevel
from frayerstore.db.interfaces.level_repo import LevelRepository
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate
from frayerstore.importer.services.generic_import_service import GenericImportService
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.db.interfaces.subject_repo import SubjectRepository
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate
from frayerstore.importer.dto.import_course import ImportCourse
from frayerstore.models.course_create import CourseCreate
from frayerstore.models.course import Course
from frayerstore.db.interfaces.course_repo import CourseRepository


class SubjectImportService(GenericImportService[ImportSubject, SubjectCreate, Subject]):
    def __init__(self, repo: SubjectRepository):
        super().__init__(
            repo=repo,
            create_factory=lambda inc: SubjectCreate(name=inc.name, slug=inc.slug),
            exception_type=SubjectImportError,
        )


class LevelImportService(GenericImportService[ImportLevel, LevelCreate, Level]):
    def __init__(self, repo: LevelRepository):
        super().__init__(
            repo=repo,
            create_factory=lambda incoming: LevelCreate(
                name=incoming.name,
                slug=incoming.slug,
            ),
            exception_type=LevelImportError,
        )


class CourseImportService(GenericImportService[ImportCourse, CourseCreate, Course]):
    def __init__(self, repo: CourseRepository):
        super().__init__(
            repo=repo,
            create_factory=lambda incoming: CourseCreate(
                subject_pk=incoming.subject_pk,
                level_pk=incoming.level_pk,
                name=incoming.name,
                slug=incoming.slug,
            ),
            exception_type=CourseImportError,
        )
