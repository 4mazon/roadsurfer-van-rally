"""
Module to handle YAML configuration loading for the van-rally application.

Provides configuration management with auto-creation from template if missing.
"""

import shutil
from pathlib import Path
from typing import Any

import yaml

LANGUAGE_CODE_LENGTH = 2


class ConfigurationError(Exception):

    """Raised when there is an error with the configuration."""


class Config:

    """Configuration manager with singleton pattern."""

    _instance: "Config | None" = None
    _config: dict[str, Any] | None = None

    def __new__(cls) -> "Config":
        """Ensure only one instance of Config exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize configuration if not already loaded."""
        if self._config is None:
            self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """
        Load configuration from config.yaml.

        If config.yaml doesn't exist, create it from config.example.yaml.

        Returns
        -------
            dict: Configuration data.

        Raises
        ------
            ConfigurationError: If configuration file is invalid or missing.

        """
        config_path = Path("config.yaml")
        example_path = Path("config.example.yaml")

        # Auto-create config from example if missing
        if not config_path.exists():
            if not example_path.exists():
                msg = "config.example.yaml not found. Cannot create default configuration."
                raise ConfigurationError(msg)

            print(f"Creating {config_path} from {example_path}...")
            shutil.copy(example_path, config_path)

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
        required_fields = {
            "api": ["base_url", "endpoints"],
            "api.endpoints": ["stations", "timeframes"],
            "maps": ["directions_url"],
            "language_map": [],
        }

        # Check top-level fields
        for field in ["api", "maps", "language_map"]:
            if field not in config:
                msg = f"Missing required field '{field}' in configuration"
                raise ConfigurationError(msg)

        # Check api fields
        for field in required_fields["api"]:
            if field not in config["api"]:
                msg = f"Missing required field 'api.{field}' in configuration"
                raise ConfigurationError(msg)

        # Check api.endpoints fields
        for field in required_fields["api.endpoints"]:
            if field not in config["api"]["endpoints"]:
                msg = f"Missing required field 'api.endpoints.{field}' in configuration"
                raise ConfigurationError(msg)

        # Check maps fields
        for field in required_fields["maps"]:
            if field not in config["maps"]:
                msg = f"Missing required field 'maps.{field}' in configuration"
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
        """Get the current language code."""
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
        """Get the base URL, stripping any language suffix if present."""
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
        """Get the full URL for the stations endpoint."""
        endpoint = self._config["api"]["endpoints"]["stations"]
        return f"{self._base_url}/{self.language}{endpoint}"

    @property
    def url_timeframes(self) -> str:
        """Get the full URL for the timeframes endpoint."""
        endpoint = self._config["api"]["endpoints"]["timeframes"]
        return f"{self._base_url}/{self.language}{endpoint}"

    @property
    def url_directions(self) -> str:
        """Get the URL for Google Maps directions."""
        return self._config["maps"]["directions_url"]


def get_config() -> Config:
    """
    Get the singleton Config instance.

    Returns
    -------
        Config: The configuration instance.

    """
    return Config()
