import pytest
from frayerstore.importer.exceptions import InvalidYamlStructure
from frayerstore.importer.dto.import_level import ImportLevel
from frayerstore.importer.coordinators.level_coordinator import LevelImportCoordinator


# ----------------------------------------------------------------------
# FAKES
# ----------------------------------------------------------------------


class FakeLevel:
    def __init__(self, pk):
        self.pk = pk


class FakeLevelService:
    """Fake GenericImportService for levels."""

    def __init__(self, returning_pk=222):
        self.calls = []
        self.returning_pk = returning_pk

    def import_item(self, incoming, stage_report):
        self.calls.append((incoming, stage_report))
        return FakeLevel(self.returning_pk)


class FakeCourseCoordinator:
    """Captures calls to import_course."""

    def __init__(self):
        self.calls = []

    def import_course(self, data, subject_pk, level_pk, report):
        self.calls.append((data, subject_pk, level_pk, report))


# ----------------------------------------------------------------------
# FIXTURE: ImportReport
# ----------------------------------------------------------------------


@pytest.fixture
def report():
    from frayerstore.importer.report import ImportReport

    return ImportReport()


# ----------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------


def test_level_import_coordinator_calls_service_and_imports_courses(
    report, monkeypatch
):
    """
    - LevelImportCoordinator should call ImportLevel.from_yaml()
    - call level_service.import_item()
    - call course_coordinator.import_course() with returned PK
    """

    # Force predictable DTO return from from_yaml
    parsed_dto = ImportLevel(subject_pk=10, name="KS4", slug="ks4")

    def fake_from_yaml(data, subject_pk):
        return parsed_dto

    monkeypatch.setattr(ImportLevel, "from_yaml", fake_from_yaml)

    level_service = FakeLevelService(returning_pk=999)
    course_coordinator = FakeCourseCoordinator()

    co = LevelImportCoordinator(level_service, course_coordinator)

    yaml = {
        "name": "KS4",
        "courses": [
            {"name": "GCSE CS"},
            {"name": "GCSE IT"},
        ],
    }

    co.import_level(yaml, subject_pk=10, report=report)

    # --- Assert: service.import_item called once ---
    assert len(level_service.calls) == 1
    incoming_passed, stage_passed = level_service.calls[0]

    # It should pass our fake DTO
    assert incoming_passed is parsed_dto

    # It should pass the correct stage of the report
    assert stage_passed is report.levels

    # --- Assert: two course imports triggered ---
    assert len(course_coordinator.calls) == 2

    # Each should have received the PK returned by FakeLevelService and subject PK
    for call in course_coordinator.calls:
        (_, subject_pk_passed, level_pk, _) = call
        assert level_pk == 999
        assert subject_pk_passed == 10

    # Correct YAML passed to children
    assert course_coordinator.calls[0][0] == {"name": "GCSE CS"}
    assert course_coordinator.calls[1][0] == {"name": "GCSE IT"}


def test_level_import_coordinator_rejects_non_list_courses(report, monkeypatch):
    """'courses' must be a list, otherwise raise InvalidYamlStructure."""

    monkeypatch.setattr(
        ImportLevel,
        "from_yaml",
        lambda data, subject_pk: ImportLevel(
            subject_pk=subject_pk, name="KS4", slug="ks4"
        ),
    )

    level_service = FakeLevelService()
    course_coordinator = FakeCourseCoordinator()
    co = LevelImportCoordinator(level_service, course_coordinator)

    yaml = {
        "name": "KS4",
        "courses": "not-a-list",
    }

    with pytest.raises(InvalidYamlStructure):
        co.import_level(yaml, subject_pk=10, report=report)


def test_level_import_coordinator_allows_no_courses_section(report, monkeypatch):
    """
    If 'courses' is missing, treat it as an empty list and do not import any courses.
    """

    monkeypatch.setattr(
        ImportLevel,
        "from_yaml",
        lambda data, subject_pk: ImportLevel(
            subject_pk=subject_pk, name="KS4", slug="ks4"
        ),
    )

    level_service = FakeLevelService()
    course_coordinator = FakeCourseCoordinator()

    co = LevelImportCoordinator(level_service, course_coordinator)

    yaml = {"name": "KS4"}  # no 'courses'

    co.import_level(yaml, subject_pk=10, report=report)

    # Service should still be called once
    assert len(level_service.calls) == 1

    # No course imports expected
    assert course_coordinator.calls == []
