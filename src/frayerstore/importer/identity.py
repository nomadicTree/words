from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from enum import StrEnum, auto
from frayerstore.importer.exceptions import ImporterError
from frayerstore.importer.dto.import_item import ImportItem
from frayerstore.importer.report import ImportStageReport
from frayerstore.models.domain_entity import DomainEntity


class ImportDecision(StrEnum):
    SKIP = auto()
    CREATE = auto()
    ERROR = auto()


@dataclass
class IdentityResolutionResult:
    decision: ImportDecision
    existing: Optional[DomainEntity] = None
    error: Optional[str] = None


def resolve_identity(
    incoming: ImportItem,
    existing_by_slug: DomainEntity | None,
    existing_by_name: DomainEntity | None,
) -> IdentityResolutionResult:
    # DOUBLE-COLLLISION (slug row != name row)
    if existing_by_slug and existing_by_name and existing_by_name != existing_by_slug:
        message = (
            f"Identity conflict: slug '{incoming.slug}' refers to "
            f"'{existing_by_slug.name}' (pk={existing_by_slug.pk}) but name '{incoming.name}' "
            f"refers to '{existing_by_name.name}' (pk={existing_by_name.pk})."
        )
        return IdentityResolutionResult(decision=ImportDecision.ERROR, error=message)

    # SLUG MATCH: skip or fatal mismatch
    if existing_by_slug:
        if existing_by_slug.name != incoming.name:
            message = (
                f"Identity conflict: slug '{existing_by_slug.slug}' found but names "
                f"do not match: incoming '{incoming.name}' vs "
                f"existing '{existing_by_slug.name}'."
            )
            return IdentityResolutionResult(
                decision=ImportDecision.ERROR, error=message
            )

        # Idempotent skip
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
            return IdentityResolutionResult(
                decision=ImportDecision.ERROR, error=message
            )
        # Idempotent skip
        return IdentityResolutionResult(
            decision=ImportDecision.SKIP, existing=existing_by_name
        )

    # NEITHER EXISTS: PROCEED TO CREATE
    return IdentityResolutionResult(decision=ImportDecision.CREATE)


def handle_resolution(
    resolution: IdentityResolutionResult,
    exception_type: type[ImporterError],
    stage_report: ImportStageReport,
) -> DomainEntity | None:
    if resolution.decision == ImportDecision.ERROR:
        stage_report.record_error(resolution.error)
        raise exception_type(resolution.error)

    if resolution.decision == ImportDecision.SKIP:
        stage_report.record_skipped(resolution.existing)
        return resolution.existing

    return None
