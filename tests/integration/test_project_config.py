"""Integration assertions for packaging and delivery configuration."""

from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]


@pytest.mark.integration
def test_project_metadata_declares_supported_variants_and_gate() -> None:
    """Check the public package metadata without depending on a TOML library."""
    metadata = (ROOT / "pyproject.toml").read_text()
    assert 'requires-python = ">=3.12,<3.15"' in metadata
    assert '"pydantic>=2.7,<3"' in metadata
    assert '"SQLAlchemy>=2.0,<3"' in metadata
    assert '"zensical==0.0.13"' in metadata
    assert '"mkdocstrings[python]>=1.0,<1.1"' in metadata
    assert 'requires = ["uv-build>=0.12.6,<0.13"]' in metadata
    assert '"--cov-fail-under=100"' in metadata
    theme = (ROOT / "docs/zensical.toml").read_text()
    assert 'variant = "classic"' in theme
    assert 'extra_css = ["source/stylesheets/extra.css"]' in theme
    assert (ROOT / "docs/source/stylesheets/extra.css").is_file()


@pytest.mark.integration
def test_workflows_have_the_required_release_boundaries() -> None:
    """Check workflow triggers, matrix dimensions, reports, and artifact retention."""
    quality = (ROOT / ".github/workflows/quality.yml").read_text()
    assert "python: ['3.12', '3.13', '3.14']" in quality
    assert "variant: [base, pydantic, sqlalchemy, combined]" in quality
    assert quality.count('pytest -m "not absent_extra" tests') == 1
    assert "betwixt-demo --non-interactive" in quality
    assert "python examples/" not in quality
    assert quality.count("name: junit-${{ matrix.python }}-${{ matrix.variant }}") == 1
    assert quality.count("name: coverage-${{ matrix.python }}-${{ matrix.variant }}") == 1
    assert quality.count("retention-days: 14") >= 6
    assert "no-extras-boundary:" in quality
    assert "run: make qa/test/no-extras" in quality
    assert "package-build:" in quality and "docs-build:" in quality

    deploy = (ROOT / ".github/workflows/deploy.yml").read_text()
    assert "tags: ['v*.*.*']" in deploy
    assert "workflow_dispatch" not in deploy
    assert "needs: verification" in deploy
    assert "contents: read" in deploy
    assert "id-token: write" in deploy
    assert "actions/download-artifact@v4" in deploy
    assert "name: release-betwixt-wheel" in deploy and "name: release-betwixt-sdist" in deploy
    assert "uv build" not in deploy

    docs = (ROOT / ".github/workflows/docs.yml").read_text()
    assert "types: [closed]" in docs
    assert "docs/source/**" in docs and "docs/zensical.toml" in docs
    assert "github-pages" in docs
    assert "docs-gate:" in docs
    assert "needs: docs-gate" in docs
    assert "actions/download-artifact@v4" in docs
    assert "name: betwixt-site" in docs
    assert "merge_commit_sha" in docs
    assert "uses: ./.github/workflows/quality.yml" not in docs
    assert 'pytest -o addopts="" tests/integration/test_docs.py' in docs


@pytest.mark.integration
def test_no_extras_make_target_is_the_workflow_boundary_recipe() -> None:
    """Require Make and quality CI to use one fresh-wheel, complete-core recipe."""
    makefile = (ROOT / "Makefile").read_text()
    quality = (ROOT / ".github/workflows/quality.yml").read_text()

    assert "qa/test/no-extras:" in makefile
    assert 'uv build --clear --wheel --out-dir "$$wheel_dir"' in makefile
    assert "build_cache_dir=$$(mktemp -d)" in makefile
    assert 'UV_CACHE_DIR="$$build_cache_dir"' in makefile
    assert "env -u UV_PROJECT_ENVIRONMENT" in makefile
    assert "--no-cache --reinstall --no-deps" in makefile
    assert "tests/integration/test_no_extras.py tests/unit" in makefile
    assert "--cov=betwixt.annotations" in makefile
    assert "--cov-report=term-missing" in makefile
    assert "--cov-report=xml:.coverage.xml" in makefile
    assert "--cov-fail-under=100" in makefile
    assert "run: make qa/test/no-extras" in quality
    assert "uv build --clear --wheel" not in quality
    assert "publish:" not in makefile
    assert "git push" not in makefile


@pytest.mark.integration
def test_release_publishes_only_verified_distribution_artifacts() -> None:
    """Require release verification to hand its exact distributions to deployment."""
    release = (ROOT / ".github/workflows/release-verification.yml").read_text()
    deploy = (ROOT / ".github/workflows/deploy.yml").read_text()
    assert "demo:" in release
    assert "jobs.demo.result" in release
    assert "python examples/" not in release
    assert "outputs.examples" not in deploy
    assert "name: release-betwixt-wheel" in release
    assert "name: release-betwixt-sdist" in release
    assert "path: dist/*.whl" in release
    assert "path: dist/*.tar.gz" in release
    assert 'test "${#wheels[@]}" -eq 1' in release
    assert 'test "${#sdists[@]}" -eq 1' in release
    assert "if-no-files-found: error" in release
    assert "uv publish" in deploy
    assert "name: release-betwixt-wheel" in deploy
    assert "name: release-betwixt-sdist" in deploy
    assert 'test "${#wheels[@]}" -eq 1' in deploy
    assert 'test "${#sdists[@]}" -eq 1' in deploy
    assert "uv publish dist/*.whl dist/*.tar.gz" in deploy
