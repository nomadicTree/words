import pytest

from frayerstore.importer.identity import (
    handle_resolution,
    IdentityResolutionResult,
    ImportDecision,
)

from frayerstore.importer.subjects import ImportSubject
from frayerstore.importer.exceptions import SubjectImportCollision


def make_subj(id, name, slug):
    return ImportSubject(id=id, name=name, slug=slug)


def test_handle_resolution_error_raises_and_records(stage_report):
    res = IdentityResolutionResult(
        decision=ImportDecision.ERROR,
        error="Something bad happened",
    )

    with pytest.raises(SubjectImportCollision):
        handle_resolution(res, SubjectImportCollision, stage_report)

    assert stage_report.errors == ["Something bad happened"]


def test_handle_resolution_skip_records(stage_report):
    existing = make_subj(1, "Computing", "computing")

    res = IdentityResolutionResult(
        decision=ImportDecision.SKIP,
        existing=existing,
    )

    out = handle_resolution(res, SubjectImportCollision, stage_report)

    assert out == existing
    assert stage_report.skipped == [existing]


def test_handle_resolution_create_returns_none(stage_report):
    res = IdentityResolutionResult(decision=ImportDecision.CREATE)

    out = handle_resolution(res, SubjectImportCollision, stage_report)

    assert out is None
    assert stage_report.skipped == []
    assert stage_report.errors == []
