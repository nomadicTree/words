import pytest
from textwrap import dedent
from frayerstore.importer.exceptions import (
    YamlLoadError,
    InvalidYamlStructure,
)
from frayerstore.importer.yaml_utils import load_yaml


def test_missing_file(tmp_path):
    nonexistent_file = tmp_path / "does_not_exist.yaml"
    with pytest.raises(FileNotFoundError):
        load_yaml(nonexistent_file)


def test_invalid_yaml(tmp_path):
    invalid_yaml_file = tmp_path / "invalid.yaml"
    invalid_yaml_file.write_text(": \n - broken")
    with pytest.raises(YamlLoadError):
        load_yaml(invalid_yaml_file)


def test_empty_file(tmp_path):
    empty_file = tmp_path / "empty.yaml"
    empty_file.write_text("")
    with pytest.raises(YamlLoadError):
        load_yaml(empty_file)


def test_explicit_null(tmp_path):
    null_file = tmp_path / "null.yaml"
    null_file.write_text("null")
    with pytest.raises(YamlLoadError):
        load_yaml(null_file)


def test_empty_newline(tmp_path):
    empty_newline_file = tmp_path / "newline.yaml"
    empty_newline_file.write_text("\n")
    with pytest.raises(YamlLoadError):
        load_yaml(empty_newline_file)


def test_yaml_not_mapping(tmp_path):
    invalid_mapping_file = tmp_path / "invalid_mapping.yaml"
    invalid_mapping_file.write_text("- a\n- b\n - c")
    with pytest.raises(InvalidYamlStructure):
        load_yaml(invalid_mapping_file)


def test_valid_yaml(tmp_path):
    valid_yaml_file = tmp_path / "valid.yaml"
    valid_yaml_file.write_text(
        dedent("""
        subject:
          name: Computing
          slug: computing
        """)
    )
    data = load_yaml(valid_yaml_file)
    assert isinstance(data, dict)
    assert "subject" in data
    assert data["subject"]["name"] == "Computing"
    assert data["subject"]["slug"] == "computing"


def test_valid_nested_yaml(tmp_path):
    valid_nested_file = tmp_path / "valid_nested.yaml"
    valid_nested_file.write_text(
        dedent("""
        subject:
          name: Computing
          slug: computing
        courses:
          ocr_h446:
            name: OCR H446
            codes:
              - 2.2.1
        """)
    )
    data = load_yaml(valid_nested_file)

    assert isinstance(data, dict)
    assert "subject" in data
    assert data["subject"]["name"] == "Computing"
    assert data["subject"]["slug"] == "computing"
    assert "ocr_h446" in data["courses"]
    assert data["courses"]["ocr_h446"]["name"] == "OCR H446"
    assert "2.2.1" in data["courses"]["ocr_h446"]["codes"]
