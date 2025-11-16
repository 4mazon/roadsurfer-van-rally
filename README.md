# Roadsurfer Van-Rally Routes Checker

[![CI](https://github.com/4mazon/roadsurfer-van-rally/actions/workflows/ci.yml/badge.svg)](https://github.com/4mazon/roadsurfer-van-rally/actions)
[![Coverage](https://codecov.io/gh/4mazon/roadsurfer-van-rally/branch/main/graph/badge.svg)](https://codecov.io/gh/4mazon/roadsurfer-van-rally)
[![License](https://img.shields.io/github/license/4mazon/roadsurfer-van-rally)](https://github.com/4mazon/roadsurfer-van-rally/blob/main/LICENSE)
[![Ruff](https://github.com/4mazon/roadsurfer-van-rally/actions/workflows/ruff.yml/badge.svg)](https://github.com/4mazon/roadsurfer-van-rally/actions/workflows/ruff.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](#)

This is a simple script to check all rally routes offered by **Roadsurfer**.

## Why?

Currently, the company offers no way to filter by return location. This script outputs every route with available dates, making it easier to find the ones that interest you.

## How to Use

1. Clone the repository:

```sh
git clone https://github.com/4mazon/roadsurfer-van-rally.git
cd roadsurfer-van-rally
```

2. Run the script:

```sh
python main.py
```

The routes will appear in the terminal.

3. (Optional) Save the output to a file:

```sh
python main.py > routes.txt
```

Once you know the route you want, go to [Roadsurfer Rally Booking](https://booking.roadsurfer.com/en/rally/) and book your van!

## Development

### Installation

To set up the development environment with all testing tools:

```sh
pip install -e "[.dev]"
```

### Running Tests

Run all tests:

```sh
pytest tests/ -v
```

### Code Coverage

Check code coverage to see which lines are tested:

```sh
pytest --cov=api_utils --cov=data_utils --cov=main --cov-report=term-missing tests/
```

For a detailed HTML report:

```sh
pytest --cov=api_utils --cov=data_utils --cov=main --cov-report=html tests/
```

The HTML report will be generated in the `htmlcov/` directory.

### Code Quality

Lint code with ruff:

```sh
ruff check .
```

Format code automatically:

```sh
ruff format .
```

## Notes

> **Warning**
>
> Use this responsibly. The script will make more requests to Roadsurfer servers than a normal user would. As per my tests, available dates and routes do not change very often.

This software will be available until I receive a request from **Roadsurfer** to remove it.

There are also standard rates at [Roadsurfer.com](https://roadsurfer.com) ;)
