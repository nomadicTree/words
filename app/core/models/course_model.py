from dataclasses import dataclass
from app.core.models.subject_model import Subject
from app.core.models.level_model import Level


@dataclass(eq=False, order=False)
class Course:
    pk: int
    name: str
    slug: str
    subject: Subject
    level: Level

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        return self.pk == other.pk

    def __hash__(self) -> int:
        return hash(self.pk)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Course):
            return NotImplemented
        if self.level != other.level:
            return self.level < other.level

        return self.name.lower() < other.name.lower()

    @property
    def label(self) -> str:
        return self.name
