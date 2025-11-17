"""Tests for cache utilities and API caching behavior."""

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from api_utils import (
    get_json_from_url,
    get_station_data,
    get_station_transfer_dates,
)
from cache_utils import (
    CACHE_DIR,
    CACHE_TTL,
    _get_cache_file_path,
    _get_cache_key,
    clear_cache,
    get_cached,
    set_cache,
)


@pytest.fixture(autouse=True)
def cleanup_cache() -> None:
    """Clear cache before and after each test."""
    clear_cache()
    yield
    clear_cache()


class TestCacheUtils:

    """Tests for cache_utils module."""

    def test_set_and_get_cache(self) -> None:
        """Test basic cache set and get operations."""
        url = "https://example.com/test"
        data = {"key": "value", "nested": {"data": 123}}

        set_cache(url, data)
        cached = get_cached(url)

        assert cached == data
        assert CACHE_DIR.exists()

    def test_get_cache_nonexistent_url(self) -> None:
        """Test getting cache for URL that was never cached."""
        url = "https://example.com/nonexistent"
        cached = get_cached(url)

        assert cached is None

    def test_get_cache_expired(self) -> None:
        """Test that expired cache is not returned."""
        url = "https://example.com/test"
        data = {"key": "value"}

        set_cache(url, data)

        # Manually modify cache file to set old timestamp
        cache_key = _get_cache_key(url)
        cache_file = _get_cache_file_path(cache_key)

        with open(cache_file, encoding="utf-8") as f:
            cache_data = json.load(f)

        cache_data["timestamp"] = time.time() - (CACHE_TTL + 1)

        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache_data, f)

        # Expired cache should not be returned
        cached = get_cached(url)
        assert cached is None

    def test_clear_cache(self) -> None:
        """Test clearing the cache directory."""
        url = "https://example.com/test"
        data = {"key": "value"}

        set_cache(url, data)
        assert CACHE_DIR.exists()

        clear_cache()
        assert not CACHE_DIR.exists()


class TestAPIUtilsCaching:

    """Tests for API caching behavior."""

    def test_get_json_from_url_with_cache_stores_data(self) -> None:
        """Test that get_json_from_url stores data in cache when use_cache=True."""
        url = "https://example.com/api"
        response_data = {"stations": [{"id": 1, "name": "Station A"}]}

        with patch("api_utils.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(response_data).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            result = get_json_from_url(url, {}, use_cache=True)

            assert result == response_data
            assert get_cached(url) == response_data

    def test_get_json_from_url_returns_cached_data(self) -> None:
        """Test that cached data is returned without making a new request."""
        url = "https://example.com/api"
        cached_data = {"cached": True, "id": 123}

        set_cache(url, cached_data)

        with patch("api_utils.urlopen") as mock_urlopen:
            result = get_json_from_url(url, {}, use_cache=True)

            # Should not call urlopen since data is cached
            mock_urlopen.assert_not_called()
            assert result == cached_data

    def test_get_json_from_url_without_cache_ignores_cache(self) -> None:
        """Test that cache is ignored when use_cache=False."""
        url = "https://example.com/api"
        cached_data = {"cached": True}
        fresh_data = {"cached": False, "fresh": True}

        set_cache(url, cached_data)

        with patch("api_utils.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(fresh_data).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            result = get_json_from_url(url, {}, use_cache=False)

            # Should fetch fresh data and not return cached
            assert result == fresh_data
            mock_urlopen.assert_called_once()

    def test_get_station_data_with_id_uses_cache(self) -> None:
        """Test that get_station_data with station_id uses cache."""
        station_id = 20
        station_data = {"id": 20, "name": "Madrid", "address": "Madrid, Spain"}

        with patch("api_utils.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(station_data).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            # First call - should fetch and cache
            result1 = get_station_data(station_id)
            assert result1 == station_data

            # Second call - should use cache
            result2 = get_station_data(station_id)
            assert result2 == station_data
            # Should only have called urlopen once (first call)
            assert mock_urlopen.call_count == 1

    def test_get_station_data_without_id_no_cache(self) -> None:
        """Test that get_station_data(None) does NOT use cache."""
        all_stations_data = [
            {"id": 1, "name": "Station 1"},
            {"id": 2, "name": "Station 2"},
        ]

        with patch("api_utils.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(all_stations_data).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            # First call
            result1 = get_station_data(None)
            assert result1 == all_stations_data

            # Second call - should NOT use cache, should fetch again
            result2 = get_station_data(None)
            assert result2 == all_stations_data
            # Should have called urlopen twice (both calls fetch fresh)
            assert mock_urlopen.call_count == 2

    def test_get_station_transfer_dates_uses_cache(self) -> None:
        """Test that get_station_transfer_dates uses cache."""
        origin_id, dest_id = 1, 2
        dates_data = [
            {"startDate": "2025-01-01", "endDate": "2025-01-08"},
            {"startDate": "2025-01-15", "endDate": "2025-01-22"},
        ]

        with patch("api_utils.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(dates_data).encode()
            mock_urlopen.return_value.__enter__.return_value = mock_response

            # First call - should fetch and cache
            result1 = get_station_transfer_dates(origin_id, dest_id)
            assert result1 == dates_data

            # Second call - should use cache
            result2 = get_station_transfer_dates(origin_id, dest_id)
            assert result2 == dates_data
            # Should only have called urlopen once
            assert mock_urlopen.call_count == 1
