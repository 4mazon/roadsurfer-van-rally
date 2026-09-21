"""
Module to handle YAML configuration loading for the van-rally application.

Loads an explicit file, a local config.yaml, or read-only bundled defaults.
"""

from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml

LANGUAGE_CODE_LENGTH = 2


class ConfigurationError(Exception):
    """Raised when there is an error with the configuration."""


class Config:
    """Configuration manager with singleton pattern."""

    _instance: Config | None = None
    _config: dict[str, Any] | None = None

    def __new__(cls, config_path: Path | None = None) -> Config:
        """Ensure only one instance of Config exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: Path | None = None) -> None:
        """Initialize configuration if not already loaded."""
        if self._config is None or config_path is not None:
            self._config = self._load_config(config_path)

    def _load_config(self, config_path: Path | None = None) -> dict[str, Any]:
        """
        Load an explicit path, local config.yaml, or bundled defaults, in that order.

        Never create configuration files or silently ignore an invalid explicit path.

        Returns
        -------
            dict: Configuration data.

        Raises
        ------
            ConfigurationError: If configuration file is invalid or missing.

        """
        if config_path is None:
            local_path = Path("config.yaml")
            config_path = (
                local_path
                if local_path.exists()
                else files("van_rally").joinpath("config.example.yaml")
            )

        # Load the config file
        try:
            with config_path.open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            msg = f"Invalid YAML in {config_path}: {e}"
            raise ConfigurationError(msg) from e
        except OSError as e:
            msg = f"Error reading {config_path}: {e}"
            raise ConfigurationError(msg) from e

        # Validate configuration structure
        self._validate_config(config)

        return config

    @staticmethod
    def _validate_config(config: dict[str, Any]) -> None:
        """
        Validate that the configuration has all required fields.

        Args:
        ----
            config (dict): Configuration dictionary to validate.

        Raises:
        ------
            ConfigurationError: If required fields are missing.

        """
        if not isinstance(config, dict):
            msg = "Configuration must be a YAML mapping"
            raise ConfigurationError(msg)

        required_fields = {
            "": ["api", "maps", "language_map"],
            "api": ["base_url", "endpoints"],
            "maps": ["directions_url"],
            "language_map": [],
            "api.endpoints": ["stations", "timeframes"],
        }
        for section, fields in required_fields.items():
            value = config
            for part in section.split(".") if section else []:
                value = value[part]
            if not isinstance(value, dict):
                msg = f"Configuration field '{section}' must be a mapping"
                raise ConfigurationError(msg)
            for field in fields:
                if field not in value:
                    path = f"{section}.{field}" if section else field
                    msg = f"Missing required field '{path}' in configuration"
                    raise ConfigurationError(msg)

    def get_api_language_code(self, language: str) -> str:
        """
        Get the API language code for a given language.

        Args:
        ----
            language (str): The language code (e.g., 'en', 'es').

        Returns:
        -------
            str: The API language code (e.g., 'en-GB', 'es-ES').
                 Defaults to 'en-GB' if not found.

        """
        return self._config.get("language_map", {}).get(language, "en-GB")

    @property
    def language(self) -> str:
        """The current language code."""
        return getattr(self, "_language", "en")

    def set_language(self, language: str) -> None:
        """
        Set the language for API calls.

        Args:
        ----
            language (str): Language code (e.g., 'en', 'es').

        """
        self._language = language

    @property
    def _base_url(self) -> str:
        """The base URL without a legacy language suffix."""
        url = self._config["api"]["base_url"]
        # Strip trailing slash
        url = url.rstrip("/")
        # If URL ends with a known language code (2 chars), strip it
        # This is a simple heuristic to support old configs
        parts = url.split("/")
        if len(parts[-1]) == LANGUAGE_CODE_LENGTH:
            return "/".join(parts[:-1])
        return url

    @property
    def url_stations(self) -> str:
        """The full URL for the stations endpoint."""
        endpoint = self._config["api"]["endpoints"]["stations"]
        return f"{self._base_url}/{self.language}{endpoint}"

    @property
    def url_timeframes(self) -> str:
        """The full URL for the timeframes endpoint."""
        endpoint = self._config["api"]["endpoints"]["timeframes"]
        return f"{self._base_url}/{self.language}{endpoint}"

    @property
    def url_directions(self) -> str:
        """The URL for Google Maps directions."""
        return self._config["maps"]["directions_url"]


def get_config(config_path: Path | None = None) -> Config:
    """
    Get the singleton Config instance, optionally loading an explicit file.

    Returns
    -------
        Config: The configuration instance.

    """
    return Config(config_path)
