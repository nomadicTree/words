class ImporterError(Exception):
    """Base clase for all importer exceptions."""


class YamlLoadError(ImporterError):
    """Raised when YAML cannot be parsed."""

    pass


class InvalidYamlStructure(ImporterError):
    """Raised when YAML is syntactically valid but structurally wrong."""

    pass


class SubjectImportError(ImporterError):
    pass


class SubjectImportCollision(ImporterError):
    """Raised when attempting to import a subject that conflicts with an existing subject."""

    pass
