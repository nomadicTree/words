from dataclasses import dataclass
from typing import Optional
from app.core.models.subject_model import Subject
from app.core.models.level_model import Level


@dataclass
class SearchFilters:
    subject: Optional[Subject] = None
    level: Optional[Level] = None


@dataclass
class SearchHit:
    word_id: int
    word: str
    word_slug: str
    subject_slug: str

    version_id: int
    version_definition: str
    level_names: list[str]

    synonyms: list[str]  # maybe empty
    search_text: str  # raw searchable text

    matched_token: str

    @property
    def level_set_slug(self) -> str:
        parts = sorted(name.lower().replace(" ", "-") for name in self.level_names)
        return "-".join(parts) if parts else ""
