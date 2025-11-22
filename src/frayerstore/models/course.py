from dataclasses import dataclass
from frayerstore.models.domain_entity import DomainEntity


@dataclass(frozen=True, order=False)
class Course(DomainEntity):
    subject_pk: int
    level_pk: int
    name: str
    slug: str

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        if self.level_pk != other.level_pk:
            return self.level_pk < other.level_pk

        return self.name.lower() < other.name.lower()

    @property
    def label(self) -> str:
        return self.name
