from dataclasses import dataclass


@dataclass(frozen=True)
class CourseCreate:
    name: str
    slug: str
    subject_pk: int
    level_pk: int
