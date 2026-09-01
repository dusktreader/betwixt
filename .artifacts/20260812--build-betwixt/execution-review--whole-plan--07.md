# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review checks the current implementation and prior findings until the required Python 3.13
variant gate fails because the review environment exhausts `/tmp` space.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--06.md`


## Scope

**whole-plan** - Iteration 07


## Issue Summary

- **Critical**:    1
- **Significant**: 0
- **Trivial**:     0


## Verification Evidence

- `make qa/full` -> passed; 100 tests passed, 100% coverage across 729 measured statements. Ruff, ty, and typos
  passed. One existing SQLite `ResourceWarning` was emitted.
- `make qa/test/no-extras` -> passed; 48 tests passed, 2 skipped, and 100% installed-package core coverage across
  597 statements. The two compatibility modules emitted non-failing `module-not-imported` warnings. Both JUnit and
  XML coverage reports were written.
- `uv lock --check` -> passed; 76 packages resolved.
- `uv build --clear` -> passed; exactly one wheel and one source distribution were produced.
- `make docs/build` -> passed; Zensical generated the site and API page.
- `make docs/serve` -> started the server at `http://localhost:10000`; the process was deliberately terminated by an
  eight-second timeout and its resulting signal exit was treated as expected for this startup probe.
- `tests/integration/test_package_install.py` -> passed; both wheel and source distribution installed and ran the
  installed demo outside the checkout.
- `tests/integration/test_docs.py tests/integration/test_project_config.py` -> passed; 8 tests passed, including the
  generated API, semantic documentation, package metadata, no-extras recipe, artifact handoff, and workflow checks.
- All six example scripts, all-feature and named non-interactive demos passed. The invalid-feature demo returned the
  expected Typer exit code 2.
- `git diff --check` -> passed before the matrix run.
- The exact documented variant commands passed for 3.12/base, 3.12/pydantic, 3.12/sqlalchemy, 3.12/combined,
  3.13/base, and 3.13/pydantic. The 3.13/sqlalchemy command failed before completion because the local `/tmp`
  filesystem was out of space. Per the review procedure, verification stopped at that quality failure; 3.13/combined
  and all four 3.14 commands were not run.

The failing command was the documented 3.13 SQLAlchemy command from `implementation-plan.md:879`:

```text
uv sync --locked --python 3.13 --all-groups --extra demo --extra sqlalchemy && uv run --python 3.13 pytest -m "not absent_extra" tests && uv run --python 3.13 python examples/user.py && uv run --python 3.13 python examples/payment.py && uv run --python 3.13 python examples/order.py && uv run --python 3.13 python examples/sqlalchemy_order.py && uv run --python 3.13 betwixt-demo --non-interactive
```

The exact failure output included:

```text
FAILED tests/integration/test_package_install.py::test_wheel_and_sdist_install_and_run_demo_outside_checkout
subprocess.CalledProcessError: ... uv pip install ... returned non-zero exit status 2

FAILED tests/unit/test_demo.py::test_run_demo_reports_captured_failure
FAILED tests/unit/test_demo.py::test_run_demo_renders_explanation_source_and_output
E       OSError: [Errno 28] No space left on device: '/tmp/tmphxtmv1hm'
E       OSError: [Errno 28] No space left on device: '/tmp/tmpmwikb_kw'

======================== 3 failed, 94 passed, 3 deselected in 8.47s =========================
```

Standalone static-command reruns, YAML parsing, independent documentation-fence execution, and the remaining matrix
cells were not run after the mandatory stop.


## Acceptance Criteria Verification

Independent AC verification was stopped after C07. The rows below are explicitly deferred, not approvals based on the
executor's journal or the prior review.


### Implementation plan

| AC      | Status | Evidence                           |
| ------- | ------ | ---------------------------------- |
| 01/AC01 | ⚠      | Deferred after C07 quality failure |
| 01/AC02 | ⚠      | Deferred after C07 quality failure |
| 01/AC03 | ⚠      | Deferred after C07 quality failure |
| 01/AC04 | ⚠      | Deferred after C07 quality failure |
| 01/AC05 | ⚠      | Deferred after C07 quality failure |
| 02/AC01 | ⚠      | Deferred after C07 quality failure |
| 02/AC02 | ⚠      | Deferred after C07 quality failure |
| 02/AC03 | ⚠      | Deferred after C07 quality failure |
| 02/AC04 | ⚠      | Deferred after C07 quality failure |
| 03/AC01 | ⚠      | Deferred after C07 quality failure |
| 03/AC02 | ⚠      | Deferred after C07 quality failure |
| 03/AC03 | ⚠      | Deferred after C07 quality failure |
| 03/AC04 | ⚠      | Deferred after C07 quality failure |
| 03/AC05 | ⚠      | Deferred after C07 quality failure |
| 04/AC01 | ⚠      | Deferred after C07 quality failure |
| 04/AC02 | ⚠      | Deferred after C07 quality failure |
| 04/AC03 | ⚠      | Deferred after C07 quality failure |
| 04/AC04 | ⚠      | Deferred after C07 quality failure |
| 04/AC05 | ⚠      | Deferred after C07 quality failure |
| 04/AC06 | ⚠      | Deferred after C07 quality failure |
| 05/AC01 | ⚠      | Deferred after C07 quality failure |
| 05/AC02 | ⚠      | Deferred after C07 quality failure |
| 05/AC03 | ⚠      | Deferred after C07 quality failure |
| 05/AC04 | ⚠      | Deferred after C07 quality failure |
| 06/AC01 | ⚠      | Deferred after C07 quality failure |
| 06/AC02 | ⚠      | Deferred after C07 quality failure |
| 06/AC03 | ⚠      | Deferred after C07 quality failure |
| 06/AC04 | ⚠      | Deferred after C07 quality failure |
| 06/AC05 | ⚠      | Deferred after C07 quality failure |
| 06/AC06 | ⚠      | Deferred after C07 quality failure |
| 07/AC01 | ⚠      | Deferred after C07 quality failure |
| 07/AC02 | ⚠      | Deferred after C07 quality failure |
| 07/AC03 | ⚠      | Deferred after C07 quality failure |
| 07/AC04 | ⚠      | Deferred after C07 quality failure |
| 08/AC01 | ⚠      | Deferred after C07 quality failure |
| 08/AC02 | ⚠      | Deferred after C07 quality failure |
| 08/AC03 | ⚠      | Deferred after C07 quality failure |
| 08/AC04 | ⚠      | Deferred after C07 quality failure |
| 08/AC05 | ⚠      | Deferred after C07 quality failure |
| 09/AC01 | ⚠      | Deferred after C07 quality failure |
| 09/AC02 | ⚠      | Deferred after C07 quality failure |
| 09/AC03 | ⚠      | Deferred after C07 quality failure |
| 09/AC04 | ⚠      | Deferred after C07 quality failure |
| 09/AC05 | ⚠      | Deferred after C07 quality failure |
| 10/AC01 | ⚠      | Deferred after C07 quality failure |
| 10/AC02 | ⚠      | Deferred after C07 quality failure |
| 10/AC03 | ⚠      | Deferred after C07 quality failure |
| 10/AC04 | ⚠      | Deferred after C07 quality failure |
| 10/AC05 | ⚠      | Deferred after C07 quality failure |
| 11/AC01 | ⚠      | Deferred after C07 quality failure |
| 11/AC02 | ⚠      | Deferred after C07 quality failure |
| 11/AC03 | ⚠      | Deferred after C07 quality failure |
| 11/AC04 | ⚠      | Deferred after C07 quality failure |
| 11/AC05 | ⚠      | Deferred after C07 quality failure |
| 12/AC01 | ⚠      | Deferred after C07 quality failure |
| 12/AC02 | ⚠      | Deferred after C07 quality failure |
| 12/AC03 | ⚠      | Deferred after C07 quality failure |
| 12/AC04 | ⚠      | Deferred after C07 quality failure |


### Design plan

| AC   | Status | Evidence                           |
| ---- | ------ | ---------------------------------- |
| AC01 | ⚠      | Deferred after C07 quality failure |
| AC02 | ⚠      | Deferred after C07 quality failure |
| AC03 | ⚠      | Deferred after C07 quality failure |
| AC04 | ⚠      | Deferred after C07 quality failure |
| AC05 | ⚠      | Deferred after C07 quality failure |
| AC06 | ⚠      | Deferred after C07 quality failure |
| AC07 | ⚠      | Deferred after C07 quality failure |
| AC08 | ⚠      | Deferred after C07 quality failure |
| AC09 | ⚠      | Deferred after C07 quality failure |
| AC10 | ⚠      | Deferred after C07 quality failure |
| AC11 | ⚠      | Deferred after C07 quality failure |
| AC12 | ⚠      | Deferred after C07 quality failure |
| AC13 | ⚠      | Deferred after C07 quality failure |
| AC14 | ⚠      | Deferred after C07 quality failure |
| AC15 | ⚠      | Deferred after C07 quality failure |
| AC16 | ⚠      | Deferred after C07 quality failure |
| AC17 | ⚠      | Deferred after C07 quality failure |
| AC18 | ⚠      | Deferred after C07 quality failure |
| AC19 | ⚠      | Deferred after C07 quality failure |
| AC20 | ⚠      | Deferred after C07 quality failure |
| AC21 | ⚠      | Deferred after C07 quality failure |
| AC22 | ⚠      | Deferred after C07 quality failure |
| AC23 | ⚠      | Deferred after C07 quality failure |
| AC24 | ⚠      | Deferred after C07 quality failure |
| AC25 | ⚠      | Deferred after C07 quality failure |
| AC26 | ⚠      | Deferred after C07 quality failure |
| AC27 | ⚠      | Deferred after C07 quality failure |
| AC28 | ⚠      | Deferred after C07 quality failure |
| AC29 | ⚠      | Deferred after C07 quality failure |
| AC30 | ⚠      | Deferred after C07 quality failure |


## Scope Verification

Scope verification was stopped with the quality procedure. The journal inventory remains within the approved plan, but
the file-by-file status was not independently completed in this iteration.

| Files                                                          | Justification                                                                       | Status |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ------ |
| `src/betwixt/**`                                               | Tasks 01-08 core declarations, constructs, engine, partial operations, and adapters | ⚠      |
| `src/betwixt_demo/**`                                          | Task 09 demo loader, features, helpers, and CLI                                     | ⚠      |
| `examples/**`                                                  | Task 09 base and optional executable examples                                       | ⚠      |
| `tests/unit/**`                                                | Tasks 01-06 core and demo behavior tests                                            | ⚠      |
| `tests/optional/**`                                            | Tasks 07-08 native adapter matrices                                                 | ⚠      |
| `tests/integration/**`                                         | Tasks 09-12 examples, no-extras, package, docs, and configuration gates             | ⚠      |
| `zensical.toml`, `docs/source/**`, `docs/mkdocs.yaml`          | Task 10 Zensical site, content, and MkDocs removal                                  | ⚠      |
| `pyproject.toml`, `uv.lock`, `Makefile`                        | Tasks 07-11 dependencies, commands, and build gates                                 | ⚠      |
| `README.md`, `CONTRIBUTING.md`, `examples/README.md`           | Tasks 09-11 project and example documentation                                       | ⚠      |
| `.github/workflows/**`                                         | Tasks 11-12 quality, release, and documentation delivery workflows                  | ⚠      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md` | Task 12 execution record                                                            | ⚠      |


## Prior Review Resolution

- **C01** ✓ Fully resolved. The authoritative no-extras plan recipe at `implementation-plan.md:99-114`, Make target at
  `Makefile:25-36`, and workflow invocation at `quality.yml:65-85` align. `make qa/test/no-extras` passed with 100%
  installed-package core coverage.
- **C02** ✓ Fully resolved. `PydanticAdapter.fields()` uses `model_fields` at `src/betwixt/adapters/pydantic.py:22-24`,
  and the ClassVar regression passed at `tests/optional/test_pydantic_adapter.py:170-182`.
- **C03** ✓ Fully resolved. SQLAlchemy projection validation rejects public unknown attributes at
  `src/betwixt/adapters/sqlalchemy.py:48-54`; the regression passed at
  `tests/optional/test_sqlalchemy_adapter.py:79-87`.
- **C04** ✓ Fully resolved. Tag deployment declares `contents: read` alongside `id-token: write` at
  `.github/workflows/deploy.yml:17-19`.
- **C05** ✓ Fully resolved. Slotted dataclass projection uses declared-field reads without requiring `__dict__` at
  `src/betwixt/adapters/dataclass.py:29-41`; the slotted regression passed at
  `tests/unit/test_core_contract.py:229-240`.
- **C06** ✓ Fully resolved. `validate_factory()` translates both `TypeError` and `ValueError` inspection failures into
  `DeclarationError` with the original cause at `src/betwixt/compiler.py:35-50`; the regression passed at
  `tests/unit/test_core_coverage.py:230-237`.
- **S01** ✓ Fully resolved. Release verification uploads exactly one wheel and sdist under distinct names at
  `.github/workflows/release-verification.yml:40-68`; tag deployment downloads and publishes those files at
  `.github/workflows/deploy.yml:28-50` without rebuilding.
- **S02** ✓ Fully resolved. The Makefile has no public `publish` target or `git push` command at `Makefile:77-104`.
- **S03** ✓ Fully resolved. The complete taxonomy, context, nested behavior, corrected case narrative, and semantic
  assertions are present in `docs/source/concepts.md:52-96`, `docs/source/behavior.md:25-68`, and
  `tests/integration/test_docs.py:72-128`.
- **S04** ✓ Fully resolved for the executed boundary. Bundled runtime examples preserve User, Payment, and nested
  Order behavior at `src/betwixt_demo/runtime_examples/`; the outside-checkout wheel/sdist smoke passed at
  `tests/integration/test_package_install.py:13-46`.
- **S05** ✓ Fully resolved. The user-defined Pydantic detection path has no coverage exclusion at
  `src/betwixt/adapters/base.py:15-18`, and the normal and no-extras coverage gates passed.
- **S06** ✓ Fully resolved in the inspected test matrix. Pydantic reverse behavior is covered at
  `tests/optional/test_pydantic_adapter.py:36-52`, SQLAlchemy reverse behavior at
  `tests/optional/test_sqlalchemy_adapter.py:192-210`, and nested/control reverse behavior at
  `tests/unit/test_tasks_01_06_exhaustive.py:114-165`.
- **S07** ✓ Fully resolved. The optional import branches at `src/betwixt/adapters/pydantic.py:13-18` and
  `src/betwixt/adapters/sqlalchemy.py:13-18` have no coverage pragmas; missing-extra causes are asserted at
  `tests/unit/test_core_coverage.py:360-378`, and both coverage gates passed.


## Findings

### Summary

| Finding | Title                                                            | Outcome |
| ------- | ---------------------------------------------------------------- | ------- |
| C07     | Python 3.13 SQLAlchemy variant gate fails because `/tmp` is full |         |


### Critical

#### C07: Python 3.13 SQLAlchemy variant gate fails because `/tmp` is full


#### Where

The exact documented 3.13 SQLAlchemy command at `implementation-plan.md:879`, specifically
`tests/integration/test_package_install.py:13-28` and `tests/unit/test_demo.py:33-57`.


#### Issue

The required variant command could not complete in the current review environment. Its package-install smoke returned
exit status 2, and both demo presentation tests failed while `tempfile.TemporaryDirectory()` attempted to create a
directory. The observed error was `OSError: [Errno 28] No space left on device` under `/tmp`.


#### Impact

The documented quality command exits nonzero, so the 3.13 SQLAlchemy acceptance cell is not green. The remaining
3.13/combined and all 3.14 cells were not run, and this review cannot establish the complete 12-cell release matrix.
The failure is an environment-integrity blocker rather than evidence of a source defect, but the plan's required gate
still fails.


#### Fix

Provide a clean review environment with sufficient temporary filesystem space, rerun the exact 3.13 SQLAlchemy command,
then rerun the remaining matrix cells and all gates that were skipped after the mandatory stop. Preserve the current
source and do not treat the passing subset as approval.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

C07 must be cleared by a successful clean-environment rerun. The quality check failed, so this iteration cannot approve
the implementation.
