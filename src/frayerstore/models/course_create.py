from dataclasses import dataclass
from frayerstore.models.subject import Subject
from frayerstore.models.level import Level


@dataclass(frozen=True)
class Course:
    name: str
    slug: str
    subject: Subject
    level: Level
