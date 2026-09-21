"""Unit tests for config_utils module."""

from pathlib import Path

import pytest
import yaml

from van_rally.config_utils import Config, ConfigurationError, get_config


def test_load_existing_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test loading an existing valid configuration file."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {
            "base_url": "https://test.com/api",
            "endpoints": {"stations": "/stations", "timeframes": "/timeframes"},
        },
        "maps": {"directions_url": "https://maps.test.com"},
        "language_map": {"en": "en-GB", "es": "es-ES"},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    config = get_config()

    assert config.url_stations == "https://test.com/api/en/stations"
    assert config.url_timeframes == "https://test.com/api/en/timeframes"
    assert config.url_directions == "https://maps.test.com"
    assert config.get_api_language_code("en") == "en-GB"
    assert config.get_api_language_code("es") == "es-ES"
    assert config.get_api_language_code("fr") == "en-GB"  # Default


def test_explicit_config_takes_precedence(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test an explicit configuration overrides the local file and remains active."""
    monkeypatch.chdir(tmp_path)

    example_content = {
        "api": {
            "base_url": "https://example.com/api",
            "endpoints": {"stations": "/sta", "timeframes": "/time"},
        },
        "maps": {"directions_url": "https://maps.example.com"},
        "language_map": {"en": "en-GB"},
    }

    example_path = tmp_path / "custom.yaml"
    with example_path.open("w", encoding="utf-8") as f:
        yaml.dump(example_content, f)

    config_path = tmp_path / "config.yaml"
    config_path.write_text("not: a valid configuration", encoding="utf-8")
    config = get_config(example_path)

    assert config_path.read_text(encoding="utf-8") == "not: a valid configuration"
    assert config.url_stations == "https://example.com/api/en/sta"
    assert get_config() is config
    assert get_config().url_stations == "https://example.com/api/en/sta"


def test_language_switching(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that changing language updates the URLs."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {
            "base_url": "https://test.com/api",
            "endpoints": {"stations": "/stations", "timeframes": "/timeframes"},
        },
        "maps": {"directions_url": "https://maps.test.com"},
        "language_map": {"en": "en-GB", "es": "es-ES"},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    config = get_config()

    # Default is 'en'
    assert config.language == "en"
    assert config.url_stations == "https://test.com/api/en/stations"

    # Switch to 'es'
    config.set_language("es")
    assert config.language == "es"
    assert config.url_stations == "https://test.com/api/es/stations"


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


def test_bundled_defaults(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test defaults work outside the checkout without creating local files."""
    monkeypatch.chdir(tmp_path)

    assert not (tmp_path / "config.yaml").exists()
    assert not (tmp_path / "config.example.yaml").exists()

    config = get_config()
    assert config.url_stations == "https://booking.roadsurfer.com/api/en/rally/stations"
    assert config.get_api_language_code("es") == "es-ES"
    assert list(tmp_path.iterdir()) == []


def test_missing_explicit_config(tmp_path: Path) -> None:
    """Never silently fall back when a requested file does not exist."""
    get_config()  # A previously loaded default must not hide a bad explicit path.
    with pytest.raises(ConfigurationError, match="Error reading"):
        get_config(tmp_path / "missing.yaml")


@pytest.mark.parametrize("content", ["", "[]", "42", "api: null\nmaps: {}\nlanguage_map: {}"])
def test_invalid_configuration_shape(tmp_path: Path, content: str) -> None:
    """Reject non-mapping configuration with a useful error."""
    config_path = tmp_path / "config.yaml"
    config_path.write_text(content, encoding="utf-8")
    with pytest.raises(ConfigurationError, match="mapping"):
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
        "language_map": {},
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
        "language_map": {},
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
        "language_map": {},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    with pytest.raises(ConfigurationError, match=r"maps\.directions_url"):
        get_config()


def test_missing_language_map(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test validation catches missing language_map field."""
    monkeypatch.chdir(tmp_path)

    config_content = {
        "api": {
            "base_url": "https://test.com",
            "endpoints": {"stations": "/s", "timeframes": "/t"},
        },
        "maps": {"directions_url": "https://maps.test.com"},
    }

    config_path = tmp_path / "config.yaml"
    with config_path.open("w", encoding="utf-8") as f:
        yaml.dump(config_content, f)

    with pytest.raises(ConfigurationError, match=r"language_map"):
        get_config()
