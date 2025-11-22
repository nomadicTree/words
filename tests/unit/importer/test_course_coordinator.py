import pytest

from frayerstore.importer.coordinators.course_coordinator import CourseImportCoordinator
from frayerstore.importer.dto.import_course import ImportCourse
from frayerstore.importer.exceptions import InvalidYamlStructure


class FakeCourse:
    def __init__(self, pk):
        self.pk = pk


class FakeCourseService:
    def __init__(self, returning_pk=10):
        self.calls = []
        self.returning_pk = returning_pk

    def import_item(self, incoming, stage_report):
        self.calls.append((incoming, stage_report))
        return FakeCourse(self.returning_pk)


class FakeTopicCoordinator:
    def __init__(self):
        self.calls = []

    def import_topic(self, data, course_pk, report):
        self.calls.append((data, course_pk, report))


@pytest.fixture
def report():
    from frayerstore.importer.report import ImportReport

    return ImportReport()


def test_import_course_handles_topics_and_passes_correct_pks(report, monkeypatch):
    parsed_course = ImportCourse(subject_pk=1, level_pk=2, name="Algorithms", slug="algorithms")

    def fake_from_yaml(data, *, subject_pk, level_pk):
        assert subject_pk == 99
        assert level_pk == 100
        return parsed_course

    monkeypatch.setattr(ImportCourse, "from_yaml", fake_from_yaml)

    course_service = FakeCourseService(returning_pk=55)
    topic_coordinator = FakeTopicCoordinator()
    coordinator = CourseImportCoordinator(course_service, topic_coordinator)

    yaml = {"name": "Algorithms", "topics": [{"code": "A1"}, {"code": "A2"}]}

    course = coordinator.import_course(yaml, subject_pk=99, level_pk=100, report=report)

    assert isinstance(course, FakeCourse)
    assert course.pk == 55

    # Course service should receive parsed DTO and correct stage
    assert course_service.calls == [(parsed_course, report.courses)]

    # Topic coordinator should be called for each topic with created course PK
    assert topic_coordinator.calls == [
        (yaml["topics"][0], 55, report),
        (yaml["topics"][1], 55, report),
    ]


def test_import_course_rejects_non_list_topics(report):
    course_service = FakeCourseService()
    topic_coordinator = FakeTopicCoordinator()
    coordinator = CourseImportCoordinator(course_service, topic_coordinator)

    with pytest.raises(InvalidYamlStructure):
        coordinator.import_course({"name": "Algorithms", "topics": "NOPE"}, subject_pk=1, level_pk=1, report=report)
