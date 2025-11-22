import pytest

from frayerstore.db.sqlite.topic_repo_sqlite import SQLiteTopicRepository
from frayerstore.db.sqlite.topic_mapper import TopicMapper
from frayerstore.models.topic import Topic
from frayerstore.models.topic_create import TopicCreate


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def mapper():
    return TopicMapper()


@pytest.fixture
def repo(schema_db, mapper):
    return SQLiteTopicRepository(schema_db, mapper)


# Helpers

def insert_subject(conn, name="Computing", slug="computing"):
    return conn.execute(
        "INSERT INTO Subjects (name, slug) VALUES (?, ?) RETURNING id, name, slug",
        (name, slug),
    ).fetchone()


def insert_level(conn, name="KS4", slug="ks4"):
    return conn.execute(
        "INSERT INTO Levels (name, slug) VALUES (?, ?) RETURNING id, name, slug",
        (name, slug),
    ).fetchone()


def insert_course(conn, *, subject_id, level_id, name="Algorithms", slug="algorithms"):
    return conn.execute(
        """
        INSERT INTO Courses (subject_id, level_id, name, slug)
        VALUES (?, ?, ?, ?)
        RETURNING id, subject_id, level_id, name, slug
        """,
        (subject_id, level_id, name, slug),
    ).fetchone()


def insert_topic(conn, *, course_id, code="A1", name="Arrays", slug="arrays"):
    return conn.execute(
        """
        INSERT INTO Topics (course_id, code, name, slug)
        VALUES (?, ?, ?, ?)
        RETURNING id, course_id, code, name, slug
        """,
        (course_id, code, name, slug),
    ).fetchone()


def setup_course_with_topic(conn):
    subject = insert_subject(conn)
    level = insert_level(conn)
    course = insert_course(conn, subject_id=subject["id"], level_id=level["id"])
    topic = insert_topic(conn, course_id=course["id"], code="A1", name="Arrays", slug="arrays")
    return course, topic


# ---------------------------------------------------------------------------
# CREATE TESTS
# ---------------------------------------------------------------------------


def test_create_inserts_row_and_returns_domain(schema_db, repo):
    subject = insert_subject(schema_db)
    level = insert_level(schema_db)
    course = insert_course(schema_db, subject_id=subject["id"], level_id=level["id"])
    data = TopicCreate(course_pk=course["id"], code="A1", name="Arrays", slug="arrays")

    created = repo.create(data)

    row = schema_db.execute("SELECT * FROM Topics WHERE slug='arrays'").fetchone()
    assert row is not None
    assert row["course_id"] == course["id"]
    assert row["code"] == "A1"

    assert isinstance(created, Topic)
    assert created.pk == row["id"]
    assert created.course_pk == course["id"]
    assert created.code == "A1"


def test_create_uses_mapper_to_build_params(schema_db, mapper, monkeypatch):
    repo = SQLiteTopicRepository(schema_db, mapper)
    subject = insert_subject(schema_db)
    level = insert_level(schema_db)
    course = insert_course(schema_db, subject_id=subject["id"], level_id=level["id"])

    called = {}

    def fake_params(data):
        called["used"] = True
        return (course["id"], "X", "x name", "x")

    monkeypatch.setattr(mapper, "create_to_params", fake_params)

    repo.create(TopicCreate(course_pk=course["id"], code="X", name="x name", slug="x"))

    assert called.get("used") is True


# ---------------------------------------------------------------------------
# LOOKUP TESTS
# ---------------------------------------------------------------------------


def test_get_by_slug_returns_topic(repo, schema_db):
    _, topic_row = setup_course_with_topic(schema_db)

    topic = repo.get_by_slug(topic_row["slug"])

    assert isinstance(topic, Topic)
    assert topic.pk == topic_row["id"]
    assert topic.course_pk == topic_row["course_id"]
    assert topic.code == topic_row["code"]


def test_get_by_slug_returns_none_when_missing(repo):
    assert repo.get_by_slug("missing") is None


def test_get_by_name_returns_topic(repo, schema_db):
    _, topic_row = setup_course_with_topic(schema_db)

    topic = repo.get_by_name(topic_row["name"])

    assert isinstance(topic, Topic)
    assert topic.slug == topic_row["slug"]


def test_get_by_name_returns_none_when_missing(repo):
    assert repo.get_by_name("Imaginary Topic") is None


def test_get_by_course_and_code_returns_topic(repo, schema_db):
    course_row, topic_row = setup_course_with_topic(schema_db)

    topic = repo.get_by_course_and_code(course_row["id"], topic_row["code"])

    assert isinstance(topic, Topic)
    assert topic.pk == topic_row["id"]


def test_get_by_course_and_code_returns_none_when_missing(repo, schema_db):
    course_row, _ = setup_course_with_topic(schema_db)

    assert repo.get_by_course_and_code(course_row["id"], "NONE") is None


def test_get_by_id_returns_topic(repo, schema_db):
    _, topic_row = setup_course_with_topic(schema_db)

    topic = repo.get_by_id(topic_row["id"])

    assert isinstance(topic, Topic)
    assert topic.pk == topic_row["id"]
    assert topic.code == topic_row["code"]


def test_get_by_id_returns_none_when_missing(repo):
    assert repo.get_by_id(9999) is None
