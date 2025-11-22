from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_level import ImportLevel
from frayerstore.importer.services.import_services import LevelImportService
from frayerstore.importer.coordinators.course_coordinator import (
    CourseImportCoordinator,
)


class LevelImportCoordinator:
    def __init__(
        self,
        level_service: LevelImportService,
        course_coordinator: CourseImportCoordinator,
    ):
        self.level_service = level_service
        self.course_coordinator = course_coordinator

    def import_level(self, data: dict, subject_pk: int, report):
        incoming = ImportLevel.from_yaml(data, subject_pk=subject_pk)
        level = self.level_service.import_item(incoming, report.levels)

        # Import courses
        courses_raw = data.get("courses", [])
        if not isinstance(courses_raw, list):
            raise InvalidYamlStructure("'courses' must be a list")

        for course_raw in courses_raw:
            self.course_coordinator.import_course(
                course_raw, subject_pk, level.pk, report
            )
