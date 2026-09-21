# Tests

Use Python 3.14 and an activated `.venv`; see the [installation instructions](../README.md).

```sh
python -m pip install -e ".[dev]"
python -m pytest
python -m pytest tests/test_api_utils.py
python -m pytest --cov=van_rally --cov-report=term-missing --cov-fail-under=80
python -m pytest --cov=van_rally --cov-report=html
python -m ruff check .
python -m ruff format --check .
```

The HTML coverage report is written to `htmlcov/index.html`.
All imports and mock targets use the `van_rally` package.

## Isolation

The automatic fixture in `conftest.py` resets configuration/translations, changes into a temporary
working directory, and redirects cache writes to a temporary directory. Tests never clear your
personal application cache or overwrite your configuration.

API tests mock network responses using the JSON files in `fixtures/`.
Configuration tests verify explicit-file precedence, local files, bundled defaults, and errors.
Translation tests cover English, Spanish, and fallback behavior.

## Installed-package smoke test

`smoke_installed.py` uses only the standard library plus the installed application.
Run it with a **non-editable** installation; it deliberately rejects imports from `src/`.

For example, on macOS/Linux, from the repository root with the development environment active:

```sh
python -m build
smoke_dir=$(mktemp -d)
python -m venv "$smoke_dir/venv"
"$smoke_dir/venv/bin/python" -m pip install dist/van_rally-0.1.0-py3-none-any.whl
"$smoke_dir/venv/bin/python" tests/smoke_installed.py
```

Use the wheel name produced by the build if the project version changes.
The smoke test launches `van-rally` and `python -m van_rally` in an empty temporary directory.
It checks help/version, bundled defaults, both languages with a mocked API, configuration errors,
and the absence of unexpected working-directory writes. No live API requests are made.

CI runs this check on Linux, macOS, and Windows before installing test tools via the wheel's
`[dev]` extra. It then runs the test suite against that same wheel, never replacing it with
an editable source install.
