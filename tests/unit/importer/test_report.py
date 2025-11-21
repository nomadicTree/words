from frayerstore.importer.report import ImportStageReport


def test_record_warning():
    report = ImportStageReport("Test")
    out = report.record_warning("warn")
    assert out == "warn"
    assert report.warnings == ["warn"]


def test_has_errors_true():
    report = ImportStageReport("Test")
    report.record_error("oops")
    assert report.has_errors is True


def test_has_errors_false():
    report = ImportStageReport("Test")
    assert report.has_errors is False
