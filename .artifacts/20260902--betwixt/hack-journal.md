# Hack journal

This journal records the bounded documentation deployment and branding update.


## Files changed

- `.github/workflows/docs.yml`
- `README.md`
- `docs/source/index.md`
- `tests/integration/test_project_config.py`
- `.artifacts/20260902--betwixt/hack-journal.md`

The user-provided `docs/source/static/logo.png` and `logo.svg` files were preserved unchanged.


## Intent

Remove the protected `github-pages` environment from the `peaceiris/actions-gh-pages` deployment while retaining the
documentation gate, artifact handoff, and main-branch-only deployment condition. Add the logo to the project and
documentation landing pages.


## Verification

- Synced locked dependencies with `uv sync --locked --python 3.14 --all-groups`.
- Passed `uv run --no-sync --python 3.14 pytest -o addopts="" tests/integration/test_project_config.py
  tests/integration/test_docs.py` with 8 tests.
- Built the site with `uv run --no-sync --python 3.14 zensical build --config-file docs/zensical.toml --clean`.
- Confirmed the generated index references `static/logo.png` and the asset is copied to `docs/site/static/`.
- Ran the Markdown formatter on `README.md` and `docs/source/index.md`; `docs/source/index.md` formatted cleanly, while
  the README formatter reported pre-existing badge, line-length, and heading-structure violations.
- Passed `git diff --check` and inspected the final diff and working-tree status.
