from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity
from frayerstore.models.subject import Subject
from frayerstore.models.level import Level


@dataclass(frozen=True, order=False)
class Course(DomainEntity):
    name: str
    slug: str
    subject: Subject
    level: Level

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        if self.level != other.level:
            return self.level < other.level

        return self.name.lower() < other.name.lower()

    @property
    def label(self) -> str:
        return self.name
