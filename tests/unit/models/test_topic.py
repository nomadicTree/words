import pytest

from frayerstore.models.topic import Topic


def test_topic_creation_and_label():
    topic = Topic(pk=1, course_pk=9, code="CS1", name="Introduction", slug="introduction")

    assert topic.pk == 1
    assert topic.course_pk == 9
    assert topic.code == "CS1"
    assert topic.name == "Introduction"
    assert topic.slug == "introduction"
    assert topic.label == "CS1: Introduction"


def test_topic_sorting_by_code():
    a = Topic(pk=1, course_pk=1, code="A1", name="Alpha", slug="alpha")
    b = Topic(pk=2, course_pk=1, code="B1", name="Beta", slug="beta")

    assert a < b
    assert not (b < a)


def test_topic_comparison_with_other_types_returns_not_implemented():
    topic = Topic(pk=1, course_pk=1, code="A1", name="Alpha", slug="alpha")

    assert (topic == 123) is False
    with pytest.raises(TypeError):
        _ = topic < 123
