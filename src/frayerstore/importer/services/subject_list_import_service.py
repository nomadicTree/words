from frayerstore.importer.dto.import_subject import ImportSubject
from frayerstore.importer.services.subject_import_service import SubjectImportService


class SubjectListImportService:
    def __init__(self, import_service: SubjectImportService):
        self.import_service = import_service

    def import_many(self, data_list, report):
        for raw in data_list:
            incoming = ImportSubject.from_yaml(raw)
            self.import_service.import_subject(incoming, report.subjects)
