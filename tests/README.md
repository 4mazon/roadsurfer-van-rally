# Tests

This directory contains the test suite for the van-rally project.

## Setup

Install the package with dev dependencies:

```bash
pip install -e ".[dev]"
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_api_utils.py
pytest tests/test_data_utils.py
pytest tests/test_main.py
```

### Run with verbose output
```bash
pytest -v
```

### Run with coverage report (terminal)
```bash
pytest --cov=api_utils --cov=data_utils --cov=main --cov-report=term-missing
```

### Run with HTML coverage report
```bash
pytest --cov=api_utils --cov=data_utils --cov=main --cov-report=html
```

This will generate an interactive HTML coverage report in `htmlcov/index.html`.

### Run specific test function
```bash
pytest tests/test_api_utils.py::test_get_json_from_url_success
```

## Test Structure

- **test_api_utils.py**: Tests for API interactions and network utilities
- **test_data_utils.py**: Tests for data processing and route formatting
- **test_main.py**: Tests for the main application flow

## Test Fixtures

The test suite uses pytest fixtures to load real API response data from JSON files. These fixtures mock actual API responses to ensure tests run consistently without making real API calls.

### Available Fixtures

Located in `fixtures/` directory:

- **stations_list.json** - List of all available stations with multilingual translations
- **station_detail.json** - Detailed information for a single station (Madrid)
- **transfer_dates.json** - Available transfer dates between stations

These fixtures are automatically loaded by the test files using pytest fixtures:

```python
@pytest.fixture
def stations_list_fixture():
    """Load stations list fixture."""
    with open(FIXTURES_DIR / "stations_list.json", encoding="utf-8") as f:
        return json.load(f)["data"]
```

## Writing Tests

All tests use `pytest` and `pytest-mock` for mocking external dependencies (API calls, file I/O, etc.).

Example test structure:
```python
def test_function_name(mocker, stations_list_fixture):
    """Test description."""
    # Use fixture data
    mock_data = stations_list_fixture
    mocker.patch("module.function", return_value=mock_data)
    
    # Call function
    result = function_under_test()
    
    # Assert results
    assert result == expected_value
```

## Coverage Goals

The project maintains high test coverage:
- **api_utils.py**: Tests all API interaction functions
- **data_utils.py**: Tests data filtering and formatting
- **main.py**: Tests main application flow (94% coverage - excludes `if __name__ == "__main__"`)

Current coverage can be checked with:
```bash
pytest --cov=api_utils --cov=data_utils --cov=main --cov-report=term-missing tests/
```

## Notes

- All fixtures use UTF-8 encoding to support international characters (umlauts, accents, etc.)
- Tests mock all external API calls to avoid hitting the live Roadsurfer API during testing
- The test suite is designed to run quickly and reliably in any environment
