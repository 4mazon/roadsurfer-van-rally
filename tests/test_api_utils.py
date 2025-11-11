"""Unit tests for api_utils module."""
import json
from pathlib import Path
from unittest.mock import MagicMock
from urllib.error import HTTPError, URLError

import pytest
from pytest_mock import MockerFixture

from api_utils import (
    get_json_from_url,
    get_station_data,
    get_station_transfer_dates,
    get_stations_data,
)

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def stations_list_fixture() -> list:
    """Load stations list fixture."""
    with open(FIXTURES_DIR / "stations_list.json", encoding="utf-8") as f:
        return json.load(f)["data"]


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


def test_get_json_from_url_success(mocker: MockerFixture) -> None:
    """Test successful JSON retrieval from URL."""
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"key": "value", "id": 123}'
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None

    mocker.patch("api_utils.urlopen", return_value=mock_response)

    result = get_json_from_url("http://test.com", {"header": "value"})
    assert result == {"key": "value", "id": 123}


def test_get_json_from_url_http_error(mocker: MockerFixture) -> None:
    """Test HTTP error handling."""
    mock_error = HTTPError("http://test.com", 404, "Not Found", {}, None)
    mocker.patch("api_utils.urlopen", side_effect=mock_error)

    result = get_json_from_url("http://test.com", {})
    assert result is None


def test_get_json_from_url_url_error(mocker: MockerFixture) -> None:
    """Test URL error handling."""
    mock_error = URLError("Connection failed")
    mocker.patch("api_utils.urlopen", side_effect=mock_error)

    result = get_json_from_url("http://test.com", {})
    assert result is None


MADRID_STATION_ID = 20


def test_get_station_data_single_station(
    mocker: MockerFixture, station_detail_fixture: dict
) -> None:
    """Test getting data for a single station using fixture data."""
    mocker.patch("api_utils.get_json_from_url", return_value=station_detail_fixture)

    result = get_station_data(MADRID_STATION_ID)
    assert result == station_detail_fixture
    assert result["id"] == MADRID_STATION_ID
    assert result["name"] == "Madrid"


def test_get_station_data_all_stations(mocker: MockerFixture, stations_list_fixture: list) -> None:
    """Test getting data for all stations using fixture data."""
    mocker.patch("api_utils.get_json_from_url", return_value=stations_list_fixture)

    result = get_station_data(None)
    assert result == stations_list_fixture
    assert len(result) > 0
    assert result[0]["id"] == 1


def test_get_stations_data(mocker: MockerFixture, stations_list_fixture: list) -> None:
    """Test getting all stations data using fixture."""
    mocker.patch("api_utils.get_station_data", return_value=stations_list_fixture)

    result = get_stations_data()
    assert result == stations_list_fixture
    assert len(result) > 0


def test_get_station_transfer_dates(mocker: MockerFixture, transfer_dates_fixture: list) -> None:
    """Test getting transfer dates between two stations using fixture."""
    mocker.patch("api_utils.get_json_from_url", return_value=transfer_dates_fixture)

    result = get_station_transfer_dates(1, 2)
    assert result == transfer_dates_fixture
    assert len(result) > 0
    assert "startDate" in result[0]
    assert "endDate" in result[0]
