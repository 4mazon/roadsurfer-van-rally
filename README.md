# Roadsurfer Van-Rally Routes Checker

[![CI](https://github.com/4mazon/roadsurfer-van-rally/actions/workflows/ci.yml/badge.svg)](https://github.com/4mazon/roadsurfer-van-rally/actions)
[![Coverage](https://codecov.io/gh/4mazon/roadsurfer-van-rally/branch/main/graph/badge.svg)](https://codecov.io/gh/4mazon/roadsurfer-van-rally)
[![License](https://img.shields.io/github/license/4mazon/roadsurfer-van-rally)](https://github.com/4mazon/roadsurfer-van-rally/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/downloads/)

Display Roadsurfer rally routes and available dates, including return locations, in your terminal.

## Requirements

- **Python 3.14 or newer** (3.14 is the tested baseline) and Git.
- Python's built-in **venv** and **pip**. No uv, Poetry, or separate environment manager.
- An internet connection for installation and fetching routes.

Install Python before creating the environment: `venv` uses an existing interpreter; it does not download one.
Use the [Python downloads](https://www.python.org/downloads/) for macOS/Windows, or your Linux distribution's packages.
On Linux you may also need the matching `python3.14-venv` package.

PyYAML is the only runtime dependency. Testing, linting, and building tools are optional development dependencies.
Dependencies and package metadata are declared in `pyproject.toml`.

## Install

Clone the repository:

```sh
git clone https://github.com/4mazon/roadsurfer-van-rally.git
cd roadsurfer-van-rally
```

### macOS / Linux

```sh
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

For Homebrew on Apple Silicon, if `python3.14` is not on your PATH, use
`/opt/homebrew/bin/python3.14 -m venv .venv`.

### Windows (PowerShell)

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install .
```

If PowerShell blocks activation, no policy change is required: use
`.\.venv\Scripts\python.exe -m pip install .` and `.\.venv\Scripts\van-rally.exe` directly.

The `.venv/` directory is ignored by Git. Do not commit or copy environments between machines;
recreate them from `pyproject.toml`. Do not install this project into your system Python.

## Run

After activating the environment:

```sh
van-rally
van-rally --language es
van-rally --help
van-rally --version
van-rally > routes.txt
```

English (`en`) is the default; Spanish (`es`) is also available. `-l es` is the short form.
You can also run `python -m van_rally` with the same arguments. This replaces the old `python main.py` command.

In a new terminal, activate the environment again; you only need to install once.
Activation is optional: from the checkout run `.venv/bin/van-rally` on macOS/Linux,
or `.\.venv\Scripts\van-rally.exe` on Windows. An absolute path to that command works from any directory.

Run `deactivate` to leave the environment.

Once you find a route, book through [Roadsurfer Rally](https://booking.roadsurfer.com/en/rally/).

## Configuration and cache

Configuration is loaded in this order (the selected file is used as a whole, not merged):

1. The file supplied with `van-rally --config /path/to/config.yaml`.
2. `config.yaml` in the current working directory (including the existing checkout configuration).
3. The default configuration bundled with the installed package.

Missing or invalid explicit files produce an error instead of silently falling back.
No configuration is automatically written, and installation does not modify your existing `config.yaml`.
The template lives at [src/van_rally/config.example.yaml](src/van_rally/config.example.yaml).
To customize, edit your existing file or save the following as a separate YAML file:

```yaml
api:
  base_url: "https://booking.roadsurfer.com/api"
  endpoints:
    stations: "/rally/stations"
    timeframes: "/rally/timeframes"
maps:
  directions_url: "https://www.google.com/maps/dir"
language_map:
  en: "en-GB"
  es: "es-ES"
```

The selected CLI language determines the API language. Keep all the sections shown above.

Responses for station details and transfer dates are cached for 24 hours under
`~/.van-rally/cache/` (your user home directory on all platforms).
The initial station list is fetched fresh. The cache can be removed to refresh results;
the old checkout-local `.cache/` is no longer used. Nothing is written inside the installed package.

## Update

With your environment activated and your local changes saved:

```sh
git pull --ff-only
python -m pip install .
```

For an editable development installation, use `python -m pip install -e ".[dev]"` instead.
Reinstall after dependency or package metadata changes; normal source edits are immediately visible in editable mode.

To deliberately upgrade dependencies, run `python -m pip install --upgrade --upgrade-strategy eager .`
(or `python -m pip install --upgrade --upgrade-strategy eager -e ".[dev]"` for development),
then run the checks below. Without `eager`, pip normally keeps dependencies that already satisfy the requirements.
Plain pip installs are **not exact, locked environments**; compatible dependency versions can change over time.

When switching from an older Python version, create a fresh environment rather than reusing it.
For example, on macOS/Linux, leave the old environment with `deactivate` if active, then:

```sh
mv .venv .venv-backup-old
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
```

Choose an unused backup name. On PowerShell, use `Rename-Item .venv .venv-backup-old`,
then repeat the Windows installation steps.
Backups named `.venv-backup-*/` are ignored too. A renamed environment is only a backup;
restore its original path if you need to use it again.
Keep your configuration files; never move them into the virtual environment.

## Development

Create/activate `.venv` as above, then:

```sh
python -m pip install -e ".[dev]"
python -m pytest --cov=van_rally --cov-report=term-missing --cov-fail-under=80
python -m ruff check .
python -m ruff format --check .
python -m build
```

`python -m ruff format .` applies formatting. `python -m build` creates a source distribution
and builds the wheel from it, checking that the source archive contains the required files.
Source lives in `src/van_rally/`; install the package before importing or testing it.

CI lints and builds on Python 3.14, then tests the actual wheel on Linux, macOS, and Windows.
It checks the runtime-only install before adding development tools, exercises both CLI entry points
outside the checkout, and verifies bundled English/Spanish translations and configuration.
Tests use mocked API responses and temporary caches, not live Roadsurfer requests or your personal cache.

See [tests/README.md](tests/README.md) for test and clean-install checks.

## Notes

Use responsibly: fetching all routes makes more requests than ordinary browsing.
Routes and dates generally do not change very often.

This software will be available until I receive a request from **Roadsurfer** to remove it.
There are also standard rates at [Roadsurfer.com](https://roadsurfer.com).
