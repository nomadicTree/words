from app.core.models.course_model import Course


class Topic:
    def __init__(self, topic_id: int, code: str, name: str, course: Course):
        self.topic_id = topic_id
        self.code = code
        self.name = name
        self.course = course

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Topic):
            return NotImplemented
        return self.topic_id == other.topic_id

    def __hash__(self) -> int:
        return hash(self.topic_id)

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Topic):
            return NotImplemented
        return self.code < other.code

    @property
    def url(self):
        subj = self.course.subject.name.replace(" ", "+")
        course = self.course.name.replace(" ", "+")
        return f"/topic_glossary?subject={subj}&course={course}#{self.code}"

    @property
    def label(self):
        return f"{self.code}: {self.name}"

    @property
    def pk(self):
        return self.topic_id
