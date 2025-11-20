from dataclasses import dataclass, field
from typing import Any


@dataclass
class ImportStageReport:
    label: str
    created: list[Any] = field(default_factory=list)
    skipped: list[Any] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def record_created(self, obj: object) -> None:
        """Append new object to created."""
        self.created.append(obj)
        return obj

    def record_skipped(self, obj: object) -> None:
        """Append new object to skipped."""
        self.skipped.append(obj)
        return obj

    def record_error(self, message: str) -> None:
        """Append new mesage to errors."""
        self.errors.append(message)
        return message

    def record_warning(self, message: str) -> None:
        """Append new message to warnings."""
        self.warnings.append(message)
        return message

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


@dataclass
class ImportReport:
    subjects: ImportStageReport
    courses: ImportStageReport
    topics: ImportStageReport
    words: ImportStageReport
