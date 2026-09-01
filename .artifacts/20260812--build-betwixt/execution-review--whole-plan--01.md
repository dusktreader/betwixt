# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan review stopped at the first failed documented variant command. The implementation is blocked until the
required Python 3.12 verification command completes successfully.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`


## Scope

**whole-plan** — Iteration 01


## Issue Summary

- **Critical**:    1
- **Significant**: 0
- **Trivial**:     0


## Verification Evidence

- `make qa/full` → passed on Python 3.14.4: 69 passed, 100% coverage across 640 measured statements; Ruff, typos, and
  ty passed.
- `uv lock --check` → passed.
- `uv build` → passed; built `dist/betwixt-0.1.0.tar.gz` and `dist/betwixt-0.1.0-py3-none-any.whl`. It emitted a warning
  that `uv_build` has no upper bound.
- `make docs/build` → passed; Zensical built the site and API page.
- `uv run ruff check src/betwixt tests src/betwixt_demo examples` → passed.
- `uv run ty check src/betwixt tests src/betwixt_demo examples` → passed.
- `uv run typos src/betwixt tests src/betwixt_demo docs/source` → passed.
- `git diff --check` → passed.
- The exact documented Python 3.12 base variant command failed after `uv sync` and before any examples or CLI smoke ran:

  ```text
  uv sync --locked --python 3.12 --all-groups --extra demo && uv run --python 3.12 pytest -m "not absent_extra" tests && uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py && uv run --python 3.12 betwixt-demo --non-interactive
  ```

  ```text
  platform linux -- Python 3.12.13, pytest-9.1.1
  collected 69 items / 2 deselected / 67 selected
  tests/unit/test_demo.py:46 test_run_demo_reports_captured_failure
  ModuleNotFoundError: No module named 'rich._emoji_codes'
  tests/unit/test_demo.py:32 test_run_demo_renders_explanation_source_and_output
  ModuleNotFoundError: No module named 'rich._emoji_codes'
  tests/unit/test_version.py:11 test_get_version_from_metadata
  importlib.metadata.PackageNotFoundError: No package metadata was found for betwixt
  3 failed, 64 passed, 2 deselected
  ModuleNotFoundError: No module named 'rich._emoji_codes'
  ```

  The command therefore exits nonzero through pytest's final reporting path. The remaining exact matrix commands were
  not
  run, as required by the review procedure after a quality-check failure.


## Acceptance Criteria Verification

The mandatory stop occurred before independent AC verification. The statuses below are deferred, not approvals based on
the executor's journal claims.

| AC      | Status | Evidence                                       |
| ------- | ------ | ---------------------------------------------- |
| 01/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 01/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 01/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 01/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 01/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 02/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 02/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 02/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 02/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 03/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 03/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 03/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 03/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 03/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 04/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 04/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 04/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 04/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 04/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 04/AC06 | ⚠      | Deferred after the Python 3.12 quality failure |
| 05/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 05/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 05/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 05/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 06/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 06/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 06/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 06/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 06/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 06/AC06 | ⚠      | Deferred after the Python 3.12 quality failure |
| 07/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 07/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 07/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 07/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 08/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 08/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 08/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 08/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 08/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 09/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 09/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 09/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 09/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 09/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 10/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 10/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 10/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 10/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 10/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 11/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 11/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 11/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 11/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |
| 11/AC05 | ⚠      | Deferred after the Python 3.12 quality failure |
| 12/AC01 | ⚠      | Deferred after the Python 3.12 quality failure |
| 12/AC02 | ⚠      | Deferred after the Python 3.12 quality failure |
| 12/AC03 | ⚠      | Deferred after the Python 3.12 quality failure |
| 12/AC04 | ⚠      | Deferred after the Python 3.12 quality failure |


## Scope Verification

The file-by-file scope review was deferred by the mandatory stop. The inventory below records the paths named by the
journal; `⚠` means no independent scope judgment was made.

| File                                                           | Justified By                 | Status |
| -------------------------------------------------------------- | ---------------------------- | ------ |
| `src/betwixt/__init__.py`                                      | Tasks 01, 03, and 04         | ⚠      |
| `src/betwixt/betwixt.py`                                       | Tasks 01, 03, 04, 05, and 06 | ⚠      |
| `src/betwixt/errors.py`                                        | Tasks 01 and 06              | ⚠      |
| `src/betwixt/types.py`                                         | Task 01                      | ⚠      |
| `src/betwixt/refs.py`                                          | Task 01                      | ⚠      |
| `src/betwixt/declaration.py`                                   | Task 01                      | ⚠      |
| `src/betwixt/adapters/__init__.py`                             | Task 01                      | ⚠      |
| `src/betwixt/adapters/base.py`                                 | Task 01                      | ⚠      |
| `src/betwixt/adapters/dataclass.py`                            | Tasks 01 and 02              | ⚠      |
| `src/betwixt/adapters/registry.py`                             | Task 01                      | ⚠      |
| `src/betwixt/annotations.py`                                   | Task 02                      | ⚠      |
| `src/betwixt/constructs.py`                                    | Task 03                      | ⚠      |
| `src/betwixt/compiler.py`                                      | Tasks 03 and 04              | ⚠      |
| `src/betwixt/engine.py`                                        | Task 04                      | ⚠      |
| `src/betwixt/nested.py`                                        | Task 05                      | ⚠      |
| `src/betwixt/partial.py`                                       | Task 06                      | ⚠      |
| `src/betwixt/adapters/pydantic.py`                             | Task 07                      | ⚠      |
| `src/betwixt/adapters/sqlalchemy.py`                           | Task 08                      | ⚠      |
| `src/betwixt/version.py`                                       | Journal continuation changes | ⚠      |
| `examples/fixtures.py`                                         | Task 09                      | ⚠      |
| `examples/user.py`                                             | Task 09                      | ⚠      |
| `examples/payment.py`                                          | Task 09                      | ⚠      |
| `examples/order.py`                                            | Task 09                      | ⚠      |
| `examples/pydantic_user.py`                                    | Task 09                      | ⚠      |
| `examples/sqlalchemy_order.py`                                 | Task 09                      | ⚠      |
| `examples/sqlalchemy_user.py`                                  | Task 09                      | ⚠      |
| `src/betwixt_demo/features/__init__.py`                        | Task 09                      | ⚠      |
| `src/betwixt_demo/features/user.py`                            | Task 09                      | ⚠      |
| `src/betwixt_demo/features/payment.py`                         | Task 09                      | ⚠      |
| `src/betwixt_demo/features/order.py`                           | Task 09                      | ⚠      |
| `src/betwixt_demo/example_loader.py`                           | Task 09                      | ⚠      |
| `src/betwixt_demo/main.py`                                     | Task 09                      | ⚠      |
| `src/betwixt_demo/helpers.py`                                  | Journal continuation changes | ⚠      |
| `examples/README.md`                                           | Task 09                      | ⚠      |
| `tests/integration/test_examples.py`                           | Task 09                      | ⚠      |
| `tests/integration/test_no_extras.py`                          | Task 07                      | ⚠      |
| `tests/integration/test_docs.py`                               | Task 10                      | ⚠      |
| `tests/integration/test_project_config.py`                     | Task 10                      | ⚠      |
| `tests/integration/conftest.py`                                | Journal continuation changes | ⚠      |
| `tests/integration/steps/main_steps.py`                        | Journal continuation changes | ⚠      |
| `tests/unit/test_demo.py`                                      | Task 09                      | ⚠      |
| `tests/unit/test_main.py`                                      | Journal continuation changes | ⚠      |
| `tests/unit/test_betwixt_core.py`                              | Tasks 01-06 continuation     | ⚠      |
| `tests/unit/test_core_contract.py`                             | Tasks 01-06 continuation     | ⚠      |
| `tests/unit/test_core_coverage.py`                             | Tasks 01-06 continuation     | ⚠      |
| `tests/unit/test_tasks_01_06_exhaustive.py`                    | Tasks 01-06 continuation     | ⚠      |
| `tests/optional/test_pydantic_adapter.py`                      | Task 07                      | ⚠      |
| `tests/optional/test_sqlalchemy_adapter.py`                    | Task 08                      | ⚠      |
| `zensical.toml`                                                | Task 10                      | ⚠      |
| `docs/source/index.md`                                         | Task 10                      | ⚠      |
| `docs/source/quickstart.md`                                    | Task 10                      | ⚠      |
| `docs/source/why-betwixt.md`                                   | Task 10                      | ⚠      |
| `docs/source/concepts.md`                                      | Task 10                      | ⚠      |
| `docs/source/behavior.md`                                      | Task 10                      | ⚠      |
| `docs/source/cases/user.md`                                    | Task 10                      | ⚠      |
| `docs/source/cases/payment.md`                                 | Task 10                      | ⚠      |
| `docs/source/cases/order.md`                                   | Task 10                      | ⚠      |
| `docs/source/integrations.md`                                  | Task 10                      | ⚠      |
| `docs/source/comparison.md`                                    | Task 10                      | ⚠      |
| `docs/source/limits.md`                                        | Task 10                      | ⚠      |
| `docs/source/api-reference.md`                                 | Task 10                      | ⚠      |
| `docs/source/delivery.md`                                      | Tasks 10 and 11              | ⚠      |
| `docs/source/reference.md`                                     | Task 10                      | ⚠      |
| `docs/mkdocs.yaml`                                             | Task 10 deletion             | ⚠      |
| `Makefile`                                                     | Tasks 10 and 11              | ⚠      |
| `pyproject.toml`                                               | Tasks 07, 08, and 11         | ⚠      |
| `uv.lock`                                                      | Tasks 07, 08, and 11         | ⚠      |
| `README.md`                                                    | Task 11 continuation changes | ⚠      |
| `CONTRIBUTING.md`                                              | Task 11 continuation changes | ⚠      |
| `.github/workflows/quality.yml`                                | Task 11                      | ⚠      |
| `.github/workflows/release-verification.yml`                   | Task 11                      | ⚠      |
| `.github/workflows/main.yml`                                   | Task 11                      | ⚠      |
| `.github/workflows/deploy.yml`                                 | Task 11                      | ⚠      |
| `.github/workflows/docs.yml`                                   | Task 11                      | ⚠      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md` | Task 12                      | ⚠      |


## Findings

### Summary

| Finding | Title                                             | Outcome |
| ------- | ------------------------------------------------- | ------- |
| C01     | Exact Python 3.12 base verification command fails |         |


### Critical

#### C01: Exact Python 3.12 base verification command fails


#### Where

`tests/unit/test_demo.py:32,46`, `src/betwixt_demo/helpers.py:297`, and `tests/unit/test_version.py:11` under the exact
command specified by the implementation plan at `implementation-plan.md:85-97`.


#### Issue

After a fresh locked Python 3.12 sync, the required base-variant command fails three selected tests. Rich cannot import
`rich._emoji_codes`, and the version test cannot find the `betwixt` distribution metadata. The command never reaches the
three base examples or the non-interactive CLI smoke.


#### Impact

The required cross-version acceptance matrix is not green. The executor's 69-test and 100%-coverage result on Python
3.14 does not establish that the documented Python 3.12 environment can run the package, demo, or examples. Release
readiness and the remaining matrix variants cannot be accepted while this required gate fails.


#### Fix

Make the exact locked Python 3.12 command pass from a clean environment, including complete Rich package contents and
discoverable `betwixt` metadata. Then rerun all twelve exact matrix commands, the no-extras boundary, and the complete
quality gate.


#### Outcome


----

## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

C01 must be resolved before the whole-plan review can continue. Quality checks failing. Fix before review.
