"""Unit tests for config_utils module."""

from collections.abc import Generator
from pathlib import Path

import pytest
import yaml

from config_utils import Config, ConfigurationError, get_config


@pytest.fixture(autouse=True)
def reset_config_singleton() -> Generator[None, None, None]:
    """Reset the Config singleton before and after each test."""
    Config._instance = None
    Config._config = None


def test_load_existing_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading an existing valid configuration file."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {
            "base_url": "https://test.com/api",
            "endpoints": {"stations": "/stations", "timeframes": "/timeframes"},
        },
        "maps": {"directions_url": "https://maps.test.com"},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    config = get_config()

    assert config.url_stations == "https://test.com/api/stations"
    assert config.url_timeframes == "https://test.com/api/timeframes"
    assert config.url_directions == "https://maps.test.com"


def test_auto_create_from_example(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test auto-creation of config.yaml from config.example.yaml when missing."""
    monkeypatch.chdir(tmp_path)

    example_content = {
        "api": {
            "base_url": "https://example.com/api",
            "endpoints": {"stations": "/sta", "timeframes": "/time"},
        },
        "maps": {"directions_url": "https://maps.example.com"},
    }

    example_path = tmp_path / "config.example.yaml"
    with example_path.open("w", encoding="utf-8") as f:
        yaml.dump(example_content, f)

    config_path = tmp_path / "config.yaml"
    assert not config_path.exists()

    config = get_config()

    assert config_path.exists()
    with config_path.open("r", encoding="utf-8") as f:
        created_content = yaml.safe_load(f)
    assert created_content == example_content
    assert config.url_stations == "https://example.com/api/sta"


def test_validate_required_fields(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test validation catches missing required fields."""
    monkeypatch.chdir(tmp_path)

    invalid_config = {
        "api": {
            "base_url": "https://test.com",
            "endpoints": {"stations": "/s", "timeframes": "/t"},
        }
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(invalid_config, f)

    with pytest.raises(ConfigurationError, match="Missing required field 'maps'"):
        get_config()


def test_invalid_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test handling of invalid YAML syntax."""
    monkeypatch.chdir(tmp_path)

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        f.write("invalid: yaml: syntax: [unclosed")

    with pytest.raises(ConfigurationError, match="Invalid YAML"):
        get_config()


def test_missing_example_template(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test error when both config.yaml and config.example.yaml are missing."""
    monkeypatch.chdir(tmp_path)

    assert not (tmp_path / "config.yaml").exists()
    assert not (tmp_path / "config.example.yaml").exists()

    with pytest.raises(ConfigurationError, match=r"config\.example\.yaml not found"):
        get_config()


def test_singleton_pattern() -> None:
    """Test that Config follows singleton pattern."""
    config1 = get_config()
    config2 = get_config()

    assert config1 is config2
    assert Config._instance is config1


def test_missing_api_base_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test validation catches missing api.base_url field."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {"endpoints": {"stations": "/s", "timeframes": "/t"}},
        "maps": {"directions_url": "https://maps.test.com"},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    with pytest.raises(ConfigurationError, match=r"api\.base_url"):
        get_config()


def test_missing_endpoint_field(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test validation catches missing endpoint fields."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {
            "base_url": "https://test.com",
            "endpoints": {"stations": "/s"},
        },
        "maps": {"directions_url": "https://maps.test.com"},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    with pytest.raises(ConfigurationError, match=r"api\.endpoints\.timeframes"):
        get_config()


def test_missing_maps_directions_url(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test validation catches missing maps.directions_url field."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {
            "base_url": "https://test.com",
            "endpoints": {"stations": "/s", "timeframes": "/t"},
        },
        "maps": {},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    with pytest.raises(ConfigurationError, match=r"maps\.directions_url"):
        get_config()
