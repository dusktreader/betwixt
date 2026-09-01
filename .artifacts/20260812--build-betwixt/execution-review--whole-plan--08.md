# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review independently verifies the implementation after the prior review's temporary-filesystem
blocker was removed. It covers every plan and design acceptance criterion, all required quality gates, the complete
Python and dependency matrix, documentation, examples, and release boundaries.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--07.md`


## Scope

**whole-plan** - Iteration 08


## Issue Summary

- **Critical**:    0
- **Significant**: 0
- **Trivial**:     0


## Verification Evidence

- `make qa/full` -> passed; 100 tests passed, 100% coverage across 729 measured statements. Ruff, ty, and typos passed.
  An existing SQLite `ResourceWarning` was emitted and did not fail the gate.
- `make qa/test/no-extras` -> passed; 48 tests passed, 2 skipped, and 100% installed-package core coverage across 597
  statements. `.junit.xml` and `.coverage.xml` were generated. The two zero-statement compatibility modules emitted
  non-failing `module-not-imported` warnings.
- `uv lock --check` -> passed; 76 packages resolved.
- `uv build --clear` -> passed; exactly one wheel and one source distribution were produced. Independent metadata
  inspection confirmed Python `>=3.12,<3.15` and exactly `demo`, `pydantic`, and `sqlalchemy` extras in both artifacts.
- `make docs/build` -> passed; Zensical generated the site and API page.
- `make docs/serve` -> passed the startup probe; it served `docs/site` at `http://localhost:10000` and was deliberately
  terminated after eight seconds. The timeout's expected signal exit was not treated as a server failure.
- `tests/integration/test_package_install.py` -> passed; both wheel and source distribution installed and ran the full
  installed demo outside the checkout.
- `tests/integration/test_docs.py tests/integration/test_project_config.py` -> passed; 8 tests passed, including the
  generated API, semantic documentation, package metadata, no-extras recipe, artifact handoff, and workflow checks.
- All six example scripts, all-feature and named non-interactive demos passed. The invalid-feature demo returned the
  expected Typer exit code 2.
- All 16 executable Python documentation fences passed in isolated namespaces.
- Standalone Ruff, ty, and typos checks passed for the complete source, tests, demo, examples, and documentation scopes.
  The same three static gates also passed in each of the 12 matrix environments.
- YAML parsing -> passed for all 5 workflow files.
- `git diff --check` -> passed. Generated site, distributions, coverage, and JUnit outputs are not tracked.
- The uninspectable default-factory probe passed for both `TypeError` and `ValueError`: declaration raises
  `DeclarationError` and preserves the original exception as its cause.
- The independent py-buzz probe passed: `BetwixtError` inherits from `Buzz`, and `DeclarationError.require_condition`
  raises the expected owned error.
- All 12 exact plan command-table cells passed sequentially in separate worktree-local environments. Each cell ran its
  locked sync, complete `pytest -m "not absent_extra" tests` suite, required examples, and non-interactive CLI smoke:

  | Python | Base | Pydantic | SQLAlchemy | Combined |
  | ------ | ---- | -------- | ---------- | -------- |
  | 3.12  | 97 passed, 3 deselected, 100% | 97 passed, 3 deselected, 100% | 97 passed, 3 deselected, 100% | 97 passed, 3
  deselected, 100% |
  | 3.13  | 97 passed, 3 deselected, 100% | 97 passed, 3 deselected, 100% | 97 passed, 3 deselected, 100% | 97 passed, 3
  deselected, 100% |
  | 3.14  | 97 passed, 3 deselected, 100% | 97 passed, 3 deselected, 100% | 97 passed, 3 deselected, 100% | 97 passed, 3
  deselected, 100% |


## Acceptance Criteria Verification

### Implementation plan

#### Task 01

| AC      | Status | Evidence                                                                                                                                     |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | Public exports in `src/betwixt/__init__.py:1-19`; dependency-free import in `tests/integration/test_no_extras.py:13-16`.                     |
| 01/AC02 | ✓      | Exact, MRO, and built-in lookup in `src/betwixt/adapters/registry.py:22-33`; registry tests in `tests/unit/test_core_contract.py:47-60`.     |
| 01/AC03 | ✓      | Adapter and field snapshots in `src/betwixt/betwixt.py:95-102`; replacement test in `tests/unit/test_core_contract.py:63-116`.               |
| 01/AC04 | ✓      | Typed references and declaration checks in `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:63-79`; malformed-reference tests passed. |
| 01/AC05 | ✓      | Lazy optional lookup in `src/betwixt/adapters/base.py:9-32`; isolated missing-extra tests in `tests/integration/test_no_extras.py:20-74`.    |


#### Task 02

| AC      | Status | Evidence                                                                                                                                           |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 02/AC01 | ✓      | Normalization and forward-reference handling in `src/betwixt/annotations.py:11-32`; tests in `tests/unit/test_core_coverage.py:97-109`.            |
| 02/AC02 | ✓      | Recursive compatibility and tuple rules in `src/betwixt/annotations.py:34-78`; grammar tests in `tests/unit/test_tasks_01_06_exhaustive.py:48-61`. |
| 02/AC03 | ✓      | Unsupported nested grammar rejects in `src/betwixt/annotations.py:81-132`; unsupported-shape tests passed.                                         |
| 02/AC04 | ✓      | Native dataclass reads, requiredness, and construction in `src/betwixt/adapters/dataclass.py:20-49`; adapter boundary tests passed.                |


#### Task 03

| AC      | Status | Evidence                                                                                                                                                       |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 03/AC01 | ✓      | Directional callable requirements in `src/betwixt/betwixt.py:296-313`; independent pairwise behavior in `tests/unit/test_core_contract.py:132-144`.            |
| 03/AC02 | ✓      | The 15 approved factories are defined in `src/betwixt/constructs.py:28-107`; forbidden pairwise aliases are absent and API generation passed.                  |
| 03/AC03 | ✓      | Implicit precedence and controls in `src/betwixt/betwixt.py:118-132`; overlap and suppression tests passed.                                                    |
| 03/AC04 | ✓      | Declaration-only reports in `src/betwixt/betwixt.py:250-286`; status and omission tests passed.                                                                |
| 03/AC05 | ✓      | Callable, factory, reference, and anchor validation in `src/betwixt/compiler.py:22-62` and `src/betwixt/betwixt.py:63-93`; uninspectable-factory probe passed. |


#### Task 04

| AC      | Status | Evidence                                                                                                                                    |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 04/AC01 | ✓      | Keyword-only operations and `ctx` injection in `src/betwixt/betwixt.py:234-248` and `src/betwixt/compiler.py:22-70`; callable tests passed. |
| 04/AC02 | ✓      | Ordered maps, reductions, and projections in `src/betwixt/betwixt.py:133-175`; Pydantic, SQLAlchemy, and dataclass projection tests passed. |
| 04/AC03 | ✓      | Ordered writes and projection overlap in `src/betwixt/betwixt.py:133-175`; overlap assertions passed.                                       |
| 04/AC04 | ✓      | Literal, factory, and required defaults in `src/betwixt/betwixt.py:176-189`; default and partial tests passed.                              |
| 04/AC05 | ✓      | Structured unmapped errors in `src/betwixt/betwixt.py:192-215` and `src/betwixt/errors.py:22-47`; diagnostics tests passed.                 |
| 04/AC06 | ✓      | Full public operation, construct, report, adapter, and error exports in `src/betwixt/__init__.py:1-19`; API assertions passed.              |


#### Task 05

| AC      | Status | Evidence                                                                                                                          |
| ------- | ------ | --------------------------------------------------------------------------------------------------------------------------------- |
| 05/AC01 | ✓      | Nested shape traversal in `src/betwixt/betwixt.py:322-358`; scalar, optional, list, tuple, dictionary, and set tests passed.      |
| 05/AC02 | ✓      | One derivation per nested invocation in `src/betwixt/betwixt.py:152-171`; call-count and context tests passed in both directions. |
| 05/AC03 | ✓      | Declaration-time nested validation in `src/betwixt/betwixt.py:81-93`; malformed-shape and callable tests passed.                  |
| 05/AC04 | ✓      | Empty-container and native set behavior in `src/betwixt/betwixt.py:339-358`; edge tests passed.                                   |


#### Task 06

| AC      | Status | Evidence                                                                                                                                             |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 06/AC01 | ✓      | Mapping-only and unknown-key checks in `src/betwixt/betwixt.py:104-115`; partial input tests passed.                                                 |
| 06/AC02 | ✓      | Partial implicit seeding in `src/betwixt/betwixt.py:118-132`; incomplete and complete producer tests passed.                                         |
| 06/AC03 | ✓      | Reduction completeness and projection/default skips in `src/betwixt/betwixt.py:133-150,176-191`; sparse tests passed.                                |
| 06/AC04 | ✓      | Recursive partial validation and path wrapping in `src/betwixt/betwixt.py:322-365`; shape and path tests passed.                                     |
| 06/AC05 | ✓      | Partial methods return before construction at `src/betwixt/betwixt.py:190-191`; dictionary return tests passed.                                      |
| 06/AC06 | ✓      | Direct and derived context behavior in both directions is covered by `tests/unit/test_tasks_01_06_exhaustive.py:114-151` and optional adapter tests. |


#### Task 07

| AC      | Status | Evidence                                                                                                                                  |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| 07/AC01 | ✓      | Optional metadata and development dependencies in `pyproject.toml:21-57`; absent-extra tests passed.                                      |
| 07/AC02 | ✓      | Canonical Pydantic fields and native construction in `src/betwixt/adapters/pydantic.py:22-59`; alias, coercion, and reverse tests passed. |
| 07/AC03 | ✓      | Alias rejection and canonical construction in `src/betwixt/adapters/pydantic.py:41-55`; alias matrix tests passed.                        |
| 07/AC04 | ✓      | Pydantic full/partial, alias, ClassVar, projection, and native-validation coverage in `tests/optional/test_pydantic_adapter.py:24-199`.   |


#### Task 08

| AC      | Status | Evidence                                                                                                                                                                     |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 08/AC01 | ✓      | Mapper field discovery and canonical names in `src/betwixt/adapters/sqlalchemy.py:26-36`; `tests/optional/test_sqlalchemy_adapter.py:49-59`.                                 |
| 08/AC02 | ✓      | `Mapped[T]` normalization and mapper-only fields in `src/betwixt/adapters/sqlalchemy.py:26-36`; normalization tests passed.                                                  |
| 08/AC03 | ✓      | Unloaded checks in `src/betwixt/adapters/sqlalchemy.py:38-42`; loader-proof, detached, and raise-on-lazy tests passed at `tests/optional/test_sqlalchemy_adapter.py:90-170`. |
| 08/AC04 | ✓      | Native ORM construction and requiredness in `src/betwixt/adapters/sqlalchemy.py:60-75`; constructibility tests passed.                                                       |
| 08/AC05 | ✓      | SQLAlchemy scalar, relationship, reverse, canonical-name, precedence, and absent-extra tests passed in `tests/optional/test_sqlalchemy_adapter.py:49-317`.                   |


#### Task 09

| AC      | Status | Evidence                                                                                                                                                                           |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 09/AC01 | ✓      | Deterministic base examples in `examples/user.py:9-15`, `payment.py:9-11`, and `order.py:9-15`; direct and integration smokes passed.                                              |
| 09/AC02 | ✓      | Optional examples in `examples/pydantic_user.py:28-47`, `sqlalchemy_order.py:33-50`, and `sqlalchemy_user.py:3-10`; no-persistence smokes passed.                                  |
| 09/AC03 | ✓      | Discoverable feature functions in `src/betwixt_demo/features/*.py:6-10` and Rich presentation in `src/betwixt_demo/helpers.py:62-314`; demo tests passed.                          |
| 09/AC04 | ✓      | Feature selection and non-interactive failure handling in `src/betwixt_demo/main.py:22-40`; checkout and installed smokes preserved context, nesting, and patches.                 |
| 09/AC05 | ✓      | Deterministic output, discovery, failures, invalid selection, all/named selection, and package smoke passed in `tests/integration/test_examples.py` and `tests/unit/test_demo.py`. |


#### Task 10

| AC      | Status | Evidence                                                                                                                                                                                                               |
| ------- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 10/AC01 | ✓      | Zensical and active mkdocstrings configuration in `zensical.toml:1-33` and `docs/source/api-reference.md:8-28`; generated API assertions passed.                                                                       |
| 10/AC02 | ✓      | Exact navigation in `zensical.toml:7-19`; navigation and page assertions passed.                                                                                                                                       |
| 10/AC03 | ✓      | Complete taxonomy, context, ordering, nested behavior, cases, and 16 executable documentation fences passed semantic assertions.                                                                                       |
| 10/AC04 | ✓      | Partial semantics, diagnostics, canonical ORM names, loaded relationships, unsupported descriptors, persistence boundaries, and variant commands are documented and tested in `tests/integration/test_docs.py:72-128`. |
| 10/AC05 | ✓      | `Makefile:57-61`, `make docs/build`, `make docs/serve`, generated API checks, and documentation integration tests passed.                                                                                              |


#### Task 11

| AC      | Status | Evidence                                                                                                                                                                                        |
| ------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 11/AC01 | ✓      | Metadata, extras, development dependencies, bounded backend, and 100% threshold in `pyproject.toml:11-12,21-57,96-101`.                                                                         |
| 11/AC02 | ✓      | Three-by-four matrix, variant commands, reports, and retention in `.github/workflows/quality.yml:12-63`; all 12 cells passed independently.                                                     |
| 11/AC03 | ✓      | Authoritative no-extras recipe in `Makefile:25-36`, workflow boundary in `.github/workflows/quality.yml:65-85`, package/docs jobs in `quality.yml:87-124`, and configuration assertions passed. |
| 11/AC04 | ✓      | Reusable outputs in `.github/workflows/release-verification.yml:3-68`; tag-only deployment, exact artifact handoff, and no rebuild in `.github/workflows/deploy.yml:4-50`.                      |
| 11/AC05 | ✓      | Closed-PR docs trigger, merge guard, merge-revision checkout, named gate, artifact download, and Pages environment in `.github/workflows/docs.yml:4-49`.                                        |


#### Task 12

| AC      | Status | Evidence                                                                                                                                                                              |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 12/AC01 | ✓      | All 12 exact variant cells passed sequentially at 100% measured-code coverage; no unjustified production `no cover` exclusions exist.                                                 |
| 12/AC02 | ✓      | All examples, CLI smokes, docs build, package build, lock check, Ruff, ty, and typos passed.                                                                                          |
| 12/AC03 | ✓      | Construct, direction, implicit-control, explanation, full/partial, snapshot, loaded-relationship, native-boundary, reverse, and projection tests passed; targeted probes also passed. |
| 12/AC04 | ✓      | `git diff --check` passed; final `git status` contains only the approved implementation and artifact paths, with generated outputs ignored.                                           |


### Design plan

| AC   | Status | Evidence                                                                                                                                                                                        |
| ---- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC01 | ✓      | Peer-type declaration and keyword-only full operations in `src/betwixt/betwixt.py:21-46,234-240`; dataclass translation passed.                                                                 |
| AC02 | ✓      | Full and partial public operations in `src/betwixt/betwixt.py:234-248`; full/partial tests passed.                                                                                              |
| AC03 | ✓      | All 15 factories in `src/betwixt/constructs.py:28-107`; forbidden aliases remain absent from exports and generated API.                                                                         |
| AC04 | ✓      | Typed field proxies and early declaration checks in `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:63-79`; malformed-reference tests passed.                                           |
| AC05 | ✓      | Callable ordering and context validation in `src/betwixt/compiler.py:22-70` and `src/betwixt/betwixt.py:217-232`; ordering tests passed.                                                        |
| AC06 | ✓      | Direct context and one-call-per-boundary derivation in `src/betwixt/betwixt.py:152-171`; both directions passed.                                                                                |
| AC07 | ✓      | Implicit compatibility, suppression, reports, and unmapped remedies in `src/betwixt/betwixt.py:118-132,250-286`; diagnostic tests passed.                                                       |
| AC08 | ✓      | Map/reduction availability and ordered writes in `src/betwixt/betwixt.py:133-175`; full and partial matrices passed.                                                                            |
| AC09 | ✓      | Projection metadata and valid Pydantic, SQLAlchemy, ordinary dataclass, and slotted dataclass paths passed in adapter and full-translation tests.                                               |
| AC10 | ✓      | Literal, factory, and required defaults in `src/betwixt/betwixt.py:176-189`; default tests and uninspectable-factory probe passed.                                                              |
| AC11 | ✓      | Class-body order and later writes in `src/betwixt/betwixt.py:133-175`; overlap tests passed.                                                                                                    |
| AC12 | ✓      | Mapping-only partial boundary in `src/betwixt/betwixt.py:104-115`; malformed-input tests passed.                                                                                                |
| AC13 | ✓      | Sparse maps and recursive containers in `src/betwixt/betwixt.py:133-175,322-365`; path-aware tests passed.                                                                                      |
| AC14 | ✓      | Complete partial reductions use `source_adapter.construct` in `src/betwixt/betwixt.py:145-150`; availability tests passed.                                                                      |
| AC15 | ✓      | Partial projections are skipped in `src/betwixt/betwixt.py:138-143`; projection-skip tests passed.                                                                                              |
| AC16 | ✓      | Partial operations return before defaults in `src/betwixt/betwixt.py:176-191`; omission tests passed.                                                                                           |
| AC17 | ✓      | Compatibility grammar in `src/betwixt/annotations.py:34-78`; recursive type matrix passed.                                                                                                      |
| AC18 | ✓      | Nested grammar and tuple/container rules in `src/betwixt/annotations.py:81-125`; shape tests passed.                                                                                            |
| AC19 | ✓      | Exact/MRO/built-in lookup and snapshots in `src/betwixt/adapters/registry.py:22-33` and `src/betwixt/betwixt.py:55-62`; registry tests passed.                                                  |
| AC20 | ✓      | Native dataclass construction and slotted projection in `src/betwixt/adapters/dataclass.py:29-45`; ordinary and slotted projection tests passed.                                                |
| AC21 | ✓      | Pydantic extras, canonical fields, aliases, coercion, defaults, ClassVar exclusion, reverse mapping, projections, and native validation passed.                                                 |
| AC22 | ✓      | SQLAlchemy mapper discovery, canonical names, loaded state, native construction, reverse mapping, dynamic projection rejection, and no-persistence boundaries passed.                           |
| AC23 | ✓      | Owned declaration, adapter, partial, unloaded, missing-default, and unmapped errors pass; native callable and construction exceptions remain unwrapped.                                         |
| AC24 | ✓      | No serialization, schema, source-validation, or persistence layer was added; boundaries are documented in `docs/source/integrations.md:3-5,31-32`.                                              |
| AC25 | ✓      | Phase 1 declarations, dataclass mapping, diagnostics, and local Make quality gates pass.                                                                                                        |
| AC26 | ✓      | Phase 2 reductions, projections, defaults, nesting, partials, grammar, tuple rules, dictionary keys, set behavior, and required defaults pass.                                                  |
| AC27 | ✓      | Optional extras, isolated boundary, canonical adapters, both-direction mappings, nested relationships, and examples pass.                                                                       |
| AC28 | ✓      | Zensical configuration, generated API, coherent cases, runnable examples, adapter boundaries, and variant commands pass.                                                                        |
| AC29 | ✓      | Checkout and installed demos preserve User, Payment, and Order output, context, nested values, and sparse patches for wheel and sdist.                                                          |
| AC30 | ✓      | CI matrix, reports, retention, package/site gates, reusable release workflow, tag-only package deployment, merged-PR docs deployment, and 100% thresholds pass static and runtime verification. |


## Scope Verification

Every path listed in the journal's task entries was directly inspected. All implementation paths are justified by the
corresponding task; the review artifact is the only file added by this review. Generated `docs/site`, `dist`, coverage,
JUnit, and isolated review environments are not implementation scope.

| File path                                                      | Justification                                      | Status |
| -------------------------------------------------------------- | -------------------------------------------------- | ------ |
| `src/betwixt/__init__.py`                                      | Tasks 01, 03, and 04 public exports                | ✓      |
| `src/betwixt/betwixt.py`                                       | Tasks 01, 03-06 declaration and translation engine | ✓      |
| `src/betwixt/errors.py`                                        | Tasks 01 and 06 owned error contracts              | ✓      |
| `src/betwixt/types.py`                                         | Task 01 adapter protocol                           | ✓      |
| `src/betwixt/refs.py`                                          | Task 01 typed references                           | ✓      |
| `src/betwixt/declaration.py`                                   | Task 01 declaration surface                        | ✓      |
| `src/betwixt/annotations.py`                                   | Task 02 annotation grammar                         | ✓      |
| `src/betwixt/adapters/__init__.py`                             | Tasks 01-02 adapter exports                        | ✓      |
| `src/betwixt/adapters/base.py`                                 | Tasks 01, 07, and 08 optional lookup               | ✓      |
| `src/betwixt/adapters/dataclass.py`                            | Tasks 01-02 dataclass boundary                     | ✓      |
| `src/betwixt/adapters/registry.py`                             | Task 01 registry and precedence                    | ✓      |
| `src/betwixt/adapters/pydantic.py`                             | Task 07 native Pydantic adapter                    | ✓      |
| `src/betwixt/adapters/sqlalchemy.py`                           | Task 08 native SQLAlchemy adapter                  | ✓      |
| `src/betwixt/constructs.py`                                    | Task 03 construct factories                        | ✓      |
| `src/betwixt/compiler.py`                                      | Tasks 03-04 callable compilation and validation    | ✓      |
| `src/betwixt/engine.py`                                        | Task 04 engine compatibility surface               | ✓      |
| `src/betwixt/explain.py`                                       | Task 03 explanation compatibility surface          | ✓      |
| `src/betwixt/nested.py`                                        | Task 05 nested compatibility surface               | ✓      |
| `src/betwixt/partial.py`                                       | Task 06 partial compatibility surface              | ✓      |
| `src/betwixt/version.py`                                       | Tasks 09-11 package version behavior               | ✓      |
| `src/betwixt_demo/helpers.py`                                  | Task 09 Rich capture and presentation              | ✓      |
| `src/betwixt_demo/main.py`                                     | Task 09 Typer feature selection                    | ✓      |
| `src/betwixt_demo/example_loader.py`                           | Task 09 checkout/installed example loading         | ✓      |
| `src/betwixt_demo/features/__init__.py`                        | Task 09 feature package                            | ✓      |
| `src/betwixt_demo/features/user.py`                            | Task 09 User feature                               | ✓      |
| `src/betwixt_demo/features/payment.py`                         | Task 09 Payment feature                            | ✓      |
| `src/betwixt_demo/features/order.py`                           | Task 09 Order feature                              | ✓      |
| `src/betwixt_demo/runtime_examples/__init__.py`                | Task 09 bundled runtime examples                   | ✓      |
| `src/betwixt_demo/runtime_examples/pydantic_user.py`           | Task 09 installed User example                     | ✓      |
| `src/betwixt_demo/runtime_examples/payment.py`                 | Task 09 installed Payment example                  | ✓      |
| `src/betwixt_demo/runtime_examples/order.py`                   | Task 09 installed Order example                    | ✓      |
| `examples/__init__.py`                                         | Task 09 example package                            | ✓      |
| `examples/fixtures.py`                                         | Task 09 shared deterministic fixtures              | ✓      |
| `examples/user.py`                                             | Task 09 User example                               | ✓      |
| `examples/payment.py`                                          | Task 09 Payment example                            | ✓      |
| `examples/order.py`                                            | Task 09 Order example                              | ✓      |
| `examples/pydantic_user.py`                                    | Task 09 Pydantic example                           | ✓      |
| `examples/sqlalchemy_order.py`                                 | Task 09 SQLAlchemy example                         | ✓      |
| `examples/sqlalchemy_user.py`                                  | Task 09 combined example                           | ✓      |
| `examples/README.md`                                           | Tasks 09 and 11 variant instructions               | ✓      |
| `tests/conftest.py`                                            | Task 01 test collection boundary                   | ✓      |
| `tests/integration/conftest.py`                                | Task 07 no-extras BDD fallback                     | ✓      |
| `tests/integration/steps/main_steps.py`                        | Task 09 integration demo coverage                  | ✓      |
| `tests/integration/test_docs.py`                               | Tasks 10-12 docs and API gates                     | ✓      |
| `tests/integration/test_examples.py`                           | Tasks 09 and 12 example gates                      | ✓      |
| `tests/integration/test_no_extras.py`                          | Tasks 01, 07, and 11 no-extras boundary            | ✓      |
| `tests/integration/test_package_install.py`                    | Tasks 09 and 12 artifact smoke                     | ✓      |
| `tests/integration/test_project_config.py`                     | Tasks 07 and 11 configuration gates                | ✓      |
| `tests/optional/test_pydantic_adapter.py`                      | Task 07 Pydantic matrix                            | ✓      |
| `tests/optional/test_sqlalchemy_adapter.py`                    | Task 08 SQLAlchemy matrix                          | ✓      |
| `tests/unit/__init__.py`                                       | Task 01 unit-test package                          | ✓      |
| `tests/unit/conftest.py`                                       | Task 01 unit-test fixtures                         | ✓      |
| `tests/unit/test_betwixt_core.py`                              | Tasks 01-06 core behavior                          | ✓      |
| `tests/unit/test_core_contract.py`                             | Tasks 01-06 contracts and projections              | ✓      |
| `tests/unit/test_core_coverage.py`                             | Tasks 01-08 reachability and coverage              | ✓      |
| `tests/unit/test_demo.py`                                      | Task 09 demo behavior                              | ✓      |
| `tests/unit/test_main.py`                                      | Task 09 existing CLI coverage                      | ✓      |
| `tests/unit/test_tasks_01_06_exhaustive.py`                    | Tasks 01-06 exhaustive matrix                      | ✓      |
| `tests/unit/test_version.py`                                   | Task 09 version coverage                           | ✓      |
| `zensical.toml`                                                | Task 10 authoritative documentation configuration  | ✓      |
| `docs/mkdocs.yaml`                                             | Task 10 MkDocs removal                             | ✓      |
| `docs/source/index.md`                                         | Task 10 home page                                  | ✓      |
| `docs/source/quickstart.md`                                    | Task 10 quickstart                                 | ✓      |
| `docs/source/reference.md`                                     | Task 10 reference transition                       | ✓      |
| `docs/source/features.md`                                      | Task 10 documentation inventory                    | ✓      |
| `docs/source/concepts.md`                                      | Task 10 construct and context narrative            | ✓      |
| `docs/source/behavior.md`                                      | Task 10 full/partial behavior narrative            | ✓      |
| `docs/source/why-betwixt.md`                                   | Task 10 design narrative                           | ✓      |
| `docs/source/cases/user.md`                                    | Task 10 User case                                  | ✓      |
| `docs/source/cases/payment.md`                                 | Task 10 Payment case                               | ✓      |
| `docs/source/cases/order.md`                                   | Task 10 Order case                                 | ✓      |
| `docs/source/integrations.md`                                  | Task 10 adapter boundary narrative                 | ✓      |
| `docs/source/comparison.md`                                    | Task 10 design comparison                          | ✓      |
| `docs/source/limits.md`                                        | Task 10 limits                                     | ✓      |
| `docs/source/api-reference.md`                                 | Task 10 generated API entry point                  | ✓      |
| `docs/source/delivery.md`                                      | Tasks 10-11 delivery narrative                     | ✓      |
| `pyproject.toml`                                               | Tasks 07, 08, and 11 metadata and gates            | ✓      |
| `uv.lock`                                                      | Tasks 07, 08, and 11 locked dependencies           | ✓      |
| `Makefile`                                                     | Tasks 09-11 QA, docs, and build commands           | ✓      |
| `README.md`                                                    | Tasks 09-11 project documentation                  | ✓      |
| `CONTRIBUTING.md`                                              | Tasks 10-11 contributor documentation              | ✓      |
| `.github/workflows/main.yml`                                   | Task 11 QA workflow caller                         | ✓      |
| `.github/workflows/quality.yml`                                | Tasks 11-12 matrix and artifact gates              | ✓      |
| `.github/workflows/release-verification.yml`                   | Task 11 reusable release gate                      | ✓      |
| `.github/workflows/deploy.yml`                                 | Task 11 tag-only package deployment                | ✓      |
| `.github/workflows/docs.yml`                                   | Task 11 merged-PR docs deployment                  | ✓      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md` | Task 12 execution record                           | ✓      |


## Prior Review Resolution

- **C07** ✓ Fully resolved. With the cleaned environment, `/tmp` had 1,037,707 free inodes before verification. The
  exact
  3.13 SQLAlchemy command from `implementation-plan.md:879`, followed by the remaining matrix cells, completed without
  filesystem errors. All 12 cells passed with their required tests, examples, and CLI smoke, so the prior environmental
  blocker no longer applies.


## Findings

### Summary

No new findings.

| Finding | Title       | Outcome |
| ------- | ----------- | ------- |
| —       | No findings |         |


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**APPROVED**

All requested quality gates passed, all 12 variant cells passed in isolated environments, C07 is resolved, and every
implementation-plan and design-plan acceptance criterion is satisfied. No production code, plan, journal, or prior
review was modified.
