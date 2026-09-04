# Documentation CI gate fix

This hack simplifies the documentation workflow after the dedicated integration test was deleted.


## Intent

Let `uv run` install or reuse the project dependencies for the documentation build, so the workflow does not need a
separate dependency synchronization step.


## Changes

- Updated `.github/workflows/docs.yml` to run `make docs/build` instead of the deleted
  `tests/integration/test_docs.py`.
- Updated `Makefile` so `UV_RUN` uses `uv run` without `--no-sync`.
- Removed the redundant `uv sync` step from `.github/workflows/docs.yml`.


## Verification

- Ran `make docs/build` locally.
- Confirmed the documentation build completed successfully and generated `docs/site`.
