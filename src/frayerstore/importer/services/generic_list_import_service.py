from typing import Type, TypeVar, Generic, Callable

TIncoming = TypeVar("TIncoming")  # ImportSubject, ImportLevel, ...
TService = TypeVar("TService")  # SubjectImportService, LevelImportService
TStage = TypeVar("TStage")  # report.subjects, report.levels, ...


class GenericListImportService(Generic[TIncoming]):
    """
    Generic "import N items from a list" service.

    - Converts raw YAML dicts into ImportItem objects
    - Delegates each item to the corresponding single-item import service
    """

    def __init__(
        self,
        import_item_cls: Type[TIncoming],  # e.g. ImportSubject
        import_service: TService,  # e.g. SubjectImportService
        stage_selector: Callable[[object], TStage],  # lambda report: report.subjects
    ):
        self.import_item_cls = import_item_cls
        self.import_service = import_service
        self.stage_selector = stage_selector

    def import_many(self, data_list, report):
        stage_report = self.stage_selector(report)

        for raw in data_list:
            incoming = self.import_item_cls.from_yaml(raw)
            self.import_service.import_item(incoming, stage_report)
