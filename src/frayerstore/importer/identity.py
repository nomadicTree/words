from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from enum import StrEnum, auto
import sqlite3
from .exceptions import ImporterError
from .models import ImportItem
from .report import ImportStageReport


class ImportDecision(StrEnum):
    SKIP = auto()
    CREATE = auto()
    ERROR = auto()


@dataclass
class IdentityResolutionResult:
    decision: ImportDecision
    existing: Optional[ImportItem] = None
    error: Optional[str] = None


def resolve_identity(
    incoming: ImportItem,
    existing_by_slug: ImportItem | None,
    existing_by_name: ImportItem | None,
    stage_report: ImportStageReport,
) -> IdentityResolutionResult:
    # DOUBLE-COLLLISION (slug row != name row)
    if (
        existing_by_slug
        and existing_by_name
        and existing_by_name.id != existing_by_slug.id
    ):
        message = (
            f"Identity conflict: slug '{incoming.slug}' refers to "
            f"'{existing_by_slug.name}' (id={existing_by_slug.id}) but name '{incoming.name}' "
            f"refers to '{existing_by_name.name}' (id={existing_by_name.id})."
        )
        stage_report.record_error(message)
        return IdentityResolutionResult(decision=ImportDecision.ERROR, error=message)

    # SLUG MATCH: skip or fatal mismatch
    if existing_by_slug:
        if existing_by_slug.name != incoming.name:
            message = (
                f"Identity conflict: slug '{existing_by_slug.slug}' found but names "
                f"do not match: incoming '{incoming.name}' vs "
                f"existing '{existing_by_slug.name}'."
            )
            stage_report.record_error(message)
            return IdentityResolutionResult(
                decision=ImportDecision.ERROR, error=message
            )

        # Idempotent skip
        stage_report.record_skipped(existing_by_slug)
        return IdentityResolutionResult(
            decision=ImportDecision.SKIP, existing=existing_by_slug
        )

    # NAME MATCH WITHOUT SLUG MATCH: fatal mismatch
    if existing_by_name:
        if existing_by_name.slug != incoming.slug:
            message = (
                f"Identity conflict: name '{existing_by_name.name}' found but slugs "
                f"do not match: incoming '{incoming.slug}' vs "
                f"existing '{existing_by_name.slug}'."
            )
            stage_report.record_error(message)
            return IdentityResolutionResult(
                decision=ImportDecision.ERROR, error=message
            )

    # NEITHER EXISTS: PROCEED TO CREATE
    return IdentityResolutionResult(decision=ImportDecision.CREATE)


def handle_resolution(resolution, exception_type) -> ImportItem | None:
    if resolution.decision is ImportDecision.ERROR:
        raise exception_type(resolution.error)

    if resolution.decision is ImportDecision.SKIP:
        return resolution.existing

    return None


def import_with_identity(
    conn: sqlite3.Connection,
    incoming: ImportItem,
    *,
    existing_by_slug: ImportItem | None,
    existing_by_name: ImportItem | None,
    stage_report: ImportStageReport,
    error_type: ImporterError,
):
    resolution = resolve_identity(
        incoming, existing_by_slug, existing_by_name, stage_report
    )

    existing = handle_resolution(resolution, error_type)

    if existing:
        return existing

    # Need to write new row
    new_obj = incoming.__class__.create_in_db(conn, incoming)
    stage_report.record_created(new_obj)
    return new_obj
