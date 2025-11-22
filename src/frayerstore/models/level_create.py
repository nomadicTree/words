from dataclasses import dataclass


@dataclass(frozen=True)
class LevelCreate:
    name: str
    slug: str
    category: str
    number: str
