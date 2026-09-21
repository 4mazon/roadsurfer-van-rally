"""Smoke-test a non-editable installation using only the standard library."""

import subprocess
import sys
import sysconfig
from importlib.metadata import version
from pathlib import Path
from tempfile import TemporaryDirectory

import van_rally


def main() -> None:
    """Check entry points, bundled resources, and configuration away from the source tree."""
    package_path = Path(van_rally.__file__).resolve()
    assert package_path.is_relative_to(Path(sys.prefix).resolve()), package_path
    executable = "van-rally.exe" if sys.platform == "win32" else "van-rally"
    cli = str(Path(sysconfig.get_path("scripts")) / executable)

    with TemporaryDirectory(prefix="van-rally-smoke-") as directory:
        for command in ([cli], [sys.executable, "-m", "van_rally"]):
            help_result = subprocess.run(
                [*command, "--help"],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=30,
            )
            assert "--config" in help_result.stdout
            version_result = subprocess.run(
                [*command, "--version"],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=30,
            )
            assert version_result.stdout.strip() == f"van-rally {version('van-rally')}"

        # Exercise the module CLI with real resources but a mocked API: no live requests.
        code = (
            "import runpy; from unittest.mock import patch; "
            "from van_rally.config_utils import get_config; "
            "assert get_config().url_stations == "
            "'https://booking.roadsurfer.com/api/en/rally/stations'; "
            "\nwith patch('van_rally.main.get_stations_data', return_value=[]):\n"
            "    runpy.run_module('van_rally', run_name='__main__')\n"
        )
        for language, expected in (
            ("en", "No stations with rally found."),
            ("es", "No se encontraron estaciones con rally."),
        ):
            result = subprocess.run(
                [sys.executable, "-c", code, "--language", language],
                cwd=directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
                timeout=30,
            )
            assert expected in result.stdout, result.stdout
            assert not result.stderr, result.stderr

        invalid = subprocess.run(
            [cli, "--config", "missing.yaml"],
            cwd=directory,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=30,
        )
        assert invalid.returncode == 2
        assert "Configuration error:" in invalid.stderr
        assert not list(Path(directory).iterdir()), (
            "CLI unexpectedly wrote into its working directory"
        )
    print("Installed-package smoke checks passed (English and Spanish, no live API requests).")


if __name__ == "__main__":
    main()
