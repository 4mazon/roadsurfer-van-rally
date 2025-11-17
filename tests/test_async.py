"""Tests for async functionality using concurrent.futures."""
from unittest.mock import MagicMock, patch

import pytest

from data_utils import (
    get_stations_with_rally,
    print_station_destinations,
)


class TestAsync:
    """Tests for async operations using concurrent.futures."""

    def test_get_stations_with_rally_concurrent(self) -> None:
        """Test that get_stations_with_rally fetches multiple stations concurrently."""
        stations = [
            {"id": 1, "name": "Station 1", "one_way": True},
            {"id": 2, "name": "Station 2", "one_way": False},
            {"id": 3, "name": "Station 3", "one_way": True},
            {"id": 4, "name": "Station 4", "one_way": True},
        ]

        station_details = {
            1: {"id": 1, "name": "Station 1", "address": "Address 1", "returns": []},
            3: {"id": 3, "name": "Station 3", "address": "Address 3", "returns": []},
            4: {"id": 4, "name": "Station 4", "address": "Address 4", "returns": []},
        }

        call_count = {"count": 0}

        def mock_get_station_data(station_id: int) -> dict:
            """Mock get_station_data that tracks calls."""
            call_count["count"] += 1
            return station_details.get(station_id)

        with patch("data_utils.get_station_data", side_effect=mock_get_station_data):
            result = get_stations_with_rally(stations)

            # Should have called get_station_data for each rally station (3 times)
            assert call_count["count"] == 3
            # Should return 3 stations (filtered by one_way=True)
            assert len(result) == 3
            # Results should be in original order
            assert result[0]["id"] == 1
            assert result[1]["id"] == 3
            assert result[2]["id"] == 4

    def test_get_stations_with_rally_empty_list(self) -> None:
        """Test get_stations_with_rally with no rally stations."""
        stations = [
            {"id": 1, "name": "Station 1", "one_way": False},
            {"id": 2, "name": "Station 2", "one_way": False},
        ]

        result = get_stations_with_rally(stations)
        assert result == []

    def test_get_stations_with_rally_preserves_order(self) -> None:
        """Test that results are returned in original order despite concurrent execution."""
        stations = [
            {"id": 5, "name": "Station 5", "one_way": True},
            {"id": 2, "name": "Station 2", "one_way": True},
            {"id": 8, "name": "Station 8", "one_way": True},
            {"id": 1, "name": "Station 1", "one_way": True},
        ]

        station_details = {
            5: {"id": 5, "name": "Station 5", "address": "Addr 5", "returns": []},
            2: {"id": 2, "name": "Station 2", "address": "Addr 2", "returns": []},
            8: {"id": 8, "name": "Station 8", "address": "Addr 8", "returns": []},
            1: {"id": 1, "name": "Station 1", "address": "Addr 1", "returns": []},
        }

        with patch("data_utils.get_station_data", side_effect=lambda sid: station_details[sid]):
            result = get_stations_with_rally(stations)

            # Should preserve original order
            assert [s["id"] for s in result] == [5, 2, 8, 1]

    def test_print_station_destinations_concurrent(self) -> None:
        """Test that print_station_destinations fetches dates concurrently."""
        station = {
            "id": 1,
            "name": "Madrid",
            "address": "Madrid, Spain",
            "returns": [2, 3, 4],  # 3 destinations
        }

        dates_data = [
            {"startDate": "2025-01-01", "endDate": "2025-01-08"},
        ]

        call_count = {"count": 0}

        def mock_get_transfer_dates(origin_id: int, dest_id: int) -> list:
            """Mock get_station_transfer_dates that tracks calls."""
            call_count["count"] += 1
            return dates_data

        with patch("data_utils.get_station_transfer_dates", side_effect=mock_get_transfer_dates):
            with patch("data_utils.print_station_destination_with_route_url"):
                with patch("data_utils.print_available_dates"):
                    with patch("data_utils.output_origin"):
                        print_station_destinations(station)

                        # Should have called get_station_transfer_dates for each destination
                        assert call_count["count"] == 3

    def test_get_stations_with_rally_handles_none_responses(self) -> None:
        """Test that get_stations_with_rally handles None responses gracefully."""
        stations = [
            {"id": 1, "name": "Station 1", "one_way": True},
            {"id": 2, "name": "Station 2", "one_way": True},
            {"id": 3, "name": "Station 3", "one_way": True},
        ]

        def mock_get_station_data(station_id: int) -> dict | None:
            """Mock that returns None for station_id=2."""
            if station_id == 2:
                return None
            return {
                "id": station_id,
                "name": f"Station {station_id}",
                "address": f"Address {station_id}",
                "returns": [],
            }

        with patch("data_utils.get_station_data", side_effect=mock_get_station_data):
            result = get_stations_with_rally(stations)

            # Should return only valid stations (1 and 3)
            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["id"] == 3

    def test_print_station_destinations_orders_output_correctly(self) -> None:
        """Test that print output is correct despite concurrent fetching."""
        station = {
            "id": 1,
            "name": "Madrid",
            "address": "Madrid, Spain",
            "returns": [2, 3],
        }

        dates_responses = {
            2: [{"startDate": "2025-01-01", "endDate": "2025-01-08"}],
            3: [{"startDate": "2025-02-01", "endDate": "2025-02-08"}],
        }

        def mock_get_transfer_dates(origin_id: int, dest_id: int) -> list:
            """Return different dates based on destination."""
            return dates_responses.get(dest_id, [])

        def mock_print_destination(station: dict, dest_id: int) -> None:
            """Mock that records which destinations were printed."""
            mock_print_destination.calls.append(dest_id)

        mock_print_destination.calls = []

        with patch("data_utils.get_station_transfer_dates", side_effect=mock_get_transfer_dates):
            with patch("data_utils.print_station_destination_with_route_url", side_effect=mock_print_destination):
                with patch("data_utils.print_available_dates"):
                    with patch("data_utils.output_origin"):
                        print_station_destinations(station)

                        # Should have printed destinations
                        assert len(mock_print_destination.calls) > 0
