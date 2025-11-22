import pytest

from frayerstore.db.sqlite.course_repo_sqlite import SQLiteCourseRepository
from frayerstore.db.sqlite.course_mapper import CourseMapper
from frayerstore.models.course import Course
from frayerstore.models.course_create import CourseCreate


# ---------------------------------------------------------------------------
# FIXTURES
# ---------------------------------------------------------------------------


@pytest.fixture
def mapper():
    return CourseMapper()


@pytest.fixture
def repo(schema_db, mapper):
    return SQLiteCourseRepository(schema_db, mapper)


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


# ---------------------------------------------------------------------------
# CREATE TESTS
# ---------------------------------------------------------------------------


def test_create_inserts_row_and_returns_domain(schema_db, repo):
    subject = insert_subject(schema_db)
    level = insert_level(schema_db)
    data = CourseCreate(
        subject_pk=subject["id"],
        level_pk=level["id"],
        name="Algorithms",
        slug="algorithms",
    )

    created = repo.create(data)

    row = schema_db.execute("SELECT * FROM Courses WHERE slug='algorithms'").fetchone()
    assert row is not None
    assert row["name"] == "Algorithms"
    assert row["subject_id"] == subject["id"]
    assert row["level_id"] == level["id"]

    assert isinstance(created, Course)
    assert created.pk == row["id"]
    assert created.subject_pk == subject["id"]
    assert created.level_pk == level["id"]


def test_create_uses_mapper_to_build_params(schema_db, mapper, monkeypatch):
    repo = SQLiteCourseRepository(schema_db, mapper)
    insert_subject(schema_db)
    insert_level(schema_db)

    called = {}

    def fake_params(data):
        called["used"] = True
        return (1, 1, "X", "x")

    monkeypatch.setattr(mapper, "create_to_params", fake_params)

    repo.create(CourseCreate(name="X", slug="x", subject_pk=1, level_pk=1))

    assert called.get("used") is True


# ---------------------------------------------------------------------------
# LOOKUP TESTS
# ---------------------------------------------------------------------------


def setup_course(conn):
    subject = insert_subject(conn)
    level = insert_level(conn)
    return insert_course(conn, subject_id=subject["id"], level_id=level["id"])


def test_get_by_slug_returns_course(repo, schema_db):
    row = setup_course(schema_db)

    course = repo.get_by_slug(row["slug"])

    assert isinstance(course, Course)
    assert course.pk == row["id"]
    assert course.name == row["name"]
    assert course.subject_pk == row["subject_id"]
    assert course.level_pk == row["level_id"]


def test_get_by_slug_returns_none_when_missing(repo):
    assert repo.get_by_slug("missing") is None


def test_get_by_name_returns_course(repo, schema_db):
    row = setup_course(schema_db)

    course = repo.get_by_name(row["name"])

    assert isinstance(course, Course)
    assert course.slug == row["slug"]


def test_get_by_name_returns_none_when_missing(repo):
    assert repo.get_by_name("Imaginary Course") is None


def test_get_by_id_returns_course(repo, schema_db):
    row = setup_course(schema_db)

    course = repo.get_by_id(row["id"])

    assert isinstance(course, Course)
    assert course.pk == row["id"]
    assert course.name == row["name"]


def test_get_by_id_returns_none_when_missing(repo):
    assert repo.get_by_id(9999) is None
