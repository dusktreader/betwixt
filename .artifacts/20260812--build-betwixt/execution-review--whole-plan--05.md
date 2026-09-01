# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review verifies the prior findings, all design and implementation acceptance criteria, the complete
quality matrix, native adapter boundaries, documentation, examples, and release workflows.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--04.md`


## Scope

**whole-plan** - Iteration 05


## Issue Summary

- **Critical**:    2
- **Significant**: 4
- **Trivial**:     0


## Verification Evidence

- `make qa/full` -> passed; 92 tests passed, 100% coverage across 715 measured statements, Ruff, ty, and typos passed.
  One existing SQLite `ResourceWarning` was emitted.
- `make qa/test/no-extras` -> passed; 44 tests passed, 2 skipped, and 100% coverage across 591 installed-package core
  statements. Both `.junit.xml` and `.coverage.xml` were written. Coverage emitted non-failing not-imported warnings for
  `betwixt.nested` and `betwixt.partial`.
- The authoritative no-extras recipe in `implementation-plan.md:99-114` and `Makefile:25-36` is the same target. Its
  fresh-wheel install, `--no-deps` boundary, complete `tests/integration/test_no_extras.py tests/unit` selection,
  15 core module selectors, both reports, and 100% threshold were independently inspected and executed.
- `uv lock --check` -> passed; the lock records the three extras, regular Pydantic and SQLAlchemy development
  dependencies, Zensical `0.0.13`, mkdocstrings `1.x`, and the supported Python range.
- `uv build` -> passed; exactly one wheel and one source distribution were produced. Distribution metadata contains
  `>=3.12, <3.15` and exactly the `demo`, `pydantic`, and `sqlalchemy` extras.
- `make docs/build` -> passed; Zensical built the site and generated API page. `make docs/serve` started the server at
  `http://localhost:10000`; a deliberate timeout stopped the live server.
- `uv run --no-sync pytest -o addopts="" tests/integration/test_docs.py` -> passed; 3 tests passed, including the API
  and Payment reverse-path assertions.
- `uv run --no-sync pytest -o addopts="" tests/integration/test_package_install.py` -> passed; wheel and sdist
  installed and the installed demo ran outside the checkout.
- `uv run --no-sync pytest -o addopts="" tests/integration/test_project_config.py` -> passed; 4 configuration tests
  passed.
- All six example scripts passed. The all-feature and named non-interactive demos passed; the invalid feature produced
  Typer exit code 2. An additional outside-checkout all-feature demo smoke passed, but exposed the reduced bundled
  runtime examples described in S04.
- All 12 Python/variant matrix cells passed independently with isolated environments. Each cell ran 90 tests, 2
  deselected `absent_extra` tests, all required examples, the non-interactive CLI, and 100% measured-code coverage.
- Documentation Python fences executed successfully: 15 fences across 12 documentation pages. The active mkdocstrings
  configuration rendered all 15 construct factories and every signature parameter in
  `docs/site/api-reference/index.html`.
- Standalone Ruff, ty, and typos commands -> passed for the complete source, test, example, and documentation scopes.
- Workflow YAML parsing -> passed for all 5 workflow files. Independent assertions verified the 12-cell matrix, 7
  retained quality artifacts, 4 release outputs, exact release artifact handoff, deployment permissions, and merged
  documentation gate.
- `git diff --check` -> passed. No generated `docs/site`, `dist/`, coverage, or JUnit output is tracked.
- `py-buzz` inspection -> `BetwixtError -> Buzz -> Exception`; `DeclarationError.require_condition(False, "bad")`
  raised `DeclarationError` with the expected normalized message.
- Independent adversarial probes passed for Pydantic `ClassVar` exclusion, Pydantic projection rejection, registry
  snapshots, subclass compatibility, nested and partial behavior, structured diagnostics, workflow boundaries, and
  artifact metadata. The SQLAlchemy unknown-projection and slotted-dataclass projection probes failed as described in
  C03 and C05.


## Acceptance Criteria Verification

### Implementation plan

| AC      | Status | Evidence                                                                                                                                                                                                                                                                                   |
| ------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 01/AC01 | ✓      | Public exports in `src/betwixt/__init__.py:1-19`; core import and surface tests in `tests/integration/test_no_extras.py:8-16`.                                                                                                                                                             |
| 01/AC02 | ✓      | Exact/MRO/built-in registry order in `src/betwixt/adapters/registry.py:22-33`; precedence tests in `tests/unit/test_core_contract.py:47-60`.                                                                                                                                               |
| 01/AC03 | ✓      | Adapter and field snapshots in `src/betwixt/betwixt.py:55-62,95-102`; replacement test in `tests/unit/test_core_contract.py:63-116`.                                                                                                                                                       |
| 01/AC04 | ✓      | Typed references and declaration validation in `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:63-79`; malformed-reference tests in `tests/unit/test_core_coverage.py:168-210`.                                                                                                    |
| 01/AC05 | ✓      | Optional lookup remains lazy in `src/betwixt/adapters/base.py:9-33`; isolated missing-extra assertions in `tests/integration/test_no_extras.py:18-48`.                                                                                                                                     |
| 02/AC01 | ✓      | Normalization and forward-reference handling in `src/betwixt/annotations.py:11-32`; matrix tests in `tests/unit/test_core_coverage.py:97-109`.                                                                                                                                             |
| 02/AC02 | ✓      | Recursive compatibility and tuple-shape rules in `src/betwixt/annotations.py:34-78`; grammar coverage in `tests/unit/test_tasks_01_06_exhaustive.py:47-60`.                                                                                                                                |
| 02/AC03 | ✓      | Unsupported nested grammar rejects in `src/betwixt/annotations.py:81-132`; unsupported-shape tests in `tests/unit/test_core_coverage.py:149-165`.                                                                                                                                          |
| 02/AC04 | ✓      | Native dataclass field/read/construct boundary in `src/betwixt/adapters/dataclass.py:20-49`; native boundary tests in `tests/unit/test_core_coverage.py:38-47`. Projection support is incomplete for slotted dataclasses; see C05.                                                         |
| 03/AC01 | ✓      | Directional callable requirements in `src/betwixt/betwixt.py:296-313`; independent pairwise execution in `tests/unit/test_tasks_01_06_exhaustive.py:63-83`.                                                                                                                                |
| 03/AC02 | ✓      | The 15 names are exported by `src/betwixt/constructs.py:28-107`; generated API and absence assertions in `tests/integration/test_docs.py:21-27`.                                                                                                                                           |
| 03/AC03 | ✓      | Implicit precedence and controls in `src/betwixt/betwixt.py:118-132`; explicit-overlap and suppression tests in `tests/unit/test_tasks_01_06_exhaustive.py:85-110`. Direction-specific test coverage remains incomplete; see S06.                                                          |
| 03/AC04 | ✓      | Declaration-only reports in `src/betwixt/betwixt.py:250-286`; status and omission tests in `tests/unit/test_core_coverage.py:412-421`.                                                                                                                                                     |
| 03/AC05 | ✓      | Declaration validation in `src/betwixt/betwixt.py:63-93` and `src/betwixt/compiler.py:22-55`; invalid declaration tests in `tests/unit/test_core_coverage.py:168-202`.                                                                                                                     |
| 04/AC01 | ✓      | Keyword-only operations and `ctx` injection in `src/betwixt/betwixt.py:234-248` and `src/betwixt/compiler.py:22-62`; signature tests in `tests/unit/test_core_coverage.py:213-236`.                                                                                                        |
| 04/AC02 | ⚠      | Ordered maps, reductions, and projections in `src/betwixt/betwixt.py:133-175`; valid projection tests in `tests/unit/test_core_contract.py:184-226`. Native projection handling is incomplete for SQLAlchemy unknown attributes and slotted dataclasses; see C03 and C05.                  |
| 04/AC03 | ✓      | Ordered writes and projection overlap in `src/betwixt/betwixt.py:133-175`; overlap assertions in `tests/unit/test_core_contract.py:147-160`.                                                                                                                                               |
| 04/AC04 | ✓      | Defaults and required-default lookup in `src/betwixt/betwixt.py:176-189`; default/partial tests in `tests/unit/test_tasks_01_06_exhaustive.py:85-110,168-182`.                                                                                                                             |
| 04/AC05 | ✓      | Structured unmapped errors in `src/betwixt/betwixt.py:192-215` and `src/betwixt/errors.py:22-47`; complete diagnostic assertions in `tests/unit/test_tasks_01_06_exhaustive.py:443-471`.                                                                                                   |
| 04/AC06 | ✓      | Full public operation and report methods in `src/betwixt/betwixt.py:234-286`; public surface and absent-name checks in `tests/integration/test_docs.py:21-27`.                                                                                                                             |
| 05/AC01 | ✓      | Nested shape traversal in `src/betwixt/betwixt.py:322-365`; list, tuple, dictionary, set, and optional assertions in `tests/unit/test_tasks_01_06_exhaustive.py:113-165`.                                                                                                                  |
| 05/AC02 | ✓      | One positional derivation per nested invocation at `src/betwixt/betwixt.py:152-171`; call-count and context assertions in `tests/unit/test_tasks_01_06_exhaustive.py:113-165`.                                                                                                             |
| 05/AC03 | ✓      | Declaration-time nested validation in `src/betwixt/betwixt.py:81-93`; malformed-shape and exception tests in `tests/unit/test_core_coverage.py:370-410`.                                                                                                                                   |
| 05/AC04 | ✓      | Empty-container and native set behavior in `src/betwixt/betwixt.py:339-358`; empty and malformed-container tests in `tests/unit/test_tasks_01_06_exhaustive.py:378-430`.                                                                                                                   |
| 06/AC01 | ✓      | Mapping-only and unknown-key checks in `src/betwixt/betwixt.py:104-115`; partial input tests in `tests/unit/test_tasks_01_06_exhaustive.py:168-202`.                                                                                                                                       |
| 06/AC02 | ✓      | Partial implicit seeding in `src/betwixt/betwixt.py:118-132`; incomplete and complete producer assertions in `tests/unit/test_tasks_01_06_exhaustive.py:432-440`.                                                                                                                          |
| 06/AC03 | ✓      | Reduction completeness and projection/default skips in `src/betwixt/betwixt.py:133-150,176-190`; sparse producer tests in `tests/unit/test_tasks_01_06_exhaustive.py:168-182`.                                                                                                             |
| 06/AC04 | ✓      | Recursive partial validation and path wrapping in `src/betwixt/betwixt.py:322-365`; all outer shapes and error paths in `tests/unit/test_core_contract.py:243-292` and `tests/unit/test_tasks_01_06_exhaustive.py:378-430`.                                                                |
| 06/AC05 | ✓      | Partial returns before construction at `src/betwixt/betwixt.py:190-191`; dictionary return assertions in `tests/unit/test_tasks_01_06_exhaustive.py:168-202`.                                                                                                                              |
| 06/AC06 | ⚠      | Rightward context and nested derivation behavior is covered in `src/betwixt/betwixt.py:152-171` and the core tests. Required leftward direction-specific nested/control coverage is absent; see S06.                                                                                       |
| 07/AC01 | ✓      | Optional metadata and development dependencies in `pyproject.toml:21-57`; no-extras import boundary in `tests/integration/test_no_extras.py:18-48`.                                                                                                                                        |
| 07/AC02 | ✓      | Canonical Pydantic fields and native construction in `src/betwixt/adapters/pydantic.py:22-58`; alias, coercion, and default tests in `tests/optional/test_pydantic_adapter.py:53-131`.                                                                                                     |
| 07/AC03 | ✓      | Alias rejection and canonical references in `src/betwixt/adapters/pydantic.py:41-55`; rejection tests in `tests/optional/test_pydantic_adapter.py:36-75`.                                                                                                                                  |
| 07/AC04 | ⚠      | Pydantic adapter tests cover native read/construct and rightward full/partial mapping in `tests/optional/test_pydantic_adapter.py:87-131`, but no representative Betwixt leftward translation is tested; see S06.                                                                          |
| 08/AC01 | ✓      | Mapper field discovery and canonical names in `src/betwixt/adapters/sqlalchemy.py:26-36`; mapped-name and registry tests in `tests/optional/test_sqlalchemy_adapter.py:48-59,259-272`.                                                                                                     |
| 08/AC02 | ✓      | `Mapped[T]` normalization and mapper-only fields in `src/betwixt/adapters/sqlalchemy.py:26-36`; normalization assertions in `tests/optional/test_sqlalchemy_adapter.py:48-58`.                                                                                                             |
| 08/AC03 | ✓      | Unloaded checks in `src/betwixt/adapters/sqlalchemy.py:38-42`; loader-proof full/partial, detached, and raise-on-lazy tests in `tests/optional/test_sqlalchemy_adapter.py:72-153`.                                                                                                         |
| 08/AC04 | ✓      | Native ORM construction in `src/betwixt/adapters/sqlalchemy.py:53-68`; constructibility matrix in `tests/optional/test_sqlalchemy_adapter.py:213-256`.                                                                                                                                     |
| 08/AC05 | ⚠      | SQLAlchemy scalar, relationship, loaded, and partial coverage is rightward-only in `tests/optional/test_sqlalchemy_adapter.py:174-210`; no representative reverse Betwixt mapping is tested; see S06.                                                                                      |
| 09/AC01 | ✓      | Deterministic base examples in `examples/user.py:9-15`, `examples/payment.py:9-11`, and `examples/order.py:9-15`; integration assertions in `tests/integration/test_examples.py:12-24`.                                                                                                    |
| 09/AC02 | ✓      | Optional example implementations in `examples/pydantic_user.py:9-47` and `examples/sqlalchemy_order.py:14-50`; optional example smoke in `tests/integration/test_examples.py:40-49`.                                                                                                       |
| 09/AC03 | ✓      | Discoverable feature functions and Rich helper in `src/betwixt_demo/features/*.py` and `src/betwixt_demo/helpers.py:62-314`; helper and feature tests in `tests/unit/test_demo.py:20-58`.                                                                                                  |
| 09/AC04 | ⚠      | Feature selection and non-interactive failure handling in `src/betwixt_demo/main.py:22-40`; selection tests in `tests/unit/test_demo.py:60-96`. The installed fallback does not preserve the full scenarios; see S04.                                                                      |
| 09/AC05 | ✓      | Deterministic output, discovery, failures, and invalid selection in `tests/integration/test_examples.py:12-49` and `tests/unit/test_demo.py:20-96`. Installed all-feature coverage is incomplete; see S04.                                                                                 |
| 10/AC01 | ✓      | Zensical and active mkdocstrings configuration in `zensical.toml:1-33` and `docs/source/api-reference.md:8-28`; generated API assertions passed.                                                                                                                                           |
| 10/AC02 | ✓      | Exact navigation in `zensical.toml:7-19`; independent navigation assertion passed in `tests/integration/test_docs.py:30-58`.                                                                                                                                                               |
| 10/AC03 | ⚠      | Python fences pass, but `docs/source/concepts.md:23-36` and `docs/source/behavior.md:18-32` do not provide the approved complete taxonomy/context narrative, and `docs/source/cases/user.md:3-6` claims a required default absent from `examples/fixtures.py:93-102`; see S03.             |
| 10/AC04 | ✓      | Partial, diagnostics, canonical ORM names, loaded relationships, unsupported descriptors, persistence boundaries, and variant commands appear in `docs/source/behavior.md:15-32`, `docs/source/integrations.md:14-32`, `docs/source/limits.md:24-27`, and `docs/source/delivery.md:18-28`. |
| 10/AC05 | ✓      | `make docs/build` passed and `make docs/serve` started the server at the documented address; API and build assertions passed in `tests/integration/test_docs.py:13-27`.                                                                                                                    |
| 11/AC01 | ✓      | Metadata, extras, development dependencies, backend bound, and 100% threshold in `pyproject.toml:11-12,21-27,35-57,64-73,96-101`.                                                                                                                                                          |
| 11/AC02 | ✓      | Three-by-four matrix and per-cell reports in `.github/workflows/quality.yml:12-63`; all 12 cells passed independently.                                                                                                                                                                     |
| 11/AC03 | ⚠      | No-extras, package, and docs jobs in `.github/workflows/quality.yml:65-124`; static workflow assertions and all local gates passed, but the no-cover policy has the reachable-path exception in S05.                                                                                       |
| 11/AC04 | ✓      | Reusable release outputs in `.github/workflows/release-verification.yml:3-68`; tag-only, all-output deployment and exact artifact handoff in `.github/workflows/deploy.yml:4-50`.                                                                                                          |
| 11/AC05 | ✓      | Closed-PR docs trigger, merge guard, merge-revision checkout, named gate, artifact download, and Pages environment in `.github/workflows/docs.yml:4-49`.                                                                                                                                   |
| 12/AC01 | ⚠      | All 12 matrix cells passed with 90 tests, 2 deselected, and 100% coverage each, but the reachable-path no-cover exception violates the stated exclusion rule; see S05.                                                                                                                     |
| 12/AC02 | ✓      | Examples, CLI, docs, package build, lock check, Ruff, ty, and typos all passed.                                                                                                                                                                                                            |
| 12/AC03 | ⚠      | Core matrices cover the main paths, but SQLAlchemy/Pydantic reverse mappings, valid leftward suppression, and valid `nested_leftward` behavior lack tests; see S06. Projection coverage also misses the C03 and C05 cases.                                                                 |
| 12/AC04 | ✓      | `git diff --check` passed and tracked-path inspection found no generated site, distribution, or unrelated artifact.                                                                                                                                                                        |


### Design plan

| AC   | Status | Evidence                                                                                                                                                                                                                                                               |
| ---- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC01 | ✓      | `Betwixt.rightward` and `leftward` have keyword-only operation arguments in `src/betwixt/betwixt.py:234-240`; dataclass translation passed.                                                                                                                            |
| AC02 | ✓      | Full and partial operation methods are present at `src/betwixt/betwixt.py:234-248`; partial return tests passed.                                                                                                                                                       |
| AC03 | ✓      | All 15 construct names are exported and the three absent pairwise aliases are absent from the generated API.                                                                                                                                                           |
| AC04 | ✓      | `FieldProxy` and declaration checks in `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:63-79`; malformed-reference tests passed.                                                                                                                               |
| AC05 | ✓      | Callable validation and reference ordering in `src/betwixt/compiler.py:22-62` and `src/betwixt/betwixt.py:217-232`; ordering tests passed.                                                                                                                             |
| AC06 | ✓      | Direct context and one-call-per-boundary derivation behavior in `src/betwixt/betwixt.py:152-171`; rightward and pairwise tests passed.                                                                                                                                 |
| AC07 | ✓      | Implicit compatibility, suppression, reports, and unmapped remedies in `src/betwixt/betwixt.py:118-132,250-286`; diagnostic tests passed.                                                                                                                              |
| AC08 | ✓      | Map/reduction availability and ordered writes in `src/betwixt/betwixt.py:133-175`; full and partial matrices passed.                                                                                                                                                   |
| AC09 | ⚠      | Projection metadata and valid Pydantic/dataclass paths work, but SQLAlchemy unknown projected attributes and slotted dataclass instances are not handled; see C03 and C05.                                                                                             |
| AC10 | ✓      | Literal, factory, and required defaults in `src/betwixt/betwixt.py:176-189`; default tests passed.                                                                                                                                                                     |
| AC11 | ✓      | Class-body order and later writes are implemented in `src/betwixt/betwixt.py:133-175`; overlap tests passed.                                                                                                                                                           |
| AC12 | ✓      | Mapping-only partial boundary and key presence in `src/betwixt/betwixt.py:104-115`; malformed-input tests passed.                                                                                                                                                      |
| AC13 | ✓      | Sparse maps and recursive containers in `src/betwixt/betwixt.py:133-175,322-365`; path-aware partial tests passed.                                                                                                                                                     |
| AC14 | ✓      | Complete partial reductions use `source_adapter.construct` in `src/betwixt/betwixt.py:145-150`; reduction availability tests passed.                                                                                                                                   |
| AC15 | ✓      | Partial projections are skipped at `src/betwixt/betwixt.py:138-143`; partial projection tests passed.                                                                                                                                                                  |
| AC16 | ✓      | Partial operations return before the default loop at `src/betwixt/betwixt.py:176-191`; default omission tests passed.                                                                                                                                                  |
| AC17 | ✓      | Compatibility grammar in `src/betwixt/annotations.py:34-78`; recursive type matrix passed.                                                                                                                                                                             |
| AC18 | ✓      | Nested grammar and tuple/container shape rules in `src/betwixt/annotations.py:81-125`; shape tests passed.                                                                                                                                                             |
| AC19 | ✓      | Exact/MRO/built-in lookup and declaration snapshots in `src/betwixt/adapters/registry.py:22-33` and `src/betwixt/betwixt.py:55-62`; registry tests passed.                                                                                                             |
| AC20 | ⚠      | Native dataclass construction works, but `DataclassAdapter.project()` calls `vars()` unconditionally and rejects a valid slotted dataclass; see C05.                                                                                                                   |
| AC21 | ✓      | Pydantic extra, canonical fields, aliases, coercion, defaults, ClassVar exclusion, and native validation tests passed.                                                                                                                                                 |
| AC22 | ⚠      | SQLAlchemy mapper discovery, canonical names, loaded-state checks, native construction, and no-persistence boundaries pass; projection unknown-field rejection is incomplete, see C03.                                                                                 |
| AC23 | ✓      | Betwixt-owned declaration, adapter, partial, default, unloaded, and unmapped errors are implemented and tested.                                                                                                                                                        |
| AC24 | ✓      | No serialization, schema, source-validation, or persistence layer was added; boundaries are documented in `docs/source/integrations.md:3-5,31-32`.                                                                                                                     |
| AC25 | ✓      | Phase 1 public declarations, dataclass mapping, diagnostics, and quality gates pass in the core suites.                                                                                                                                                                |
| AC26 | ✓      | Phase 2 reductions, projections, defaults, nested containers, and partial matrices pass except the projection edge cases in C03 and C05.                                                                                                                               |
| AC27 | ⚠      | Optional extras, isolated boundary, canonical adapters, and examples pass; the required representative reverse mapping tests are absent for both optional adapters, see S06.                                                                                           |
| AC28 | ⚠      | Zensical and active generated API content pass, but the conceptual taxonomy/context narrative and User case claim are incomplete, see S03.                                                                                                                             |
| AC29 | ⚠      | Checkout examples and CLI pass, but installed-package fallback modules reduce User, Payment, and Order to simplified dataclass demos, see S04.                                                                                                                         |
| AC30 | ⚠      | CI matrix, reports, retention, package/site gates, release, and docs deployment pass. The line-coverage gate is 100%, but a reachable production line is excluded by an unjustified no-cover pragma and required reverse-direction tests are missing; see S05 and S06. |


## Scope Verification

Every path listed in the journal's task entries was directly inspected. The rows group those paths by the plan task that
justifies them; generated `docs/site`, `dist`, coverage, and JUnit outputs remain untracked and are not implementation
scope.

| Files                                                                                                           | Justification                                                                              | Status |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------ |
| `src/betwixt/__init__.py`, `version.py`, `annotations.py`, `refs.py`, `types.py`, `declaration.py`, `errors.py` | Tasks 01-02 and 04 public contracts, annotations, references, and errors                   | ✓      |
| `src/betwixt/adapters/**`                                                                                       | Tasks 01, 02, 07, and 08 registry, dataclass, Pydantic, and SQLAlchemy adapters            | ⚠      |
| `src/betwixt/betwixt.py`, `compiler.py`, `constructs.py`, `engine.py`, `explain.py`, `nested.py`, `partial.py`  | Tasks 03-06 constructs, translation, diagnostics, nested traversal, and partial operations | ⚠      |
| `src/betwixt_demo/**`                                                                                           | Task 09 demo discovery, Rich presentation, feature selection, and installed fallback       | ⚠      |
| `examples/**`                                                                                                   | Task 09 deterministic base and optional examples                                           | ✓      |
| `tests/unit/**`                                                                                                 | Tasks 01-06 core, diagnostics, coverage, and demo tests                                    | ⚠      |
| `tests/optional/**`                                                                                             | Tasks 07-08 native Pydantic and SQLAlchemy matrices                                        | ⚠      |
| `tests/integration/**`                                                                                          | Tasks 09-12 examples, no-extras, package, docs, and configuration gates                    | ⚠      |
| `zensical.toml`, `docs/source/**`, `docs/mkdocs.yaml`                                                           | Task 10 Zensical configuration, content, generated API, and MkDocs removal                 | ⚠      |
| `pyproject.toml`, `uv.lock`, `Makefile`                                                                         | Tasks 07-11 dependencies, lock resolution, quality, docs, build, and release commands      | ✓      |
| `README.md`, `CONTRIBUTING.md`, `examples/README.md`                                                            | Tasks 09-11 project, documentation, and variant instructions                               | ✓      |
| `.github/workflows/main.yml`, `quality.yml`, `release-verification.yml`, `deploy.yml`, `docs.yml`               | Tasks 11-12 quality, release, and documentation delivery workflows                         | ✓      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md`                                                  | Task 12 execution record                                                                   | ✓      |


## Prior Review Resolution

- **C01** ✓ Fully resolved. `implementation-plan.md:99-114` names `make qa/test/no-extras` as authoritative;
  `Makefile:25-36`
  implements the fresh-wheel/module-selector recipe and `tests/integration/test_project_config.py:64-83` asserts its
  alignment. The command passed with 100% installed-package coverage.
- **C02** ✓ Fully resolved. `src/betwixt/adapters/pydantic.py:22-24` derives fields from `model_fields`; the ClassVar
  regression and native construction pass in `tests/optional/test_pydantic_adapter.py:151-163`.
- **C03** ⚠ Partially resolved. Projection producers are explicit and Pydantic/dataclass invalid types and unreadable
  fields are adapter-owned at `src/betwixt/betwixt.py:138-143` and the adapter `project()` methods. The SQLAlchemy
  adapter still extracts only `_fields` at `src/betwixt/adapters/sqlalchemy.py:44-51`, silently dropping an arbitrary
  projected attribute; the independent probe reproduced `{'value': 1}` after adding `model.extra = True`. See C03.
- **C04** ✓ Fully resolved. Tag deployment declares `contents: read` with `id-token: write` at
  `.github/workflows/deploy.yml:17-24`; the workflow YAML and configuration tests passed.
- **S01** ✓ Fully resolved. `.github/workflows/release-verification.yml:40-68` builds and uploads exactly one wheel and
  sdist under distinct release names, and `.github/workflows/deploy.yml:28-50` downloads, counts, and publishes those
  files without `uv build`.
- **S02** ✓ Fully resolved. `Makefile:77-104` has no `publish` target or phony entry, and
  `tests/integration/test_project_config.py:64-83` asserts that neither `publish:` nor `git push` remains.


## Findings

### Summary

| Finding | Title                                                               | Outcome |
| ------- | ------------------------------------------------------------------- | ------- |
| C03     | SQLAlchemy projections still discard unknown attributes             |         |
| C05     | Slotted dataclass projections fail at the adapter boundary          |         |
| S03     | Documentation does not deliver the complete approved narrative      |         |
| S04     | Installed demo fallback does not preserve the implemented scenarios |         |
| S05     | A reachable Pydantic detection path is excluded from coverage       |         |
| S06     | Required reverse-direction acceptance coverage is incomplete        |         |


### Critical

#### C03: SQLAlchemy projections still discard unknown attributes


#### Where

`src/betwixt/adapters/sqlalchemy.py:44-51` and `tests/optional/test_sqlalchemy_adapter.py:61-70`


#### Issue

`SQLAlchemyAdapter.project()` validates the projected type and reads every mapper field, but never checks for unknown
instance attributes. A direct probe created `Model(value=1)`, assigned `model.extra = True`, and received `{'value': 1}`
instead of a Betwixt-owned adapter error. The existing SQLAlchemy projection test covers wrong types and unreadable
fields,
not unknown fields.


#### Impact

The projection contract silently discards data on a supported native boundary. This violates design AC09's explicit
unknown-field rejection and leaves the prior C03 projection finding only partially resolved.


#### Fix

Reject public projected attributes that are not mapper fields while allowing SQLAlchemy's internal instance state. Add a
SQLAlchemy regression test that assigns an unknown attribute and asserts the adapter-owned error before final
construction.


#### Outcome


----

#### C05: Slotted dataclass projections fail at the adapter boundary


#### Where

`src/betwixt/adapters/dataclass.py:29-40`


#### Issue

`DataclassAdapter.project()` calls `vars(value)` unconditionally to find unknown projected fields. A valid
`@dataclass(slots=True)` destination has no `__dict__`, so a direct projection probe raises the raw `TypeError: vars()
argument must have __dict__ attribute` instead of extracting its declared fields.


#### Impact

A standard-library dataclass supported by the adapter cannot be returned by a full projection. This violates the native
dataclass boundary and design AC09/AC20 even though ordinary dataclass projection tests and the 100% line gate pass.


#### Fix

Handle slotted dataclasses by extracting declared fields with `getattr` without requiring `__dict__`; retain unknown-
attribute rejection for instances that do have an instance dictionary. Add a slotted projection regression test.


#### Outcome


### Significant

#### S03: Documentation does not deliver the complete approved narrative


#### Where

`docs/source/concepts.md:23-36`, `docs/source/behavior.md:18-32`, `docs/source/cases/user.md:3-6`,
`docs/source/cases/order.md:3-5`, and `examples/fixtures.py:70-102`


#### Issue

The Python fences execute, but the documentation is not complete against the approved Documentation Architecture. The
Concepts page does not provide the complete construct taxonomy/table or explain aliases, callable ordering, or typed
runtime context. The Behavior page omits the nested container behavior. The User case claims a required default although
`user_mapping()` has only a pairwise mapping and no default declaration. The Order case claims a customer although the
shared fixture has `identifier`, `address`, `items`, and `note`, but no customer.


#### Impact

The generated API page is accurate while the conceptual site teaches an incomplete and partly false contract. The
existing
documentation test checks fences, keywords, and generated names at `tests/integration/test_docs.py:30-58`; it does not
check narrative completeness or the claimed User/Order behavior.


#### Fix

Expand the Concepts and Behavior pages with the approved taxonomy, context, alias, and nested-shape contract. Align the
User and Order prose with the shared fixtures, or implement and test the claimed default/customer scenario. Add semantic
documentation assertions for the required narrative claims.


#### Outcome


----

#### S04: Installed demo fallback does not preserve the implemented scenarios


#### Where

`src/betwixt_demo/example_loader.py:7-14`, `src/betwixt_demo/runtime_examples/pydantic_user.py:3-33`,
`src/betwixt_demo/runtime_examples/payment.py:3-35`, `src/betwixt_demo/runtime_examples/order.py:3-31`, and
`tests/integration/test_package_install.py:13-36`


#### Issue

The checkout demo loads the real `examples` package, but an installed package falls back to simplified dataclass
modules.
The bundled `pydantic_user` module contains no Pydantic or SQLAlchemy, the bundled Payment module has no currency or
context, and the bundled Order module has no nested values or patch. An outside-checkout all-feature run passed while
printing those reduced models. The package smoke tests only the Payment feature, so this mismatch is not detected.


#### Impact

The installed `betwixt-demo` does not demonstrate the optional native adapters or the nested/context/partial behavior
that
the shipped feature names and documentation promise. A successful package smoke can therefore validate the wrong demo.


#### Fix

Ship runtime examples that preserve the documented scenarios and optional boundaries, or package the shared examples for
the installed command. Extend the outside-checkout smoke to run all features and assert representative nested, context,
partial, Pydantic, and SQLAlchemy output.


#### Outcome


----

#### S05: A reachable Pydantic detection path is excluded from coverage


#### Where

`src/betwixt/adapters/base.py:15-18`


#### Issue

The `issubclass(type_, BaseModel)` path at line 18 is a normal, reachable Pydantic detection path, but it carries
`# pragma: no cover` with a comment describing only the no-Pydantic isolated boundary. A tracing probe using a
user-defined Pydantic model reached line 18. The line is testable and is already reached by the optional adapter matrix;
it is not structural or intentionally untestable.


#### Impact

The repository can claim 100% measured coverage while excluding a reachable production path without an applicable
justification. This violates the explicit local no-cover rule in design AC30 and implementation Task 06/11/12.


#### Fix

Remove the pragma from line 18 and retain the existing user-defined Pydantic discovery test, or replace it with a
precise
justification for an actually untestable line. Re-run every 100% coverage gate.


#### Outcome


----

#### S06: Required reverse-direction acceptance coverage is incomplete


#### Where

`tests/optional/test_pydantic_adapter.py:99-131`, `tests/optional/test_sqlalchemy_adapter.py:102-210`,
`tests/unit/test_core_coverage.py:370-379`, and `tests/unit/test_tasks_01_06_exhaustive.py:204-220`


#### Issue

The optional Betwixt mappings exercise rightward full/partial translation, but neither optional suite declares a
representative leftward mapping. The valid `nested_leftward` factory is constructed but never translated, and
`disable_implicit_leftward` appears only in an invalid-anchor test. Line coverage reaches shared implementation lines
without proving these direction-specific dispatch and suppression paths.


#### Impact

The required design AC27 and Task 12 AC03 matrices do not establish bidirectional optional adapter behavior or every
directional construct/control. A future leftward regression can pass all current tests and the 100% threshold.


#### Fix

Add Pydantic and SQLAlchemy full/partial leftward mappings, valid `nested_leftward` full and partial cases, and valid
leftward implicit suppression tests with assertions for context, native construction, and sparse output.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

C03 and C05 must be resolved before approval. S03-S06 must be addressed before the whole-plan acceptance matrix is
complete.
