import json

from dataclasses import dataclass, field

from urllib.parse import quote_plus
from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject
from app.core.models.course_model import Course


class UrlMixin:
    @property
    def url(self):
        return f"/view?id={self.word_id}"


@dataclass
class RelatedWord(UrlMixin):
    word_id: str
    word: str


class WordVersion:
    def __init__(
        self,
        wv_id,
        word,
        word_id,
        definition,
        characteristics,
        examples,
        non_examples,
        topics: list[Topic],
        levels: list[Level],
    ):
        self.wv_id = wv_id
        self.word = word
        self.word_id = word_id
        self.definition = definition
        self.characteristics = self._ensure_list(characteristics)
        self.examples = self._ensure_list(examples)
        self.non_examples = self._ensure_list(non_examples)
        self.levels = levels
        self.topics = topics

    def __eq__(self, other: object):
        if not isinstance(other, WordVersion):
            return NotImplemented
        return self.wv_id == other.wv_id

    def __hash__(self) -> int:
        return hash(self.wv_id)

    def __lt__(self, other):
        if not isinstance(other, WordVersion):
            return NotImplemented
        return self.word.lower() < other.word.lower()

    @property
    def level_label(self) -> str:
        """Return a human-readable label for this WordVersion's levels."""
        levels = [l.name for l in self.levels]

        if not levels:
            return "All levels"
        if len(levels) == 1:
            return levels[0]
        if len(levels) == 2:
            return " and ".join(levels)
        return ", ".join(levels[:-1]) + f", and {levels[-1]}"

    @property
    def url(self) -> str:
        level_param = quote_plus(self.level_label)
        return f"/view?id={self.word_id}&level={level_param}"

    @property
    def courses(self) -> set[Course]:
        return {t.course for t in self.topics}

    def _ensure_list(self, value):
        # Case 1: Already a real list (preview mode)
        if isinstance(value, list):
            return value

        # Case 2: None or empty string → treat as empty list
        if not value:
            return []

        # Case 3: A JSON string → decode it
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
            return []
        except Exception:
            return []


class WordVersionChoice:
    def __init__(self, version: WordVersion):
        self.version = version

    @property
    def name(self) -> str:
        return self.version.level_label

    @property
    def pk(self) -> str:
        return self.version.wv_id


class Word(UrlMixin):
    def __init__(
        self,
        word_id,
        word,
        subject: Subject,
        versions: list[WordVersion],
        related_words: list[RelatedWord],
    ):
        self.word_id = word_id
        self.word = word
        self.subject = subject
        self.versions = versions
        self.related_words = related_words

    def __eq__(self, other: object):
        if not isinstance(other, Word):
            return NotImplemented
        return self.word_id == other.word_id

    def __hash__(self) -> int:
        return hash(self.word_id)

    @property
    def courses(self) -> set[Course]:
        return {c for v in self.versions for c in v.courses}
