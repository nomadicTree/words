import json
from app_lib.repositories import (
    get_topics_for_word,
    get_subject_name,
    get_related_words,
)


class Word:
    def __init__(self, row):
        self.id = row["id"]
        self.word = row["word"]
        self.definition = (
            row["definition"] if "definition" in row.keys() else ""
        )
        self.characteristics = (
            json.loads(row["characteristics"])
            if "characteristics" in row.keys()
            else []
        )
        self.examples = (
            json.loads(row["examples"]) if "examples" in row.keys() else []
        )
        self.non_examples = (
            json.loads(row["non_examples"])
            if "non_examples" in row.keys()
            else []
        )
        self.subject_name = row["subject_name"]

        topic_rows = get_topics_for_word(self.id)

        self.topics = [dict(r) for r in topic_rows]

        self._related_words = None

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "word": self.word,
            "definition": self.definition,
            "characteristics": self.characteristics,
            "examples": self.examples,
            "non_examples": self.non_examples,
            "subject_name": self.subject_name,
            "topics": self.topics,
            "related_words": self.related_words,
        }

    @property
    def related_words(self):
        return []
        if self._related_words is None:
            self._related_words = get_related_words(self.id)
            self._related_words = sorted(
                self._related_words, key=lambda w: w["word"]
            )
            # Add urls
            for w in self._related_words:
                w["url"] = f"/view?id={w["id"]}"
        return self._related_words
