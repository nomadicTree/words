from frayerstore.importer.identity import (
    resolve_identity,
    ImportDecision,
)

from frayerstore.importer.subjects import ImportSubject


def make_subj(id, name, slug):
    return ImportSubject(id=id, name=name, slug=slug)


def test_double_collision_returns_error():
    incoming = make_subj(None, "Computing", "computing")
    slug_row = make_subj(1, "Computing", "computing")
    name_row = make_subj(2, "Different", "different")

    out = resolve_identity(incoming, slug_row, name_row)
    assert out.decision == ImportDecision.ERROR
    assert "Identity conflict" in out.error


def test_slug_match_name_mismatch_is_error():
    incoming = make_subj(None, "Maths", "maths")
    existing = make_subj(1, "Mathematics", "maths")

    out = resolve_identity(incoming, existing, None)
    assert out.decision == ImportDecision.ERROR


def test_slug_match_identical_is_skip():
    incoming = make_subj(None, "Computing", "computing")
    existing = make_subj(1, "Computing", "computing")

    out = resolve_identity(incoming, existing, None)
    assert out.decision == ImportDecision.SKIP
    assert out.existing == existing


def test_name_match_slug_mismatch_is_error():
    incoming = make_subj(None, "Computing", "comp")
    existing = make_subj(1, "Computing", "computing")

    out = resolve_identity(incoming, None, existing)
    assert out.decision == ImportDecision.ERROR


def test_name_match_identical_is_skip():
    incoming = make_subj(None, "Computing", "computing")
    existing = make_subj(1, "Computing", "computing")

    out = resolve_identity(incoming, None, existing)
    assert out.decision == ImportDecision.SKIP


def test_neither_match_is_create():
    incoming = make_subj(None, "Computing", "computing")

    out = resolve_identity(incoming, None, None)
    assert out.decision == ImportDecision.CREATE
