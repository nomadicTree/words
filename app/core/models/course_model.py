from app.core.models.subject_model import Subject
from app.core.models.level_model import Level


class Course:
    def __init__(self, course_id: int, name: str, subject: Subject, level: Level):
        self.course_id = course_id
        self.name = name
        self.subject = subject
        self.level = level
