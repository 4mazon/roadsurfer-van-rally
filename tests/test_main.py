"""Unit tests for main module."""

import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from van_rally.main import main, parse_arguments

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Constants for test data
FIRST_STATIONS_COUNT = 2
RETURN_STATIONS_IDS = [2, 3]


def test_parse_arguments_defaults(mocker: MockerFixture) -> None:
    """Test parsing arguments with defaults."""
    mocker.patch("sys.argv", ["van-rally"])
    args = parse_arguments()
    assert args.language == "en"
    assert args.config is None


def test_parse_arguments_custom_language(mocker: MockerFixture) -> None:
    """Test parsing arguments with custom language."""
    mocker.patch("sys.argv", ["van-rally", "--language", "es"])
    args = parse_arguments()
    assert args.language == "es"

    mocker.patch("sys.argv", ["van-rally", "-l", "de"])
    args = parse_arguments()
    assert args.language == "de"


@pytest.fixture
def stations_list_fixture() -> list:
    """Load stations list fixture."""
    with open(FIXTURES_DIR / "stations_list.json", encoding="utf-8") as f:
        return json.load(f)["data"]


def test_main_no_rally_stations(mocker: MockerFixture, stations_list_fixture: list) -> None:
    """Test main function when no rally stations are found using fixture data."""
    # Use only first 2 stations from fixture for this test
    mock_stations = stations_list_fixture[:FIRST_STATIONS_COUNT]

    # Mock argument parsing to return default language
    mock_args = mocker.Mock()
    mock_args.language = "en"
    mock_args.config = None
    mocker.patch("van_rally.main.parse_arguments", return_value=mock_args)

    mocker.patch("van_rally.main.get_stations_data", return_value=mock_stations)
    mocker.patch("van_rally.main.get_stations_with_rally", return_value=[])
    mocker.patch("van_rally.main.load_translations")
    mock_output_title = mocker.patch("van_rally.main.output_obtaining_station_list_title")
    mock_no_stations = mocker.patch("van_rally.main.print_no_stations_with_rally_found")
    mock_print_routes = mocker.patch("van_rally.main.print_routes_for_stations")

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

    # Mock argument parsing to return default language
    mock_args = mocker.Mock()
    mock_args.language = "en"
    mock_args.config = None
    mocker.patch("van_rally.main.parse_arguments", return_value=mock_args)

    mocker.patch("van_rally.main.get_stations_data", return_value=mock_all_stations)
    mocker.patch("van_rally.main.get_stations_with_rally", return_value=mock_rally_stations)
    mocker.patch("van_rally.main.load_translations")
    mock_output_title = mocker.patch("van_rally.main.output_obtaining_station_list_title")
    mock_no_stations = mocker.patch("van_rally.main.print_no_stations_with_rally_found")
    mock_print_routes = mocker.patch("van_rally.main.print_routes_for_stations")

    main()

    mock_output_title.assert_called_once()
    mock_no_stations.assert_not_called()
    mock_print_routes.assert_called_once_with(mock_rally_stations)


def test_main_api_returns_none(mocker: MockerFixture) -> None:
    """Test main function when API returns None."""
    # Mock argument parsing to return default language
    mock_args = mocker.Mock()
    mock_args.language = "en"
    mock_args.config = None
    mocker.patch("van_rally.main.parse_arguments", return_value=mock_args)

    mocker.patch("van_rally.main.get_stations_data", return_value=None)
    mock_get_rally = mocker.patch("van_rally.main.get_stations_with_rally")
    mocker.patch("van_rally.main.load_translations")
    mock_output_title = mocker.patch("van_rally.main.output_obtaining_station_list_title")
    mock_no_stations = mocker.patch("van_rally.main.print_no_stations_with_rally_found")

    # Now main handles None gracefully
    main()

    mock_output_title.assert_called_once()
    mock_no_stations.assert_called_once()
    mock_get_rally.assert_not_called()


def test_parse_config_argument(mocker: MockerFixture, tmp_path: Path) -> None:
    """Parse an explicit configuration file path."""
    config_path = tmp_path / "custom.yaml"
    mocker.patch("sys.argv", ["van-rally", "--config", str(config_path)])
    assert parse_arguments().config == config_path


def test_main_invalid_config(
    mocker: MockerFixture, tmp_path: Path, capsys: pytest.CaptureFixture
) -> None:
    """Fail cleanly before making API requests when configuration is invalid."""
    mocker.patch("sys.argv", ["van-rally", "--config", str(tmp_path / "missing.yaml")])
    request = mocker.patch("van_rally.main.get_stations_data")
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 2
    assert "Configuration error:" in capsys.readouterr().err
    request.assert_not_called()


def test_main_uses_explicit_config(mocker: MockerFixture, tmp_path: Path) -> None:
    """Forward the selected file and language to the shared configuration."""
    config_path = tmp_path / "custom.yaml"
    mocker.patch("sys.argv", ["van-rally", "--config", str(config_path), "-l", "es"])
    config = mocker.patch("van_rally.main.get_config")
    mocker.patch("van_rally.main.get_stations_data", return_value=None)
    main()
    config.assert_called_once_with(config_path)
    config.return_value.set_language.assert_called_once_with("es")
