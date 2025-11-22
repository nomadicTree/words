import pytest
from frayerstore.importer.coordinators.subject_coordinator import (
    SubjectImportCoordinator,
)
from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.exceptions import InvalidYamlStructure


# ----------------------------------------------------------------------
# FAKES
# ----------------------------------------------------------------------


class FakeSubject:
    """Dummy domain object returned by the service."""

    def __init__(self, pk):
        self.pk = pk


class FakeSubjectService:
    """
    Fakes the GenericImportService for subjects.

    Tracks calls to import_item and returns a FakeSubject with a fixed PK.
    """

    def __init__(self, returning_pk=123):
        self.calls = []
        self.returning_pk = returning_pk

    def import_item(self, incoming, stage_report):
        self.calls.append((incoming, stage_report))
        return FakeSubject(self.returning_pk)


class FakeLevelCoordinator:
    """Tracks calls to import_level."""

    def __init__(self):
        self.calls = []

    def import_level(self, data, subject_pk, report):
        self.calls.append((data, subject_pk, report))


# ----------------------------------------------------------------------
# FIXTURE: A real ImportReport (so stage selectors work correctly)
# ----------------------------------------------------------------------


@pytest.fixture
def report():
    from frayerstore.importer.report import ImportReport

    return ImportReport()


# ----------------------------------------------------------------------
# TESTS
# ----------------------------------------------------------------------


def test_import_subject_calls_service_and_import_levels(report, monkeypatch):
    """
    - SubjectImportCoordinator should:
      - parse DTO using ImportSubject.from_yaml()
      - call subject_service.import_item()
      - call level_coordinator.import_level() for each level
      - pass correct PK from service to children
    """

    # --- replace ImportSubject.from_yaml so we see exactly what is passed ---
    parsed_dto = ImportSubject(name="Computing", slug="computing")

    def fake_from_yaml(data):
        return parsed_dto

    monkeypatch.setattr(ImportSubject, "from_yaml", fake_from_yaml)

    # --- set up fakes ---
    subject_service = FakeSubjectService(returning_pk=42)
    level_coordinator = FakeLevelCoordinator()

    coordinator = SubjectImportCoordinator(subject_service, level_coordinator)

    yaml = {
        "name": "Computing",
        "levels": [
            {"name": "KS4"},
            {"name": "KS5"},
        ],
    }

    coordinator.import_subject(yaml, report)

    # ---- ASSERT: subject service called exactly once ----
    assert len(subject_service.calls) == 1

    incoming_passed, stage_report_passed = subject_service.calls[0]

    # Should be the DTO returned by our monkeypatched from_yaml
    assert incoming_passed is parsed_dto

    # Should pass the correct stage in the report
    assert stage_report_passed is report.subjects

    # ---- ASSERT: levels imported correctly ----
    assert len(level_coordinator.calls) == 2

    # Should receive the PK returned by FakeSubjectService
    assert level_coordinator.calls[0][1] == 42
    assert level_coordinator.calls[1][1] == 42

    # Should receive the YAML level dicts
    assert level_coordinator.calls[0][0] == {"name": "KS4"}
    assert level_coordinator.calls[1][0] == {"name": "KS5"}


def test_import_subject_rejects_invalid_levels_type(report, monkeypatch):
    """Coordinator must raise InvalidYamlStructure if 'levels' is not a list."""

    monkeypatch.setattr(
        ImportSubject,
        "from_yaml",
        lambda data: ImportSubject(name="Computing", slug="computing"),
    )

    subject_service = FakeSubjectService()
    level_coordinator = FakeLevelCoordinator()

    coordinator = SubjectImportCoordinator(subject_service, level_coordinator)

    bad_yaml = {
        "name": "Computing",
        "levels": "NOT A LIST",
    }

    with pytest.raises(InvalidYamlStructure):
        coordinator.import_subject(bad_yaml, report)


def test_import_subject_without_levels_is_valid(report, monkeypatch):
    """
    If no 'levels' key exists, coordinator should treat it as empty list.
    """

    monkeypatch.setattr(
        ImportSubject,
        "from_yaml",
        lambda data: ImportSubject(name="Computing", slug="computing"),
    )

    subject_service = FakeSubjectService()
    level_coordinator = FakeLevelCoordinator()

    coordinator = SubjectImportCoordinator(subject_service, level_coordinator)

    yaml = {"name": "Computing"}  # no "levels" key

    coordinator.import_subject(yaml, report)

    # No level imports expected
    assert level_coordinator.calls == []

    # But subject import should still happen
    assert len(subject_service.calls) == 1
