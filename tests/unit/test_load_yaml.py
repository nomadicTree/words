import pytest
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


def test_yaml_not_mapping(tmp_path):
    invalid_mapping_file = tmp_path / "invalid_mapping.yaml"
    invalid_mapping_file.write_text("- a\n- b\n - c")
    with pytest.raises(InvalidYamlStructure):
        load_yaml(invalid_mapping_file)


def test_valid_yaml(tmp_path):
    valid_yaml_file = tmp_path / "valid.yaml"
    valid_yaml_file.write_text("subject:\n  name: Computing\n  slug: computing\n")
    data = load_yaml(valid_yaml_file)
    assert isinstance(data, dict)
    assert "subject" in data
    assert data["subject"]["name"] == "Computing"
    assert data["subject"]["slug"] == "computing"
