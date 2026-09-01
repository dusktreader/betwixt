# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review checks prior finding resolution, current source semantics, package boundaries, documentation,
quality gates, and release workflows.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--03.md`


## Scope

**whole-plan** - Iteration 04


## Issue Summary

- **Critical**:    4
- **Significant**: 2
- **Trivial**:     0


## Verification Evidence

- `make qa/full` -> passed; 87 tests passed, 100% coverage across 686 measured statements, Ruff passed, ty passed, and
  typos passed. One existing SQLite resource warning was emitted.
- `make qa/test/no-extras` -> passed; 43 tests passed, 2 skipped, and 100% coverage across 580 installed-package core
  statements. `.junit.xml` and `.coverage.xml` were written. The two zero-statement compatibility modules emitted
  non-failing not-imported warnings.
- The exact no-extras command documented in `implementation-plan.md:104-105` -> **failed** after 43 tests passed and 2
  skipped. Its `src/betwixt/...` coverage selectors did not match the installed `betwixt...` modules:

  ```text
  WARNING: Module src/betwixt/annotations.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/adapters/base.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/adapters/dataclass.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/adapters/registry.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/betwixt.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/compiler.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/constructs.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/declaration.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/engine.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/errors.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/explain.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/nested.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/partial.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/refs.py was never imported. (module-not-imported)
  WARNING: Module src/betwixt/types.py was never imported. (module-not-imported)
  WARNING: Failed to generate report: No data to report.
  ERROR: Coverage failure: total of 0 is less than fail-under=100
  FAIL Required test coverage of 100% not reached. Total coverage: 0.00%
  ======================== 43 passed, 2 skipped in 0.30s =========================
  ```

- The current 12-cell CI matrix was rerun with separate environments: all 12 cells passed 85 tests, deselected the 2
  `absent_extra` tests, reached 100% coverage, ran their required examples, and completed the non-interactive CLI smoke.
  One initial concurrent attempt exhausted local `/tmp` inodes; the affected cells passed when rerun sequentially.
- `uv lock --check` -> passed.
- `uv build --clear` -> passed; one wheel and one source distribution were produced with the bounded `uv-build` backend
  requirement and no backend warning.
- `make docs/build` -> passed; Zensical generated `docs/site` and the API page. The generated API page contains all 15
  construct factories and their signature parameters, verified both by `tests/integration/test_docs.py` and direct HTML
  inspection.
- `make docs/serve` -> started Zensical at `http://localhost:10000`; a deliberate five-second timeout stopped it.
- Standalone Ruff, ty, and typos commands -> passed for the complete source, test, example, and documentation scopes.
- `git diff --check` -> passed.
- `tests/integration/test_package_install.py` -> passed for wheel and sdist installation outside the checkout. An
  additional outside-checkout smoke ran the full non-interactive demo from both artifacts successfully.
- All six example scripts passed. The all-feature and named non-interactive demos passed; the invalid feature exited 2
  with Typer's expected validation error. The focused core, optional-adapter, example, and documentation tests passed:
  47 tests passed.
- Python documentation fences executed successfully in their page namespaces. The Payment full reverse and reverse
  partial examples produced `Payment(1210)` and `{"cents": 1210}`.
- Workflow YAML parsing passed. The quality workflow contains a 3-by-4 matrix (12 combinations) and seven artifact
  upload steps; matrix and no-extras report uploads use 14-day retention and `if: ${{ !cancelled() }}`.
- `py-buzz` inspection confirmed `BetwixtError -> Buzz -> Exception`; inherited `require_condition()` produced a
  specialized `DeclarationError` with Buzz's normalized message behavior.


## Acceptance Criteria Verification

Only criteria whose status changed or whose prior finding remains open are listed. Unchanged criteria retain the prior
review's status.

| AC      | Status | Evidence                                                                                                                                                                                                   |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC03 | ✓      | Adapter snapshots are exercised in both directions by `tests/unit/test_core_contract.py::test_declared_mapping_keeps_adapters_after_registry_replacement` and `src/betwixt/betwixt.py:95-102`.             |
| 04/AC02 | ⚠      | Reductions and projections execute in `src/betwixt/betwixt.py:138-175`, but invalid and unknown projection results are not rejected at that boundary.                                                      |
| 07/AC02 | ⚠      | Native Pydantic construction works in `tests/optional/test_pydantic_adapter.py:22-129`, but `src/betwixt/adapters/pydantic.py:22-23` exposes `ClassVar` annotations as fields and later raises `KeyError`. |
| 10/AC03 | ✓      | All page fences execute; the shared Payment case is validated by `tests/integration/test_docs.py::test_payment_documentation_example_matches_the_implemented_reverse_path`.                                |
| 10/AC04 | ✓      | Boundary prose is present in `docs/source/behavior.md:15-32` and `docs/source/integrations.md:14-32`; Payment reverse behavior is executable and asserted.                                                 |
| 11/AC03 | ✗      | The Make recipe and `quality.yml:65-85` agree, but the authoritative command still documented at `implementation-plan.md:104-105` fails its 100% coverage gate.                                            |
| 11/AC04 | ⚠      | `release-verification.yml:3-13` exposes the four required outputs and `deploy.yml:4-14` is tag-only, but the deploy job's checkout permission and distribution handoff are incomplete.                     |
| 11/AC05 | ✓      | `docs.yml:12-30` builds and validates the merge revision, uploads `betwixt-site`, and `docs.yml:32-49` downloads that artifact after `needs: docs-gate` under `github-pages`.                              |
| 12/AC01 | ✓      | All 12 Python/variant cells passed with 100% measured-code coverage; the no-extras boundary also passed at 100%.                                                                                           |
| 12/AC02 | ✓      | The package, documentation, six examples, CLI paths, lint, type, typo, and outside-checkout artifact smokes passed.                                                                                        |
| 12/AC03 | ⚠      | The requested core, adapter, nested, partial, tuple, diagnostic, and registry behavior is exercised, but projection validation and the Pydantic `ClassVar` boundary are untested and incorrect.            |
| 12/AC04 | ✓      | `git diff --check` passed and no generated `docs/site` or `dist/` output is tracked.                                                                                                                       |


## Scope Verification

The journal's modified paths remain within the approved plan. No unrelated subsystem change was found.

| Files                                                          | Justification                                                                      | Status |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ------ |
| `src/betwixt/**`                                               | Tasks 01-08 core declarations, constructs, engine, nested operations, and adapters | ✓      |
| `src/betwixt_demo/**`                                          | Task 09 demo loader, features, helpers, and CLI                                    | ✓      |
| `examples/**`                                                  | Task 09 base and optional executable examples                                      | ✓      |
| `tests/unit/**`                                                | Tasks 01-06 core and demo behavior tests                                           | ✓      |
| `tests/optional/**`                                            | Tasks 07-08 native adapter matrices                                                | ✓      |
| `tests/integration/**`                                         | Tasks 09-12 examples, no-extras, package, docs, and configuration gates            | ✓      |
| `zensical.toml`, `docs/source/**`, `docs/mkdocs.yaml`          | Task 10 Zensical site, content, and MkDocs removal                                 | ✓      |
| `pyproject.toml`, `uv.lock`, `Makefile`                        | Tasks 07-08 and 10-11 dependencies, commands, and build gates                      | ✓      |
| `README.md`, `CONTRIBUTING.md`, `examples/README.md`           | Tasks 09-11 project and example documentation                                      | ✓      |
| `.github/workflows/**`                                         | Tasks 11-12 quality, release, and documentation delivery workflows                 | ✓      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md` | Task 12 execution record                                                           | ✓      |


## Prior Review Resolution

- **C01** ✗ Not resolved. The plan's canonical installed-package command at `implementation-plan.md:104-105` still
  selects `src/betwixt/...` coverage targets and fails with zero measured coverage. `Makefile:25-36` and
  `quality.yml:65-73` use a different module-name recipe.
- **C10** ✓ Fully resolved. `docs/source/cases/payment.md:15-28` now uses the declared reverse map, and
  `tests/integration/test_docs.py:61-68` executes both reverse operations and asserts the patch.
- **C12** ✓ Fully resolved. `tests/unit/test_core_contract.py:62-115` replaces both registered adapters after a mapping
  is declared and proves that the original and replacement mappings use their respective snapshots.
- **C13** ✓ Fully resolved. `docs.yml:12-30` is a named docs gate that uploads `betwixt-site`; `docs.yml:32-49` depends
  on it and deploys only the downloaded artifact.
- **S03** ✓ Fully resolved. `pyproject.toml:96-98` bounds `uv-build` to `>=0.12.6,<0.13`, and `uv build --clear`
  passed without the prior backend warning.


## Findings

### Summary

| Finding | Title                                                                           | Outcome |
| ------- | ------------------------------------------------------------------------------- | ------- |
| C01     | Canonical no-extras quality command still fails and diverges from the workflow  |         |
| C02     | Pydantic adapter exposes non-model annotations as fields                        |         |
| C03     | Projection results are not represented or validated                             |         |
| C04     | Tag deployment checkout lacks the declared contents permission                  |         |
| S01     | Release publishes a fresh rebuild instead of the verified distribution artifact |         |
| S02     | Makefile retains a manual package-release trigger                               |         |


### Critical

#### C01: Canonical no-extras quality command still fails and diverges from the workflow


#### Where

`implementation-plan.md:99-113`, `Makefile:5-36`, and `.github/workflows/quality.yml:65-85`


#### Issue

The implementation plan remains the authoritative command source, but its isolated command passes filesystem paths such
as
`src/betwixt/annotations.py` to coverage after installing the package. The installed modules are named
`betwixt.annotations`, so coverage collects no data and fails the 100% gate. The Makefile and workflow now use a fresh
wheel and importable module selectors instead, making the passing recipe different from the plan.


#### Impact

The documented no-extras gate is not executable. A clean checkout cannot reproduce the required plan command, and the
failed run does not establish the complete core report required for the release boundary.


#### Fix

Make one recipe authoritative by updating the plan to the fresh-wheel/module-selector command, or change the Makefile to
execute the plan's corrected form. Keep the complete `tests/integration/test_no_extras.py tests/unit` selection, all 15
dependency-free core modules, both XML reports, and `--cov-fail-under=100`.


#### Outcome


----

#### C02: Pydantic adapter exposes non-model annotations as fields


#### Where

`src/betwixt/adapters/pydantic.py:22-24` and `src/betwixt/adapters/pydantic.py:44-45`


#### Issue

`PydanticAdapter.fields()` returns every annotation from `resolved_fields()` rather than only the entries in
`BaseModel.model_fields`. A normal Pydantic `ClassVar` is therefore exposed as a Betwixt destination field, but
`required()` and `construct()` index it in `model_fields` and raise `KeyError`. An independent reproduction with
`kind: ClassVar[str]` printed `{'value': int, 'kind': ClassVar[str]}` and then failed with `KeyError 'kind'`.


#### Impact

Ordinary Pydantic models with class-level configuration or constants cannot be mapped reliably. The adapter crosses the
native Pydantic field boundary and emits an unowned failure instead of constructing or reporting a valid mapping.


#### Fix

Build the adapter field mapping from `model_fields` only, resolving annotations for those canonical names. Add a test
with
`ClassVar`, and cover other non-input annotations that Pydantic excludes from `model_fields`.


#### Outcome


----

#### C03: Projection results are not represented or validated


#### Where

`src/betwixt/betwixt.py:141-143`, `src/betwixt/betwixt.py:222-230`, and `src/betwixt/betwixt.py:267-285`


#### Issue

Projection producers use an empty destination name, so `_explain()` never reports a projection as an explicit producer.
For a mapping whose only declaration is `project_rightward`, `explain_rightward()` reports a compatible field as
`implicit` even though the projection supplies the value. Extraction also iterates only the final destination fields,
silently discarding extra projected attributes. If the projection returns a mapping or an object missing a destination
attribute, the code leaks a raw `AttributeError` rather than rejecting the invalid projection through the declared
adapter boundary. The current behavior was reproduced with a projection returning `{"value": 1}`: it raised
`AttributeError`, and a projection object with an extra field was silently reduced to the destination.


#### Impact

The explanation API lies about the active producer, and malformed projection output can be silently discarded or escape
as
an unowned exception. This violates the projection extraction and diagnostics contract in design AC09 and Task 04.


#### Fix

Retain projection metadata as an explicit producer, report its coverage in both explanation directions, and validate the
returned object and extracted fields through the destination adapter. Reject unknown or unreadable projected fields with
the specified Betwixt-owned declaration or adapter error, then add positive and negative tests.


#### Outcome


----

#### C04: Tag deployment checkout lacks the declared contents permission


#### Where

`.github/workflows/deploy.yml:12-22`


#### Issue

The package deployment job grants only `id-token: write` at job scope, then runs `actions/checkout@v4`. GitHub Actions
sets unspecified permissions to `none` when a permissions block is provided, so the checkout has no declared
`contents: read` permission. The verification job does not supply the deployment job's token permissions.


#### Impact

The automatic tag release can fail at its first checkout step after all reusable verification outputs succeed,
preventing
the package publication path from completing.


#### Fix

Grant `contents: read` alongside `id-token: write` for the deployment job, or remove the checkout and publish a verified
artifact supplied by the release gate. Add workflow validation that exercises the tag job's permission and checkout
path.


#### Outcome


### Significant

#### S01: Release publishes a fresh rebuild instead of the verified distribution artifact


#### Where

`.github/workflows/quality.yml:87-107`, `.github/workflows/release-verification.yml:40-48`, and
`.github/workflows/deploy.yml:27-35`


#### Issue

The quality workflow builds and uploads `betwixt-wheel` and `betwixt-sdist`. The reusable release workflow separately
builds distributions, but does not upload or expose them. The tag deploy job then runs `uv build` again and publishes
that
new output. No job verifies the exact files passed to `uv publish`.


#### Impact

The package published from a tag is not the package produced by the gated build. Backend, environment, or source changes
between jobs can make the published files differ from the artifacts whose success enabled deployment.


#### Fix

Build distributions once in the release gate, upload both files, and make the deployment job download and publish those
exact artifacts. Preserve the success outputs, tag-only trigger, and separate wheel/sdist artifact names.


#### Outcome


----

#### S02: Makefile retains a manual package-release trigger


#### Where

`Makefile:79-84`, `design-plan.md:602-608`, and `implementation-plan.md:743-746`


#### Issue

The public `make publish` target prompts an operator, creates a version tag, and pushes it to `origin`. The approved
delivery contract says package publication has no manual publication path and occurs automatically only from a validated
pushed version tag. The target remains advertised as a package publication command even though the workflow itself is
tag-only.


#### Impact

The repository exposes a second, operator-triggered release path that is not represented by the quality/release gate
contract. It can create a publication run without a documented release rehearsal or explicit human review of the tag
operation.


#### Fix

Remove the `publish` target and document the tag workflow as the sole release path, or rename and narrow any
tag-creation
helper so it does not claim to publish and is explicitly covered by the approved release procedure.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C04 and S01-S02 must be resolved before approval. The canonical documented no-extras quality command fails, so the
review is blocked even though the corrected Make recipe, normal quality gate, matrix, package smokes, documentation, and
static checks pass.
