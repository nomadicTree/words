"""ABC for all items used during import"""

from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod


@dataclass(frozen=True)
class ImportItem(ABC):
    name: str
    slug: str

    @classmethod
    @abstractmethod
    def from_yaml(cls, data: dict) -> ImportItem:
        pass
