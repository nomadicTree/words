import json

from dataclasses import dataclass

from app.core.models.topic_model import Topic
from app.core.models.level_model import Level
from app.core.models.subject_model import Subject


@dataclass
class RelatedWord:
    word_id: str
    word: str

    @property
    def url(self):
        return f"/view?id={self.word_id}"


class WordVersion:
    def __init__(
        self,
        wv_id,
        definition,
        characteristics,
        examples,
        non_examples,
        topics: list[Topic],
        levels: list[Level],
    ):
        self.wv_id = wv_id
        self.definition = definition
        self.characteristics = json.loads(characteristics) or "[]"
        self.examples = json.loads(examples) or "[]"
        self.non_examples = json.loads(non_examples) or "[]"
        self.levels = levels
        self.topics = topics


class Word:
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
