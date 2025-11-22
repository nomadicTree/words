from __future__ import annotations
from frayerstore.importer.exceptions import SubjectImportError
from frayerstore.importer.report import ImportStageReport
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.db.interfaces.subject_repo import SubjectRepository
from frayerstore.models.subject import Subject
from frayerstore.models.subject_create import SubjectCreate
from frayerstore.importer.identity import resolve_identity, handle_resolution


class SubjectImportService:
    """
    Orchestrates importing a single subject from YAML into the database.

    Responsibilities:
    - Look up existing subjects by slug and name
    - Run identity resolution (create / skip / error)
    - Persist new subjects via the repository
    - Record results in the ImportStageReport
    """

    def __init__(self, repo: SubjectRepository) -> None:
        self.repo = repo

    def import_subject(
        self, incoming: ImportSubject, stage_report: ImportStageReport
    ) -> Subject:
        # Check existing state in the DB
        existing_by_slug = self.repo.get_by_slug(incoming.slug)
        existing_by_name = self.repo.get_by_name(incoming.name)

        # Decide wether to CREATE / SKIP / ERROR
        resolution = resolve_identity(
            incoming=incoming,
            existing_by_slug=existing_by_slug,
            existing_by_name=existing_by_name,
        )

        # Apply SKIP / ERROR behaviour (may raise)
        existing = handle_resolution(
            resolution=resolution,
            exception_type=SubjectImportError,
            stage_report=stage_report,
        )

        if existing is not None:
            # Idempotent: subject already exists and is consistent
            return existing

        # CREATE path
        candidate = SubjectCreate(name=incoming.name, slug=incoming.slug)
        created = self.repo.create(candidate)
        stage_report.record_created(created)

        return created
