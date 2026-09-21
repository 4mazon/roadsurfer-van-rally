"""Protect the status-check names used by GitHub's branch protection."""

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
REQUIRED_CHECKS = {
    "required-lint": ("Ruff Lint", ["build"]),
    "required-tests": ("Run Tests", ["build", "tests"]),
    "required-coverage": ("Coverage (fail if < 80%)", ["build", "tests"]),
}


@pytest.fixture
def workflow() -> dict:
    """Read the workflow without YAML 1.1 converting the on key to a boolean."""
    return yaml.load(WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_required_check_contract(workflow: dict) -> None:
    """Keep required names and real upstream dependencies stable."""
    assert "pull_request" in workflow["on"]
    for job_id, (name, dependencies) in REQUIRED_CHECKS.items():
        job = workflow["jobs"][job_id]
        assert job["name"] == name
        assert job["if"] == "${{ always() }}"
        needs = job["needs"]
        assert ([needs] if isinstance(needs, str) else needs) == dependencies
        assert "strategy" not in job  # Matrix suffixes would change the required name.
        assert "continue-on-error" not in job
        (step,) = job["steps"]
        assert "continue-on-error" not in step
        assert step["env"]["UPSTREAM_RESULTS"] == "${{ toJSON(needs) }}"
        assert step["shell"] == "python"

    build_steps = workflow["jobs"]["build"]["steps"]
    assert any("python -m ruff check ." in step.get("run", "") for step in build_steps)
    test_steps = workflow["jobs"]["tests"]["steps"]
    assert any("--cov-fail-under=80" in step.get("run", "") for step in test_steps)
    assert workflow["jobs"]["tests"]["strategy"]["matrix"]["os"] == [
        "ubuntu-latest",
        "macos-latest",
        "windows-latest",
    ]


@pytest.mark.parametrize("job_id", REQUIRED_CHECKS)
@pytest.mark.parametrize("status", ["success", "failure", "cancelled", "skipped"])
def test_required_checks_fail_closed(workflow: dict, job_id: str, status: str) -> None:
    """Execute each guard and reject any non-success result, including skipped jobs."""
    _, dependencies = REQUIRED_CHECKS[job_id]
    script = workflow["jobs"][job_id]["steps"][0]["run"]
    for dependency in dependencies:
        results = {name: {"result": "success"} for name in dependencies}
        results[dependency]["result"] = status
        result = subprocess.run(
            [sys.executable, "-c", script],
            env=os.environ | {"UPSTREAM_RESULTS": json.dumps(results)},
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        assert result.returncode == (0 if status == "success" else 1), result.stderr
