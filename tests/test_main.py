"""Unit tests for main module."""
import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from main import main

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Constants for test data
FIRST_STATIONS_COUNT = 2
RETURN_STATIONS_IDS = [2, 3]


@pytest.fixture
def stations_list_fixture() -> list:
    """Load stations list fixture."""
    with open(FIXTURES_DIR / "stations_list.json", encoding="utf-8") as f:
        return json.load(f)["data"]


def test_main_no_rally_stations(mocker: MockerFixture, stations_list_fixture: list) -> None:
    """Test main function when no rally stations are found using fixture data."""
    # Use only first 2 stations from fixture for this test
    mock_stations = stations_list_fixture[:FIRST_STATIONS_COUNT]

    mocker.patch("main.get_stations_data", return_value=mock_stations)
    mocker.patch("main.get_stations_with_rally", return_value=[])
    mock_output_title = mocker.patch("main.output_obtaining_station_list_title")
    mock_no_stations = mocker.patch("main.print_no_stations_with_rally_found")
    mock_print_routes = mocker.patch("main.print_routes_for_stations")

    main()

    mock_output_title.assert_called_once()
    mock_no_stations.assert_called_once()
    mock_print_routes.assert_not_called()


def test_main_with_rally_stations(mocker: MockerFixture, stations_list_fixture: list) -> None:
    """Test main function when rally stations are found using fixture data."""
    # Use actual fixture data for all stations
    mock_all_stations = stations_list_fixture

    # Create mock rally station from fixture
    mock_rally_stations = [
        {
            **stations_list_fixture[0],
            "returns": RETURN_STATIONS_IDS,  # Add returns field for rally
        }
    ]

    mocker.patch("main.get_stations_data", return_value=mock_all_stations)
    mocker.patch("main.get_stations_with_rally", return_value=mock_rally_stations)
    mock_output_title = mocker.patch("main.output_obtaining_station_list_title")
    mock_no_stations = mocker.patch("main.print_no_stations_with_rally_found")
    mock_print_routes = mocker.patch("main.print_routes_for_stations")

    main()

    mock_output_title.assert_called_once()
    mock_no_stations.assert_not_called()
    mock_print_routes.assert_called_once_with(mock_rally_stations)


def test_main_api_returns_none(mocker: MockerFixture) -> None:
    """Test main function when API returns None."""
    mocker.patch("main.get_stations_data", return_value=None)
    mock_get_rally = mocker.patch("main.get_stations_with_rally")
    mock_output_title = mocker.patch("main.output_obtaining_station_list_title")
    mock_no_stations = mocker.patch("main.print_no_stations_with_rally_found")

    # Now main handles None gracefully
    main()

    mock_output_title.assert_called_once()
    mock_no_stations.assert_called_once()
    mock_get_rally.assert_not_called()
    mock_get_rally.assert_not_called()
