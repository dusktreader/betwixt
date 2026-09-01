# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review checks the corrective changes against the implementation plan, prior findings, executable
quality gates, adapter matrices, documentation, package artifacts, and delivery workflows.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--02.md`


## Scope

**whole-plan** - Iteration 03


## Issue Summary

- **Critical**:    4
- **Significant**: 1
- **Trivial**:     0


## Verification Evidence

- `UV_PROJECT_ENVIRONMENT=/tmp/opencode/betwixt-review-03-314 uv sync --locked --python 3.14 --all-groups --extra demo`
  -> passed; 76 locked packages installed.
- `UV_PROJECT_ENVIRONMENT=/tmp/opencode/betwixt-review-03-314 make qa/full` -> passed; 83 tests passed, 100% coverage
  across 686 measured statements, Ruff passed, ty passed, and typos passed.
- The complete test run included `tests/integration/test_package_install.py`, which built both wheel and sdist,
  installed
  each into an isolated environment outside the checkout, and ran the installed `betwixt-demo` command successfully.
- The complete test run included `tests/integration/test_docs.py`, which built the Zensical site and checked all 15
  construct names and their signature parameters in the generated API page.
- The exact no-extras command documented in `implementation-plan.md:104-113` -> **failed**. It collected 43 tests, had
  38 passed and 2 skipped, failed 4 tests against a stale cached installed package, and then failed its coverage gate.
  The relevant complete failure output was:

  ```text
  FAILED tests/unit/test_core_contract.py::test_annotations_cover_forward_optional_generics_and_any
  FAILED tests/unit/test_tasks_01_06_exhaustive.py::test_annotation_grammar_and_normalization
  FAILED tests/unit/test_tasks_01_06_exhaustive.py::test_snapshot_is_immutable_after_declaration
  FAILED tests/unit/test_tasks_01_06_exhaustive.py::test_global_suppression_and_unmapped_diagnostics_are_actionable

  E       assert not True
  E        +  where True = compatible(tuple[int, ...], tuple[int, int])
  E       Failed: DID NOT RAISE <class 'TypeError'>
  E       AttributeError: 'UnmappedFieldError' object has no attribute 'direction'

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
  ========================= 4 failed, 38 passed, 2 skipped in 0.27s =========================
  ```

- Per the review procedure, verification stopped after the documented quality gate failed. The twelve matrix command
  cells, standalone `make qa/test/no-extras`, standalone `uv build`, `make docs/serve`, `uv lock --check`, workflow YAML
  parsing, and `git diff --check` were not rerun after that failure. The package and documentation checks above did run
  inside `make qa/full`.


## Acceptance Criteria Verification

Only criteria whose status changed or whose prior finding remains open are listed. Unchanged criteria retain the prior
review's status.

| AC      | Status | Evidence                                                                                                                                                                                                         |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 02/AC02 | ✓      | `src/betwixt/annotations.py:44-73`; `tests/unit/test_tasks_01_06_exhaustive.py::test_annotation_grammar_and_normalization`                                                                                       |
| 03/AC01 | ✓      | `src/betwixt/betwixt.py:152-171`; `tests/unit/test_tasks_01_06_exhaustive.py::test_subclass_compatibility_and_nested_callable_contract`                                                                          |
| 03/AC04 | ✓      | `src/betwixt/betwixt.py:276-285`; `tests/unit/test_tasks_01_06_exhaustive.py::test_global_suppression_and_unmapped_diagnostics_are_actionable`                                                                   |
| 04/AC05 | ✓      | `src/betwixt/betwixt.py:192-214`, `src/betwixt/errors.py:25-47`; diagnostic assertions in the same test above                                                                                                    |
| 05/AC01 | ✓      | `src/betwixt/annotations.py:104-125`; tuple and container assertions in `test_annotation_grammar_and_normalization`                                                                                              |
| 06/AC01 | ✓      | `src/betwixt/betwixt.py:322-365`; `tests/unit/test_tasks_01_06_exhaustive.py::test_nested_partial_shapes_and_partial_explicit_seed`                                                                              |
| 06/AC02 | ✓      | `src/betwixt/betwixt.py:128-132`; seed-retention assertions at `tests/unit/test_tasks_01_06_exhaustive.py:432-440`                                                                                               |
| 06/AC04 | ✓      | `src/betwixt/betwixt.py:339-358`; malformed shape and empty-container assertions at `tests/unit/test_tasks_01_06_exhaustive.py:414-430`                                                                          |
| 07/AC03 | ✓      | `src/betwixt/adapters/pydantic.py:28-42`; alias-choice and alias-only tests at `tests/optional/test_pydantic_adapter.py:51-73`                                                                                   |
| 07/AC04 | ✓      | `tests/optional/test_pydantic_adapter.py:76-129`; native validation, alias, partial, default, and coercion cases                                                                                                 |
| 08/AC03 | ✓      | `src/betwixt/adapters/sqlalchemy.py:38-42`; loader-proof full, partial, detached, and raise-on-lazy tests at `tests/optional/test_sqlalchemy_adapter.py:66-140`                                                  |
| 08/AC05 | ✓      | `tests/optional/test_sqlalchemy_adapter.py:162-245`; nested relationship and requiredness cases                                                                                                                  |
| 09/AC02 | ✓      | `examples/sqlalchemy_order.py:30-50`; deterministic adapter translation assertion at `tests/integration/test_examples.py:27-35`                                                                                  |
| 10/AC01 | ✓      | `docs/source/api-reference.md:8-28`; generated API assertions at `tests/integration/test_docs.py:18-27`                                                                                                          |
| 10/AC03 | ⚠      | Fences no longer use the prior undefined names, but `docs/source/cases/payment.md:14-20` calls a leftward partial path that `examples/fixtures.py:105-124` does not declare and therefore returns an empty patch |
| 10/AC04 | ⚠      | Boundary prose exists in `docs/source/behavior.md:15-32` and `docs/source/integrations.md:14-32`, but the Payment example does not demonstrate the claimed reverse-direction behavior                            |
| 11/AC03 | ⚠      | `quality.yml:58-76` runs a corrected substitute, while the canonical plan command still fails and the substitute selects named tests rather than `tests/unit`                                                    |
| 11/AC05 | ✗      | `docs.yml:11-42` has one build-and-deploy job; it neither depends on a named docs gate nor downloads the `betwixt-site` artifact from `quality.yml:98-111`                                                       |
| 12/AC03 | ⚠      | Behavioral tests now cover the corrective core and adapter paths, but no test changes the registry after an existing mapping is declared; see `tests/unit/test_tasks_01_06_exhaustive.py:370-375`                |


## Scope Verification

The journal's individual modified paths are grouped by the plan area they implement. No unrelated subsystem change was
found.

| Files                                                          | Justification                                                           | Status |
| -------------------------------------------------------------- | ----------------------------------------------------------------------- | ------ |
| `src/betwixt/**`                                               | Tasks 01-08 core, constructs, engine, partial operations, and adapters  | ✓      |
| `src/betwixt_demo/**`                                          | Task 09 demo loader, features, helpers, and CLI                         | ✓      |
| `examples/**`                                                  | Task 09 base and optional executable examples                           | ✓      |
| `tests/unit/**`                                                | Tasks 01-06 core and demo behavior tests                                | ✓      |
| `tests/optional/**`                                            | Tasks 07-08 native adapter matrices                                     | ✓      |
| `tests/integration/**`                                         | Tasks 09-12 examples, no-extras, package, docs, and configuration gates | ✓      |
| `zensical.toml`, `docs/source/**`, `docs/mkdocs.yaml`          | Task 10 Zensical site, content, and MkDocs removal                      | ✓      |
| `pyproject.toml`, `uv.lock`, `Makefile`                        | Tasks 07-08 and 10-11 dependencies, commands, and build gates           | ✓      |
| `README.md`, `CONTRIBUTING.md`, `examples/README.md`           | Tasks 09-11 project and example documentation                           | ✓      |
| `.github/workflows/**`                                         | Tasks 11-12 quality, release, and documentation delivery workflows      | ✓      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md` | Task 12 execution record                                                | ✓      |


## Prior Review Resolution

- **C01** ✗ Not resolved. The canonical no-extras command at `implementation-plan.md:104-113` failed with zero measured
  coverage and stale-package behavior failures. `Makefile:24-29` and `quality.yml:58-64` use a different wheel-based,
  named-test substitute.
- **C02** ✓ Fully resolved. `pyproject.toml:100-101` includes both `betwixt` and `betwixt_demo`,
  `src/betwixt_demo/example_loader.py:7-14` has an installed-package fallback, and the outside-checkout wheel/sdist test
  passes at `tests/integration/test_package_install.py:13-36`.
- **C03** ✓ Fully resolved. Plain-class subclass compatibility is handled at `src/betwixt/annotations.py:44-50` and
  exercised in both directions at `tests/unit/test_tasks_01_06_exhaustive.py:331-350`.
- **C04** ✓ Fully resolved. Nested results are passed through the declared directional callable at
  `src/betwixt/betwixt.py:166-171`; both directional wrappers change the result in
  `tests/unit/test_tasks_01_06_exhaustive.py:312-328`.
- **C05** ✓ Fully resolved. `_nested()` retains and validates the outer shape at `src/betwixt/betwixt.py:322-365`, with
  wrong-shape, path, tuple-arity, and empty-container tests at `tests/unit/test_tasks_01_06_exhaustive.py:378-430`.
- **C06** ✓ Fully resolved. Partial implicit fields are seeded before explicit producers at
  `src/betwixt/betwixt.py:128-132`; incomplete and complete producer cases are asserted at
  `tests/unit/test_tasks_01_06_exhaustive.py:432-440`.
- **C07** ✓ Fully resolved. Fixed and variadic tuple shapes are rejected when they differ at
  `src/betwixt/annotations.py:104-116`, with both mismatch directions tested at
  `tests/unit/test_core_coverage.py:155-156`.
- **C08** ✓ Fully resolved. Global suppression has its own explanation branch at `src/betwixt/betwixt.py:276-279`, and
  the reason is asserted at `tests/unit/test_tasks_01_06_exhaustive.py:443-453`.
- **C09** ✓ Fully resolved. The error now carries structured details in `src/betwixt/errors.py:25-47` and builds a
  complete message from the explanation at `src/betwixt/betwixt.py:192-214`; the full contract is asserted at
  `tests/unit/test_tasks_01_06_exhaustive.py:454-470`.
- **C10** ⚠ Partially resolved. The old undefined names and fixture mismatches are rejected by the documentation smoke
  at
  `tests/integration/test_docs.py:53-57`, but the Payment snippet at `docs/source/cases/payment.md:14-20` claims a
  reverse
  partial translation that the fixture does not implement. The full narrative remains unreliable.
- **C11** ✓ Fully resolved. `examples/sqlalchemy_order.py:30-50` constructs a Betwixt mapping and asserts translated
  canonical fields; `tests/integration/test_examples.py:27-35` checks deterministic output.
- **C12** ⚠ Partially resolved. The corrective behavior matrices are present and the normal suite reaches 100% measured
  coverage, but the required post-declaration registry mutation is absent from the snapshot test at
  `tests/unit/test_tasks_01_06_exhaustive.py:370-375`; the registry test at `tests/unit/test_core_contract.py:44-58`
  only checks lookup precedence.
- **C13** ✗ Not resolved. `docs.yml:11-42` still builds and publishes directly in one job. It does not consume the
  `betwixt-site` artifact or depend on a separately named docs gate.
- **S01** ✓ Fully resolved. `_validation_alias_accepts_name()` recognizes canonical `AliasChoices` at
  `src/betwixt/adapters/pydantic.py:48-50`, with accepting and rejecting choice matrices at
  `tests/optional/test_pydantic_adapter.py:51-73`.
- **S02** ✓ Fully resolved. `api-reference.md:10-28` lists all 15 factories and the documentation test checks every
  exported factory and signature parameter at `tests/integration/test_docs.py:21-27`.
- **S03** ✗ Not resolved. `pyproject.toml:96-98` still declares `uv-build>=0.1.0` without an upper bound.
- **S04** ✓ Fully resolved for the tested matrix. Pydantic native errors, aliases, partial keys, defaults, and coercion
  are covered at `tests/optional/test_pydantic_adapter.py:51-129`; SQLAlchemy loaded/unloaded, detached, raise-on-lazy,
  nested relationship, requiredness, and canonical-name cases are covered at
  `tests/optional/test_sqlalchemy_adapter.py:47-245`.


## Findings

### Summary

| Finding | Title                                                                          | Outcome |
| ------- | ------------------------------------------------------------------------------ | ------- |
| C01     | Canonical no-extras quality command still fails and diverges from the workflow |         |
| C10     | Documentation still claims an unimplemented reverse Payment translation        |         |
| C12     | Registry snapshot immutability remains untested                                |         |
| C13     | Documentation deployment still bypasses the named site artifact and gate       |         |
| S03     | Release builds still leave `uv-build` unbounded                                |         |


### Critical

#### C01: Canonical no-extras quality command still fails and diverges from the workflow


#### Where

`implementation-plan.md:99-113`, `Makefile:24-29`, and `.github/workflows/quality.yml:58-76`


#### Issue

The plan's authoritative command still measures `src/betwixt/...` names after installing the package, so coverage sees
no
matching imported modules. The current run also reused an old cached installed package, exposing stale behavior
failures.
The workflow invokes a different command, selects six named unit files rather than the plan's complete `tests/unit`
selection, and does not make the two recipes reproducibly equivalent.


#### Impact

The documented no-extras release gate is not executable. A clean checkout cannot reproduce the passing workflow gate
from
the plan, and the failed run proves the required quality command does not establish the 100% boundary evidence.


#### Fix

Choose one authoritative recipe, update both the plan and workflow to use it, force the local package build to refresh,
and
preserve the complete core test set plus both report uploads. Run that exact recipe in a clean isolated environment.


#### Outcome


----

#### C10: Documentation still claims an unimplemented reverse Payment translation


#### Where

`docs/source/cases/payment.md:14-20` and `examples/fixtures.py:105-124`


#### Issue

The documented snippet calls `mapping.leftward_partial({"dollars": 12.10}, ...)` and describes an asymmetric reverse
direction, but `payment_mapping()` declares only `map_rightward` and `reduce_rightward`. The leftward partial operation
therefore has no producer for `cents` and returns `{}`. The snippet has no assertion that would expose the
contradiction,
and the documentation smoke checks text rather than snippet behavior.


#### Impact

The site still presents a non-working case as executable guidance and does not deliver the approved coherent Payment
narrative. Readers cannot use the documented reverse operation to produce a patch.


#### Fix

Either add and test the intended leftward declaration in the shared fixture, or change the snippet and prose to show
only
the implemented direction. Add an integration check that executes the documented Payment snippet and asserts its patch.


#### Outcome


----

#### C12: Registry snapshot immutability remains untested


#### Where

`tests/unit/test_tasks_01_06_exhaustive.py:370-375` and `tests/unit/test_core_contract.py:44-58`


#### Issue

The snapshot test proves only that the field mapping proxy rejects direct mutation. It never registers or replaces an
adapter after an existing `Betwixt` declaration, and the registry test covers precedence only. The plan requires later
registry changes to affect new declarations without mutating existing ones.


#### Impact

The normal 100% line result can pass while the adapter-snapshot contract regresses. Existing mappings could silently
change
behavior after process-local registration changes without a test detecting it.


#### Fix

Declare a mapping, replace or register an adapter for one side, and assert the existing mapping retains the original
adapter
while a new mapping sees the replacement. Cover both registry directions or document the exact boundary.


#### Outcome


----

#### C13: Documentation deployment still bypasses the named site artifact and gate


#### Where

`.github/workflows/quality.yml:98-111` and `.github/workflows/docs.yml:11-42`


#### Issue

`quality.yml` uploads `betwixt-site`, but `docs.yml` has a single `docs` job that rebuilds `docs/site` and publishes
that
directory directly. There is no named docs verification gate, `needs` dependency, artifact download, or assertion that
deployment uses the quality-gated site output.


#### Impact

Branch protection cannot address a distinct documentation gate, and the published site is not the artifact produced by
the
named CI docs build. A deployment can succeed even when the quality workflow's site artifact is unavailable or
different.


#### Fix

Create a named docs verification job that builds, validates, and uploads `betwixt-site`. Make the guarded deployment job
depend on that job and download only its artifact, retaining the merged-main checkout, exact event guards, and
`github-pages` environment.


#### Outcome


### Significant

#### S03: Release builds still leave `uv-build` unbounded


#### Where

`pyproject.toml:96-98`


#### Issue

The build-system requirement remains `uv-build>=0.1.0` with no tested upper bound. The current source still has the
release
reproducibility warning identified in the prior review.


#### Impact

A future breaking build-backend release can change or break wheel and source-distribution generation while the project
metadata and lockfile appear unchanged.


#### Fix

Pin `uv-build` to a tested compatible upper bound, regenerate `uv.lock`, and keep the outside-checkout wheel and sdist
installation smoke in the release gate.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED - CHANGES REQUIRED**

C01, C10, C12, C13, and S03 must be resolved before approval. The documented no-extras quality check failed, so the
review is blocked regardless of the passing normal quality suite.
