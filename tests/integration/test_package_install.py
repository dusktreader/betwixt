"""Verify release artifacts from outside the checkout."""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


@pytest.mark.integration
def test_wheel_and_sdist_install_and_run_demo_outside_checkout(tmp_path: Path) -> None:
    """Install each artifact into an isolated environment and invoke the advertised script."""
    dist = tmp_path / "dist"
    subprocess.run(
        ["uv", "build", "--clear", "--out-dir", str(dist)], cwd=ROOT, check=True, capture_output=True, text=True
    )
    artifacts = sorted(path for path in dist.iterdir() if path.suffix in {".whl", ".gz"})
    for artifact in artifacts:
        environment = tmp_path / artifact.stem
        subprocess.run(
            ["uv", "venv", "--python", sys.executable, str(environment)], check=True, capture_output=True, text=True
        )
        python = environment / "bin" / "python"
        subprocess.run(
            ["uv", "pip", "install", "--python", str(python), f"{artifact}[demo,pydantic,sqlalchemy]"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        completed = subprocess.run(
            [str(environment / "bin" / "betwixt-demo"), "--non-interactive"],
            cwd=tmp_path,
            check=True,
            capture_output=True,
            text=True,
        )
        output = completed.stdout
        assert "PersonView(name='Ada', age=36)" in output
        assert "map_rightward" in output
        assert "reduce_rightward" in output
        assert "project_rightward" in output
        assert "map_leftward" in output
        assert "right=(R.first_name, R.last_name)" in output
        assert "PydanticTwixt" in output
        assert "RowTwixt" in output
        assert "AccountTwixt" in output
        assert "email_address" in output
        assert "amount_cents" in output
        assert "displayName" in output
        assert "balanceDollars" in output
