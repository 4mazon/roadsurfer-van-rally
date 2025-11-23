"""
Translation system for the van-rally application.

Supports multiple languages via JSON files with English as the default.
"""

import json
import sys
from pathlib import Path

# Default language
DEFAULT_LANGUAGE = "en"


class TranslationManager:

    """Manages translations for the application."""

    def __init__(self) -> None:
        """Initialize the translation manager with empty dictionaries."""
        self._translations: dict[str, str] = {}
        self._fallback_translations: dict[str, str] = {}
        self._translations_dir = Path(__file__).parent / "translations"

    def load_translations(self, language: str = DEFAULT_LANGUAGE) -> dict[str, str]:
        """
        Load translations from a JSON file for the specified language.

        Args:
        ----
            language (str): Language code (e.g., 'en', 'es'). Defaults to English.

        Returns:
        -------
            dict: Dictionary with translations for the specified language.

        """
        # Load the requested language
        language_file = self._translations_dir / f"{language}.json"

        if language_file.exists():
            with open(language_file, encoding="utf-8") as f:
                self._translations = json.load(f)
        else:
            # Warn if language not found and fall back to English
            if language != DEFAULT_LANGUAGE:
                print(
                    f"Warning: Translation file for '{language}' not found. "
                    f"Falling back to {DEFAULT_LANGUAGE}.",
                    file=sys.stderr,
                )
            # Load default language
            default_file = self._translations_dir / f"{DEFAULT_LANGUAGE}.json"
            if not default_file.exists():
                # If even default is missing, use empty dict and return early
                self._translations = {}
                print(
                    f"Error: Default translation file '{DEFAULT_LANGUAGE}.json' not found.",
                    file=sys.stderr,
                )
                return self._translations

            with open(default_file, encoding="utf-8") as f:
                self._translations = json.load(f)

        # Always load English as fallback for missing keys
        if language == DEFAULT_LANGUAGE:
            return self._translations

        fallback_file = self._translations_dir / f"{DEFAULT_LANGUAGE}.json"
        if not fallback_file.exists():
            return self._translations

        with open(fallback_file, encoding="utf-8") as f:
            self._fallback_translations = json.load(f)

        return self._translations

    def get_translation(self, key: str) -> str:
        """
        Get a translation for the given key.

        Falls back to English if the key is missing in the current language.

        Args:
        ----
            key (str): The translation key.

        Returns:
        -------
            str: The translated string, or the key itself if not found.

        """
        # Try current language first
        if key in self._translations:
            return self._translations[key]

        # Fall back to English
        if key in self._fallback_translations:
            return self._fallback_translations[key]

        # If all else fails, return the key itself
        return key

    @property
    def translations(self) -> dict[str, str]:
        """Get the current translations dictionary."""
        return self._translations


# Create a singleton instance
_manager = TranslationManager()

# Initialize with default language
_manager.load_translations()


# Public API - maintain backward compatibility
def load_translations(language: str = DEFAULT_LANGUAGE) -> dict[str, str]:
    """
    Load translations from a JSON file for the specified language.

    Args:
    ----
        language (str): Language code (e.g., 'en', 'es'). Defaults to English.

    Returns:
    -------
        dict: Dictionary with translations for the specified language.

    """
    return _manager.load_translations(language)


def get_translation(key: str) -> str:
    """
    Get a translation for the given key.

    Falls back to English if the key is missing in the current language.

    Args:
    ----
        key (str): The translation key.

    Returns:
    -------
        str: The translated string, or the key itself if not found.

    """
    return _manager.get_translation(key)
