import pytest

from frayerstore.db.sqlite.topic_mapper import TopicMapper
from frayerstore.models.topic import Topic
from frayerstore.models.topic_create import TopicCreate


def make_row(id=1, course_id=11, code="A1", name="Arrays", slug="arrays"):
    return {
        "id": id,
        "course_id": course_id,
        "code": code,
        "name": name,
        "slug": slug,
    }


@pytest.fixture
def mapper():
    return TopicMapper()


# ---------------------------------------------------------------------------
# row_to_domain
# ---------------------------------------------------------------------------


def test_row_to_domain_returns_topic(mapper):
    row = make_row(id=9, course_id=3, code="BIO1", name="Cells", slug="cells")

    topic = mapper.row_to_domain(row)

    assert isinstance(topic, Topic)
    assert topic.pk == 9
    assert topic.course_pk == 3
    assert topic.code == "BIO1"
    assert topic.name == "Cells"
    assert topic.slug == "cells"


def test_row_to_domain_does_not_mutate_input(mapper):
    row = make_row()
    original = row.copy()

    mapper.row_to_domain(row)

    assert row == original


# ---------------------------------------------------------------------------
# create_to_params
# ---------------------------------------------------------------------------


def test_create_to_params_returns_tuple_in_order(mapper):
    data = TopicCreate(course_pk=7, code="M1", name="Matrices", slug="matrices")

    params = mapper.create_to_params(data)

    assert params == (7, "M1", "Matrices", "matrices")


def test_create_to_params_accepts_whitespace(mapper):
    data = TopicCreate(course_pk=2, code="  C1  ", name="  Circles  ", slug="circles")

    params = mapper.create_to_params(data)

    assert params == (2, "  C1  ", "  Circles  ", "circles")
