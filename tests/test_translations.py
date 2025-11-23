"""Unit tests for the translations module."""

import json
from pathlib import Path
from typing import Any
from unittest.mock import mock_open, patch

import pytest

from translations import DEFAULT_LANGUAGE, get_translation, load_translations


def test_load_translations_english() -> None:
    """Test loading English translations (default language)."""
    translations = load_translations("en")

    assert isinstance(translations, dict)
    assert "found_routes" in translations
    assert "origin" in translations
    assert translations["found_routes"] == "Showing found routes"


def test_load_translations_spanish() -> None:
    """Test loading Spanish translations."""
    translations = load_translations("es")

    assert isinstance(translations, dict)
    assert "found_routes" in translations
    assert "origin" in translations
    assert translations["found_routes"] == "Mostrando rutas encontradas"


def test_load_translations_invalid_language(capsys: pytest.CaptureFixture) -> None:
    """Test loading an invalid language falls back to English."""
    translations = load_translations("fr")

    # Should fall back to English
    assert isinstance(translations, dict)
    assert translations["found_routes"] == "Showing found routes"

    # Should print a warning to stderr
    captured = capsys.readouterr()
    assert "Warning: Translation file for 'fr' not found" in captured.err
    assert f"Falling back to {DEFAULT_LANGUAGE}" in captured.err


def test_get_translation_existing_key() -> None:
    """Test getting a translation for an existing key."""
    load_translations("en")
    translation = get_translation("found_routes")

    assert translation == "Showing found routes"


def test_get_translation_missing_key() -> None:
    """Test getting a translation for a missing key returns the key itself."""
    load_translations("en")
    translation = get_translation("nonexistent_key")

    assert translation == "nonexistent_key"


def test_get_translation_fallback_to_english() -> None:
    """Test that missing keys in Spanish fall back to English."""
    # Create a mock Spanish file with missing keys
    mock_es_data = {"found_routes": "Mostrando rutas encontradas"}
    mock_en_data = {
        "found_routes": "Showing found routes",
        "origin": "Origin",
        "destination": "Destination",
    }

    # Mock the file reading
    def mock_file_open(file_path: Path, *args: Any, **kwargs: Any) -> Any:
        file_str = str(file_path)
        if "es.json" in file_str:
            return mock_open(read_data=json.dumps(mock_es_data))()
        elif "en.json" in file_str:
            return mock_open(read_data=json.dumps(mock_en_data))()
        raise FileNotFoundError(f"No such file: {file_path}")

    with (
        patch("builtins.open", side_effect=mock_file_open),
        patch.object(Path, "exists", return_value=True),
    ):
        load_translations("es")

        # This key exists in Spanish
        assert get_translation("found_routes") == "Mostrando rutas encontradas"

        # This key only exists in English (fallback)
        assert get_translation("origin") == "Origin"


def test_default_language_is_english() -> None:
    """Test that the default language is English."""
    assert DEFAULT_LANGUAGE == "en"
