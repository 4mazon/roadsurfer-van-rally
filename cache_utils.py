"""
Cache utilities for storing and retrieving API responses.

Provides file-based caching for API responses with optional TTL.
"""

import json
import shutil
import time
from hashlib import md5
from pathlib import Path

CACHE_DIR = Path(".cache")
CACHE_TTL = 86400  # 24 hours in seconds


def _get_cache_key(url: str) -> str:
    """Generate a cache key from a URL."""
    return md5(url.encode()).hexdigest()


def _get_cache_file_path(cache_key: str) -> Path:
    """Get the full path for a cache file."""
    return CACHE_DIR / f"{cache_key}.json"


def _ensure_cache_dir() -> None:
    """Ensure the cache directory exists."""
    CACHE_DIR.mkdir(exist_ok=True)


def get_cached(url: str) -> dict | None:
    """
    Retrieve a cached response for a URL, if it exists and is not expired.

    Args:
    ----
        url (str): The URL to retrieve from cache.

    Returns:
    -------
        dict | None: The cached data if valid, None otherwise.

    """
    if not CACHE_DIR.exists():
        return None

    cache_key = _get_cache_key(url)
    cache_file = _get_cache_file_path(cache_key)

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, encoding="utf-8") as f:
            cache_data = json.load(f)

        # Check TTL
        if cache_data.get("timestamp", 0) + CACHE_TTL < time.time():
            return None  # Cache expired

        return cache_data.get("data")
    except (OSError, json.JSONDecodeError):
        return None


def set_cache(url: str, data: dict) -> None:
    """
    Store a response in the cache.

    Args:
    ----
        url (str): The URL the data came from.
        data (dict): The data to cache.

    """
    _ensure_cache_dir()

    cache_key = _get_cache_key(url)
    cache_file = _get_cache_file_path(cache_key)

    cache_data = {"timestamp": time.time(), "data": data}

    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)
    except OSError as e:
        print(f"Warning: Failed to write cache for {url}: {e}")


def clear_cache() -> None:
    """Clear all cached data."""
    if CACHE_DIR.exists():
        shutil.rmtree(CACHE_DIR)
