import pytest

from frayerstore.importer.coordinators.topic_coordinator import TopicImportCoordinator
from frayerstore.importer.dto.import_topic import ImportTopic


class FakeService:
    def __init__(self, returning=None):
        self.calls = []
        self.returning = returning or object()

    def import_topic(self, incoming, stage_report):
        self.calls.append((incoming, stage_report))
        return self.returning


@pytest.fixture
def coordinator(repo=None):
    service = FakeService()
    return TopicImportCoordinator(service)


def test_import_topic_passes_parsed_dto_and_stage(report, monkeypatch):
    returned = object()
    service = FakeService(returning=returned)
    coordinator = TopicImportCoordinator(service)

    parsed = ImportTopic(course_pk=9, code="CS1", name="Intro", slug="intro")
    called_with = {}

    def fake_from_yaml(data, *, course_pk):
        called_with["course_pk"] = course_pk
        return parsed

    monkeypatch.setattr(ImportTopic, "from_yaml", fake_from_yaml)

    topic = coordinator.import_topic({"code": "CS1", "name": "Intro"}, course_pk=9, report=report)

    assert topic is returned
    assert called_with["course_pk"] == 9
    assert service.calls == [(parsed, report.topics)]
