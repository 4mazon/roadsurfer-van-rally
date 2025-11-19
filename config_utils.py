"""
Module to handle YAML configuration loading for the van-rally application.

Provides configuration management with auto-creation from template if missing.
"""

import shutil
from pathlib import Path
from typing import Any

import yaml


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
        }

        # Check top-level fields
        for field in ["api", "maps"]:
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

    @property
    def url_stations(self) -> str:
        """Get the full URL for the stations endpoint."""
        base = self._config["api"]["base_url"]
        endpoint = self._config["api"]["endpoints"]["stations"]
        return f"{base}{endpoint}"

    @property
    def url_timeframes(self) -> str:
        """Get the full URL for the timeframes endpoint."""
        base = self._config["api"]["base_url"]
        endpoint = self._config["api"]["endpoints"]["timeframes"]
        return f"{base}{endpoint}"

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
