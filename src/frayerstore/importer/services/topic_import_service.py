from frayerstore.core.utils.slugify import slugify
from frayerstore.importer.dto.import_topic import ImportTopic
from frayerstore.importer.exceptions import TopicImportError
from frayerstore.models.topic_create import TopicCreate


class TopicImportService:
    def __init__(self, repo):
        self.repo = repo

    def import_topic(self, incoming: ImportTopic, stage_report):
        existing = self.repo.get_by_course_and_code(incoming.course_pk, incoming.code)

        if existing:
            if existing.name != incoming.name:
                msg = f"Topic code '{incoming.code}' already exists with a different name."
                stage_report.record_error(msg)
                raise TopicImportError(msg)
            stage_report.record_skipped(existing)
            return existing

        create_dto = TopicCreate(
            course_pk=incoming.course_pk,
            code=incoming.code,
            name=incoming.name,
            slug=slugify(incoming.name),
        )
        created = self.repo.create(create_dto)
        stage_report.record_created(created)
        return created
