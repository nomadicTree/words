from __future__ import annotations
from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity


@dataclass(frozen=True)
class Level(DomainEntity):
    name: str
    slug: str
