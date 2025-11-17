"""Unit tests for data_utils module."""

import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from data_utils import (
    get_stations_with_rally,
    print_available_dates,
    print_routes_for_stations,
    print_station_destination_with_route_url,
    print_station_destinations,
)

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Constants for test data
EXPECTED_RALLY_STATIONS_COUNT = 2
EXPECTED_DATE_CALLS_COUNT = 2
MADRID_STATION_ID = 20
EXPECTED_ROUTE_CALLS_COUNT = 2


@pytest.fixture
def station_detail_fixture() -> dict:
    """Load station detail fixture."""
    with open(FIXTURES_DIR / "station_detail.json", encoding="utf-8") as f:
        return json.load(f)["data"]


@pytest.fixture
def transfer_dates_fixture() -> list:
    """Load transfer dates fixture."""
    with open(FIXTURES_DIR / "transfer_dates.json", encoding="utf-8") as f:
        return json.load(f)["data"]


def test_get_stations_with_rally_filters_correctly(
    mocker: MockerFixture, station_detail_fixture: dict
) -> None:
    """Test filtering stations with rally capability using fixture data."""
    mock_stations = [
        {"id": 1, "name": "Station 1", "one_way": True},
        {"id": 2, "name": "Station 2", "one_way": False},
        {"id": 3, "name": "Station 3", "one_way": True},
        {"id": 4, "name": "Station 4"},  # no one_way key
    ]

    mocker.patch("data_utils.get_station_data", return_value=station_detail_fixture)

    result = get_stations_with_rally(mock_stations)

    # Should only return stations with one_way=True (stations 1 and 3)
    assert len(result) == EXPECTED_RALLY_STATIONS_COUNT
    assert all(station == station_detail_fixture for station in result)


def test_get_stations_with_rally_empty_list(mocker: MockerFixture) -> None:
    """Test with empty station list."""
    result = get_stations_with_rally([])
    assert result == []


def test_print_available_dates(mocker: MockerFixture) -> None:
    """Test printing available dates."""
    mock_dates = [
        {"startDate": "2025-12-01T00:00:00Z", "endDate": "2025-12-10T00:00:00Z"},
        {"startDate": "2025-12-15T00:00:00Z", "endDate": "2025-12-25T00:00:00Z"},
    ]

    mock_output = mocker.patch("data_utils.output_available_dates")

    print_available_dates(mock_dates)

    # Verify output function was called with formatted dates
    assert mock_output.call_count == EXPECTED_DATE_CALLS_COUNT
    mock_output.assert_any_call("01/12/2025", "10/12/2025")
    mock_output.assert_any_call("15/12/2025", "25/12/2025")


def test_print_station_destination_with_route_url(
    mocker: MockerFixture, station_detail_fixture: dict
) -> None:
    """Test printing station destination with route URL using fixture data."""
    station = {
        "id": 1,
        "name": "Origin Station",
        "address": "123 Main St, City, Country",
    }

    mocker.patch("data_utils.get_station_data", return_value=station_detail_fixture)
    mock_output_title = mocker.patch("data_utils.output_destination_title")
    mock_output_url = mocker.patch("data_utils.output_destination_with_route_url")

    print_station_destination_with_route_url(station, MADRID_STATION_ID)

    mock_output_title.assert_called_once()
    mock_output_url.assert_called_once()

    # Verify the destination name is passed
    call_args = mock_output_url.call_args[0]
    assert call_args[0] == station_detail_fixture["name"]


def test_print_station_destinations(mocker: MockerFixture, transfer_dates_fixture: list) -> None:
    """Test printing all destinations for a station using fixture data."""
    station = {
        "id": 1,
        "name": "Origin Station",
        "address": "123 Main St",
        "returns": [2, 3],
    }

    mock_output_origin = mocker.patch("data_utils.output_origin")
    mocker.patch("data_utils.print_station_destination_with_route_url")
    mocker.patch("data_utils.get_station_transfer_dates", return_value=transfer_dates_fixture)
    mocker.patch("data_utils.print_available_dates")

    print_station_destinations(station)

    mock_output_origin.assert_called_once_with("Origin Station")


def test_print_routes_for_stations(mocker: MockerFixture) -> None:
    """Test printing routes for multiple stations."""
    stations = [
        {"id": 1, "name": "Station 1", "returns": [2]},
        {"id": 3, "name": "Station 3", "returns": [4]},
    ]

    mock_output_title = mocker.patch("data_utils.output_found_routes_title")
    mock_print_destinations = mocker.patch("data_utils.print_station_destinations")

    print_routes_for_stations(stations)

    mock_output_title.assert_called_once()
    assert mock_print_destinations.call_count == EXPECTED_ROUTE_CALLS_COUNT
