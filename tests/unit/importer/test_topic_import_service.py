import pytest

from frayerstore.importer.services.topic_import_service import TopicImportService
from frayerstore.importer.dto.import_topic import ImportTopic
from frayerstore.importer.exceptions import TopicImportError
from frayerstore.models.topic_create import TopicCreate


class FakeTopic:
    def __init__(self, *, pk=1, course_pk=1, code="A1", name="Arrays", slug="arrays"):
        self.pk = pk
        self.course_pk = course_pk
        self.code = code
        self.name = name
        self.slug = slug


class FakeRepo:
    def __init__(self):
        self.created = []
        self.existing = None

    def get_by_course_and_code(self, course_pk, code):
        return self.existing

    def create(self, data: TopicCreate):
        created = FakeTopic(
            course_pk=data.course_pk, code=data.code, name=data.name, slug=data.slug
        )
        self.created.append(data)
        return created


@pytest.fixture
def incoming():
    return ImportTopic(course_pk=3, code="CS1", name="Intro", slug="intro")


@pytest.fixture
def repo():
    return FakeRepo()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_creates_new_topic_when_not_existing(repo, stage_report, incoming):
    service = TopicImportService(repo)

    topic = service.import_topic(incoming, stage_report)

    assert isinstance(topic, FakeTopic)
    assert topic.slug == "intro"
    assert stage_report.created == [topic]
    assert repo.created[0].course_pk == 3
    assert repo.created[0].code == "CS1"
    assert repo.created[0].name == "Intro"


def test_skips_existing_topic_with_same_name(repo, stage_report, incoming):
    repo.existing = FakeTopic(course_pk=incoming.course_pk, code=incoming.code, name=incoming.name)
    service = TopicImportService(repo)

    topic = service.import_topic(incoming, stage_report)

    assert topic is repo.existing
    assert stage_report.skipped == [repo.existing]
    assert stage_report.errors == []


def test_raises_when_existing_topic_has_different_name(repo, stage_report, incoming):
    repo.existing = FakeTopic(course_pk=incoming.course_pk, code=incoming.code, name="Different")
    service = TopicImportService(repo)

    with pytest.raises(TopicImportError):
        service.import_topic(incoming, stage_report)

    assert stage_report.errors  # error recorded
    assert stage_report.created == []
    assert stage_report.skipped == []
