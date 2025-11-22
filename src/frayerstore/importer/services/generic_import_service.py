from typing import Callable, Generic, TypeVar

from frayerstore.importer.identity import resolve_identity, handle_resolution
from frayerstore.importer.exceptions import ImporterError
from frayerstore.importer.report import ImportStageReport

TIncoming = TypeVar("TIncoming")  # ImportItem subclass
TCreate = TypeVar("TCreate")  # Create DTO (SubjectCreate, LevelCreate, etc.)
TDomain = TypeVar("TDomain")  # Domain entity (Subject, Level, etc.)
TRepo = TypeVar("TRepo")  # Repository interface


class GenericImportService(Generic[TIncoming, TCreate, TDomain]):
    """
    Shared import logic for simple importer pipelines:

    - Look up by slug and name
    - Identity resolution (skip / error / create)
    - Create via repository
    - Update ImportStageReport
    """

    def __init__(
        self,
        repo: TRepo,
        create_factory: Callable[[TIncoming], TCreate],
        exception_type: type[ImporterError],
    ) -> None:
        self.repo = repo
        self.create_factory = create_factory
        self.exception_type = exception_type

    def import_item(
        self, incoming: TIncoming, stage_report: ImportStageReport
    ) -> TDomain:
        # Look up existing state
        existing_by_slug = self.repo.get_by_slug(incoming.slug)
        existing_by_name = self.repo.get_by_name(incoming.name)

        # Identity resolution
        resolution = resolve_identity(
            incoming=incoming,
            existing_by_slug=existing_by_slug,
            existing_by_name=existing_by_name,
        )

        # Apply SKIP / ERROR logic
        existing = handle_resolution(
            resolution=resolution,
            exception_type=self.exception_type,
            stage_report=stage_report,
        )

        if existing is not None:
            # Idempotent case: item already exists consistently
            return existing

        # CREATE path
        create_dto = self.create_factory(incoming)
        created = self.repo.create(create_dto)
        stage_report.record_created(created)
        return created
