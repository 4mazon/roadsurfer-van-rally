"""Isolate application state and filesystem writes for every test."""

from collections.abc import Generator
from pathlib import Path

import pytest

from van_rally import cache_utils
from van_rally.config_utils import Config
from van_rally.translations import load_translations


@pytest.fixture(autouse=True)
def isolate_application_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[None]:
    """Keep tests independent of personal configuration, cache, and working directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cache_utils, "CACHE_DIR", tmp_path / "cache" / "responses")
    Config._instance = None
    Config._config = None
    load_translations("en")
    yield
    Config._instance = None
    Config._config = None
    load_translations("en")
