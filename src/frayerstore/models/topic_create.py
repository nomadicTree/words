from dataclasses import dataclass


@dataclass(frozen=True)
class TopicCreate:
    code: str
    name: str
    slug: str
    course_pk: int
