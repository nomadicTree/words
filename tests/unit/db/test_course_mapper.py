import pytest

from frayerstore.db.sqlite.course_mapper import CourseMapper
from frayerstore.models.course import Course
from frayerstore.models.course_create import CourseCreate


def make_row(id=1, subject_id=10, level_id=20, name="Algorithms", slug="algorithms"):
    return {
        "id": id,
        "subject_id": subject_id,
        "level_id": level_id,
        "name": name,
        "slug": slug,
    }


@pytest.fixture
def mapper():
    return CourseMapper()


# ---------------------------------------------------------------------------
# row_to_domain
# ---------------------------------------------------------------------------


def test_row_to_domain_returns_course(mapper):
    row = make_row(id=7, subject_id=2, level_id=3, name="Biology", slug="biology")

    course = mapper.row_to_domain(row)

    assert isinstance(course, Course)
    assert course.pk == 7
    assert course.subject_pk == 2
    assert course.level_pk == 3
    assert course.name == "Biology"
    assert course.slug == "biology"


def test_row_to_domain_does_not_mutate_input(mapper):
    row = make_row()
    original = row.copy()

    mapper.row_to_domain(row)

    assert row == original


# ---------------------------------------------------------------------------
# create_to_params
# ---------------------------------------------------------------------------


def test_create_to_params_returns_tuple_in_order(mapper):
    data = CourseCreate(name="Chemistry", slug="chemistry", subject_pk=5, level_pk=9)

    params = mapper.create_to_params(data)

    assert params == (5, 9, "Chemistry", "chemistry")


def test_create_to_params_accepts_raw_strings(mapper):
    data = CourseCreate(name="  Spaced  ", slug="spaced", subject_pk=1, level_pk=2)

    params = mapper.create_to_params(data)

    assert params == (1, 2, "  Spaced  ", "spaced")
