import pytest

from frayerstore.models.level import Level


def test_level_creation_and_fields():
    level = Level(pk=1, name="KS4", slug="ks4")

    assert level.pk == 1
    assert level.name == "KS4"
    assert level.slug == "ks4"


def test_level_sorting_by_name_then_pk():
    a = Level(pk=2, name="KS4", slug="ks4")
    b = Level(pk=1, name="KS5", slug="ks5")
    c_same_name = Level(pk=3, name="KS4", slug="ks4b")

    # Name comparison (case-insensitive)
    assert a < b  # "ks4" < "ks5"
    # Same name falls back to pk
    assert a < c_same_name
    assert (c_same_name < a) is False


def test_level_comparison_with_other_types_returns_not_implemented():
    level = Level(pk=1, name="KS4", slug="ks4")

    assert (level == "not a level") is False
    with pytest.raises(TypeError):
        _ = level < "not a level"
