from app.core.models.course_model import Course


class Topic:
    def __init__(self, topic_id: int, code: str, name: str, course: Course):
        self.topic_id = topic_id
        self.code = code
        self.name = name
        self.course = course

    @property
    def url(self):
        subj = self.course.subject.name.replace(" ", "+")
        course = self.course.name.replace(" ", "+")
        return f"/topic_glossary?subject={subj}&course={course}#{self.code}"

    @property
    def label(self):
        return f"{self.code}: {self.name}"
