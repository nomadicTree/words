from pathlib import Path
from frayerstore.importer.yaml_utils import load_yaml
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.services.generic_list_import_service import (
    GenericListImportService,
)

from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.services.import_services import (
    SubjectImportService,
    LevelImportService,
)

from frayerstore.importer.dto.import_level import ImportLevel


def import_items_from_file(
    *,
    path: Path,
    yaml_key: str,
    import_item_cls,
    import_service,
    stage_selector,
    report,
):
    """
    Generic YAML list importer:
    - loads YAML
    - extracts a list under a specific key
    - validates it is a list
    - uses GenericListImportService to import items
    """

    data = load_yaml(path)
    items = data.get(yaml_key)

    if not isinstance(items, list):
        raise InvalidYamlStructure(f"Expected '{yaml_key}' to be a list")

    list_importer = GenericListImportService(
        import_item_cls=import_item_cls,
        import_service=import_service,
        stage_selector=stage_selector,
    )

    list_importer.import_many(items, report)


def import_subjects_from_file(path, import_service: SubjectImportService, report):
    import_items_from_file(
        path=path,
        yaml_key="subjects",
        import_item_cls=ImportSubject,
        import_service=import_service,
        stage_selector=lambda r: r.subjects,
        report=report,
    )


def import_levels_from_file(path, import_service: LevelImportService, report):
    import_items_from_file(
        path=path,
        yaml_key="levels",
        import_item_cls=ImportLevel,
        import_service=import_service,
        stage_selector=lambda r: r.levels,
        report=report,
    )
