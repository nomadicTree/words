from __future__ import annotations
from frayerstore.importer.exceptions import LevelImportError, SubjectImportError
from frayerstore.importer.dto.import_level import ImportLevel
from frayerstore.db.interfaces.level_repo import LevelRepository
from frayerstore.models.level import Level
from frayerstore.models.level_create import LevelCreate
from frayerstore.importer.services.generic_import_service import GenericImportService
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.db.interfaces.subject_repo import SubjectRepository
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate


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
                category=incoming.category,
                number=incoming.number,
            ),
            exception_type=LevelImportError,
        )
