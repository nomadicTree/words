import pytest

from frayerstore.models.course import Course


def test_course_creation_and_label():
    course = Course(pk=1, subject_pk=10, level_pk=20, name="Algorithms", slug="algorithms")

    assert course.pk == 1
    assert course.subject_pk == 10
    assert course.level_pk == 20
    assert course.name == "Algorithms"
    assert course.slug == "algorithms"
    assert course.label == "Algorithms"


def test_course_sorting_prefers_level_then_name_case_insensitive():
    lower_level = Course(pk=1, subject_pk=10, level_pk=1, name="Maths", slug="maths")
    higher_level = Course(pk=2, subject_pk=10, level_pk=2, name="Art", slug="art")
    same_level_alpha = Course(pk=3, subject_pk=10, level_pk=1, name="biology", slug="biology")

    assert lower_level < higher_level  # lower level_pk first
    # Same level: compare case-insensitively by name
    assert (lower_level < same_level_alpha) is False
    assert same_level_alpha < lower_level


def test_course_comparison_with_other_types_returns_not_implemented():
    course = Course(pk=1, subject_pk=1, level_pk=1, name="Art", slug="art")

    assert (course == "not a course") is False
    with pytest.raises(TypeError):
        _ = course < "not a course"
