from pathlib import Path
from frayerstore.importer.services.subject_list_import_service import (
    SubjectListImportService,
)

from frayerstore.importer.yaml_utils import load_yaml
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.report import ImportReport


def import_subjects_from_file(
    path: Path, list_import_service: SubjectListImportService, report: ImportReport
):
    data = load_yaml(path)
    subjects = data.get("subjects")

    if not isinstance(subjects, list):
        raise InvalidYamlStructure("Expected 'subjects' to be a list")

    list_import_service.import_many(subjects, report)
