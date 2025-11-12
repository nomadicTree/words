import json

from dataclasses import dataclass, field

from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject


class UrlMixin:
    @property
    def url(self):
        return f"/view?id={self.word_id}"


@dataclass
class RelatedWord(UrlMixin):
    word_id: str
    word: str


@dataclass
class SearchResult(UrlMixin):
    word_id: int
    word: str
    subject: Subject
    versions: list = field(default_factory=list)


class WordVersion(UrlMixin):
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
        self.characteristics = json.loads(characteristics) or "[]"
        self.examples = json.loads(examples) or "[]"
        self.non_examples = json.loads(non_examples) or "[]"
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
