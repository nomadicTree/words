from frayerstore.importer.dto.import_topic import ImportTopic


class TopicImportCoordinator:
    def __init__(self, topic_service):
        self.topic_service = topic_service  # NOT generic importer

    def import_topic(self, data: dict, course_pk: int, report):
        incoming = ImportTopic.from_yaml(data, course_pk=course_pk)

        # Topic service must use get_by_course_and_code instead of get_by_name
        topic = self.topic_service.import_topic(
            incoming,
            report.topics,
        )

        return topic
