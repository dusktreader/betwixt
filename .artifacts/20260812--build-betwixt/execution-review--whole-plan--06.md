# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review verifies the prior findings, all design and implementation acceptance criteria, the complete
quality matrix, native adapter boundaries, documentation, examples, and delivery workflows.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--05.md`


## Scope

**whole-plan** - Iteration 06


## Issue Summary

- **Critical**:    1
- **Significant**: 1
- **Trivial**:     0


## Verification Evidence

- `make qa/full` -> passed; 100 tests passed, 100% coverage across 721 measured statements. One existing SQLite
  `ResourceWarning` was emitted.
- `make qa/test/no-extras` -> passed; 48 tests passed, 2 skipped, and 100% coverage across 593 installed-package core
  statements. Both `.junit.xml` and `.coverage.xml` were written. Coverage emitted non-failing not-imported warnings
  for the zero-statement `betwixt.nested` and `betwixt.partial` modules.
- The no-extras contract was independently checked: `implementation-plan.md:99-114`, `Makefile:25-36`, and
  `quality.yml:65-85` all select `make qa/test/no-extras`; the recipe builds a fresh wheel, installs it with no
  dependencies, selects `tests/integration/test_no_extras.py tests/unit`, measures the explicit core module list, and
  retains the 100% threshold and both reports.
- `uv lock --check` -> passed; 76 packages resolved. The lock records the supported Python range, three package extras,
  Pydantic, SQLAlchemy, Zensical, mkdocstrings, and the bounded build backend.
- `uv build` -> passed; exactly one wheel and one source distribution were produced. Wheel metadata contains Python
  `>=3.12,<3.15` after normalizing packaging whitespace and exactly `demo`, `pydantic`, and `sqlalchemy` extras.
- `make docs/build` -> passed; Zensical generated the site and API page. `make docs/serve` started at
  `http://localhost:10000` and was deliberately terminated by a five-second timeout.
- `uv run --no-sync pytest -o addopts="" tests/integration/test_package_install.py` -> passed; both wheel and source
  distribution were installed and the complete installed demo ran outside the checkout.
- `uv run --no-sync pytest -o addopts="" tests/integration/test_docs.py` -> passed; 4 tests passed, including the API,
  navigation, semantic narrative, Payment reverse, and partial assertions.
- All 16 executable Python documentation fences passed in isolated namespaces. Installation shell snippets were
  inspected
  without executing mutating commands.
- All six example scripts, all-feature and named non-interactive demos passed. The invalid feature smoke returned Typer
  exit code 2. An independent base-extra installed demo smoke also passed outside the checkout.
- All 12 Python/variant matrix cells passed independently with separate environments. Each cell ran 97 tests with
  100% measured-code coverage, its required examples, non-interactive CLI, Ruff, ty, and typos checks.
- The four documented representative variant command blocks passed with their documented interpreters and extras. The
  full workflow matrix uses exactly 3 Python versions crossed with 4 variants, for 12 cells.
- Standalone Ruff, ty, and typos commands -> passed for the complete source, test, example, and documentation scopes.
- YAML parsing -> passed for all 5 workflow files. Independent assertions verified the 12-cell matrix, variant extras,
  no-extras boundary, report guards, artifact retention, release handoff, tag-only deployment, and merged-PR docs gate.
- `git diff --check` -> passed. No generated `docs/site`, `dist/`, coverage, or JUnit output is tracked.
- `py-buzz` -> passed; `BetwixtError -> Buzz -> Exception`, and `DeclarationError.require_condition(False, "bad")`
  raised `DeclarationError` with the expected message.
- Adversarial probes passed for Pydantic `ClassVar` exclusion, Pydantic projection rejection, SQLAlchemy dynamic
  projection rejection, registry snapshots, reverse optional-adapter mappings, nested reverse behavior, slotted
  dataclass projections, workflow boundaries, and artifact metadata.
- An adversarial uninspectable default-factory probe raised raw `ValueError: signature unavailable` during declaration
  instead of `DeclarationError`; this is recorded as C06. Coverage analysis also found excluded reachable optional
  import lines at `src/betwixt/adapters/pydantic.py:16-17` and `src/betwixt/adapters/sqlalchemy.py:17-18`; this is
  recorded as S07.


## Acceptance Criteria Verification

### Implementation plan

| AC      | Status | Evidence                                                                                                                                                                                                                         |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | Public exports in `src/betwixt/__init__.py:1-19`; dependency-free import in `tests/integration/test_no_extras.py:13-16`.                                                                                                         |
| 01/AC02 | ✓      | Exact/MRO/built-in lookup in `src/betwixt/adapters/registry.py:22-33`; precedence tests in `tests/unit/test_core_contract.py:47-60`.                                                                                             |
| 01/AC03 | ✓      | Adapter and field snapshots in `src/betwixt/betwixt.py:95-102`; replacement test in `tests/unit/test_core_contract.py:63-116`.                                                                                                   |
| 01/AC04 | ✓      | Typed references and declaration checks in `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:63-79`; malformed-reference tests passed.                                                                                     |
| 01/AC05 | ✓      | Isolated no-extras lookup assertions in `tests/integration/test_no_extras.py:20-74`; `make qa/test/no-extras` passed.                                                                                                            |
| 02/AC01 | ✓      | Normalization and forward-reference handling in `src/betwixt/annotations.py:11-32`; matrix tests in `tests/unit/test_core_coverage.py:97-109`.                                                                                   |
| 02/AC02 | ✓      | Recursive compatibility and tuple rules in `src/betwixt/annotations.py:34-78`; grammar tests passed.                                                                                                                             |
| 02/AC03 | ✓      | Unsupported nested grammar rejects in `src/betwixt/annotations.py:81-132`; unsupported-shape tests passed.                                                                                                                       |
| 02/AC04 | ✓      | Native dataclass reads and construction in `src/betwixt/adapters/dataclass.py:20-49`; native boundary tests passed.                                                                                                              |
| 03/AC01 | ✓      | Directional callable requirements in `src/betwixt/betwixt.py:296-313`; independent pairwise tests passed.                                                                                                                        |
| 03/AC02 | ✓      | The 15 approved factories are exported by `src/betwixt/constructs.py:28-107`; forbidden aliases remain absent.                                                                                                                   |
| 03/AC03 | ✓      | Implicit precedence and controls in `src/betwixt/betwixt.py:118-132`; overlap and suppression tests passed.                                                                                                                      |
| 03/AC04 | ✓      | Declaration-only reports in `src/betwixt/betwixt.py:250-286`; status and omission tests passed.                                                                                                                                  |
| 03/AC05 | ⚠      | Callable, reference, anchor, and ordinary factory validation passes, but an uninspectable callable reaches raw `ValueError` through `src/betwixt/compiler.py:35-43`; see C06.                                                    |
| 04/AC01 | ✓      | Keyword-only operations and `ctx` injection in `src/betwixt/betwixt.py:234-248` and `src/betwixt/compiler.py:22-62`; signature tests passed.                                                                                     |
| 04/AC02 | ✓      | Ordered maps, reductions, and projections in `src/betwixt/betwixt.py:133-175`; Pydantic, SQLAlchemy, and slotted projection probes passed.                                                                                       |
| 04/AC03 | ✓      | Ordered writes and projection overlap in `src/betwixt/betwixt.py:133-175`; overlap assertions passed.                                                                                                                            |
| 04/AC04 | ✓      | Defaults and required-default lookup in `src/betwixt/betwixt.py:176-189`; default and partial tests passed.                                                                                                                      |
| 04/AC05 | ✓      | Structured unmapped errors in `src/betwixt/betwixt.py:192-215` and `src/betwixt/errors.py:22-47`; diagnostic assertions passed.                                                                                                  |
| 04/AC06 | ✓      | Full public operations, reports, constructs, adapters, and errors are exported; `tests/integration/test_docs.py:21-27` passed.                                                                                                   |
| 05/AC01 | ✓      | Nested shape traversal in `src/betwixt/betwixt.py:322-365`; container assertions passed.                                                                                                                                         |
| 05/AC02 | ✓      | One derivation per nested invocation at `src/betwixt/betwixt.py:152-171`; call-count and context tests passed in both directions.                                                                                                |
| 05/AC03 | ✓      | Declaration-time nested validation in `src/betwixt/betwixt.py:81-93`; malformed-shape tests passed.                                                                                                                              |
| 05/AC04 | ✓      | Empty-container and native set behavior in `src/betwixt/betwixt.py:339-358`; edge tests passed.                                                                                                                                  |
| 06/AC01 | ✓      | Mapping-only and unknown-key checks in `src/betwixt/betwixt.py:104-115`; partial input tests passed.                                                                                                                             |
| 06/AC02 | ✓      | Partial implicit seeding in `src/betwixt/betwixt.py:118-132`; incomplete and complete producer tests passed.                                                                                                                     |
| 06/AC03 | ✓      | Reduction completeness and projection/default skips in `src/betwixt/betwixt.py:133-150,176-190`; sparse tests passed.                                                                                                            |
| 06/AC04 | ✓      | Recursive partial validation and path wrapping in `src/betwixt/betwixt.py:322-365`; shape and path tests passed.                                                                                                                 |
| 06/AC05 | ✓      | Partial methods return before construction at `src/betwixt/betwixt.py:190-191`; dictionary return tests passed.                                                                                                                  |
| 06/AC06 | ✓      | Direct and derived context behavior is exercised in both directions by core and optional tests.                                                                                                                                  |
| 07/AC01 | ✓      | Optional metadata and development dependencies in `pyproject.toml:21-57`; absent-extra tests passed.                                                                                                                             |
| 07/AC02 | ✓      | Canonical Pydantic fields and native construction in `src/betwixt/adapters/pydantic.py:22-58`; alias and coercion tests passed.                                                                                                  |
| 07/AC03 | ✓      | Alias rejection and canonical references in `src/betwixt/adapters/pydantic.py:41-55`; rejection tests passed.                                                                                                                    |
| 07/AC04 | ✓      | Pydantic full/partial reverse and native-boundary matrix in `tests/optional/test_pydantic_adapter.py:36-199`.                                                                                                                    |
| 08/AC01 | ✓      | Mapper field discovery and canonical names in `src/betwixt/adapters/sqlalchemy.py:26-36`; mapper and registry tests passed.                                                                                                      |
| 08/AC02 | ✓      | `Mapped[T]` normalization and mapper-only fields in `src/betwixt/adapters/sqlalchemy.py:26-36`; normalization tests passed.                                                                                                      |
| 08/AC03 | ✓      | Unloaded checks in `src/betwixt/adapters/sqlalchemy.py:38-42`; loader-proof full, partial, detached, and raise-on-lazy tests passed.                                                                                             |
| 08/AC04 | ✓      | Native ORM construction in `src/betwixt/adapters/sqlalchemy.py:60-75`; constructibility tests passed.                                                                                                                            |
| 08/AC05 | ✓      | SQLAlchemy scalar, relationship, reverse, canonical-name, precedence, and absent-extra tests passed in `tests/optional/test_sqlalchemy_adapter.py:49-317`.                                                                       |
| 09/AC01 | ✓      | Deterministic base examples in `examples/user.py:9-15`, `payment.py:9-11`, and `order.py:9-15`; integration outputs passed.                                                                                                      |
| 09/AC02 | ✓      | Optional examples in `examples/pydantic_user.py:28-47`, `sqlalchemy_order.py:33-50`, and `sqlalchemy_user.py:3-10`; no-persistence smoke passed.                                                                                 |
| 09/AC03 | ✓      | Discoverable features and Rich presentation in `src/betwixt_demo/features/*.py` and `src/betwixt_demo/helpers.py:62-314`; demo tests passed.                                                                                     |
| 09/AC04 | ✓      | Feature selection, context, nested values, sparse patches, and non-interactive failure handling are implemented in `src/betwixt_demo/main.py:22-40` and the three feature/example modules; checkout and installed smokes passed. |
| 09/AC05 | ✓      | Deterministic output, discovery, failures, invalid selection, all/named selection, and package smoke passed in `tests/integration/test_examples.py` and `tests/unit/test_demo.py`.                                               |
| 10/AC01 | ✓      | Zensical and active mkdocstrings configuration in `zensical.toml:1-33` and `docs/source/api-reference.md:8-28`; generated API assertions passed.                                                                                 |
| 10/AC02 | ✓      | Exact navigation in `zensical.toml:7-19`; navigation assertions passed.                                                                                                                                                          |
| 10/AC03 | ✓      | Complete taxonomy, context, ordering, nested behavior, cases, and 16 executable documentation fences are present and passed semantic assertions.                                                                                 |
| 10/AC04 | ✓      | Partial semantics, diagnostics, canonical ORM names, loaded relationships, unsupported descriptors, persistence boundaries, and variant commands are documented and tested.                                                      |
| 10/AC05 | ✓      | `make docs/build`, `make docs/serve`, generated API checks, and `tests/integration/test_docs.py` passed.                                                                                                                         |
| 11/AC01 | ✓      | Metadata, extras, development dependencies, backend bound, and 100% threshold in `pyproject.toml:11-12,21-57,96-101`.                                                                                                            |
| 11/AC02 | ✓      | Three-by-four matrix and per-cell commands/reports in `.github/workflows/quality.yml:12-63`; all 12 cells passed independently.                                                                                                  |
| 11/AC03 | ⚠      | No-extras, package, and docs jobs pass, but reachable optional-import lines remain excluded by unjustified pragmas at `src/betwixt/adapters/pydantic.py:16-17` and `sqlalchemy.py:17-18`; see S07.                               |
| 11/AC04 | ✓      | Reusable outputs in `.github/workflows/release-verification.yml:3-68`; tag-only deployment, exact artifact handoff, and no rebuild in `.github/workflows/deploy.yml:4-50`.                                                       |
| 11/AC05 | ✓      | Closed-PR docs trigger, merge guard, merge-revision checkout, named gate, artifact download, and Pages environment in `.github/workflows/docs.yml:4-49`.                                                                         |
| 12/AC01 | ⚠      | All 12 variant cells pass at 100%, but the no-cover policy is not satisfied by the reachable optional-import exclusions; see S07.                                                                                                |
| 12/AC02 | ✓      | Examples, CLI, docs, package build, lock check, Ruff, ty, and typos all passed.                                                                                                                                                  |
| 12/AC03 | ⚠      | Core, adapter, nested, partial, tuple, diagnostic, projection, and reverse behavior passed; the uninspectable factory declaration path lacks owned-error coverage and fails C06.                                                 |
| 12/AC04 | ✓      | `git diff --check` passed and generated site, distributions, coverage, and JUnit output remain untracked.                                                                                                                        |


### Design plan

| AC   | Status | Evidence                                                                                                                                                                                                                           |
| ---- | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AC01 | ✓      | `Betwixt.rightward` and `leftward` use keyword-only operation arguments at `src/betwixt/betwixt.py:234-240`; dataclass translation passed.                                                                                         |
| AC02 | ✓      | Full and partial operation methods are present at `src/betwixt/betwixt.py:234-248`; full/partial tests passed.                                                                                                                     |
| AC03 | ✓      | All 15 constructs are exported and the three absent pairwise aliases are absent from generated API output.                                                                                                                         |
| AC04 | ✓      | `FieldProxy` and declaration checks in `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:63-79`; malformed-reference tests passed.                                                                                           |
| AC05 | ✓      | Callable validation and reference ordering in `src/betwixt/compiler.py:22-62` and `src/betwixt/betwixt.py:217-232`; ordering tests passed.                                                                                         |
| AC06 | ✓      | Direct context and one-call-per-boundary derivation behavior in `src/betwixt/betwixt.py:152-171`; both directions passed.                                                                                                          |
| AC07 | ✓      | Implicit compatibility, suppression, reports, and unmapped remedies in `src/betwixt/betwixt.py:118-132,250-286`; diagnostic tests passed.                                                                                          |
| AC08 | ✓      | Map/reduction availability and ordered writes in `src/betwixt/betwixt.py:133-175`; full and partial matrices passed.                                                                                                               |
| AC09 | ✓      | Projection metadata and valid Pydantic, SQLAlchemy, ordinary dataclass, and slotted dataclass paths pass adapter and full-translation probes.                                                                                      |
| AC10 | ✓      | Literal, factory, and required defaults in `src/betwixt/betwixt.py:176-189`; default tests passed.                                                                                                                                 |
| AC11 | ✓      | Class-body order and later writes in `src/betwixt/betwixt.py:133-175`; overlap tests passed.                                                                                                                                       |
| AC12 | ✓      | Mapping-only partial boundary in `src/betwixt/betwixt.py:104-115`; malformed-input tests passed.                                                                                                                                   |
| AC13 | ✓      | Sparse maps and recursive containers in `src/betwixt/betwixt.py:133-175,322-365`; path-aware tests passed.                                                                                                                         |
| AC14 | ✓      | Complete partial reductions use `source_adapter.construct` at `src/betwixt/betwixt.py:145-150`; availability tests passed.                                                                                                         |
| AC15 | ✓      | Partial projections are skipped at `src/betwixt/betwixt.py:138-143`; projection-skip tests passed.                                                                                                                                 |
| AC16 | ✓      | Partial operations return before defaults at `src/betwixt/betwixt.py:176-191`; omission tests passed.                                                                                                                              |
| AC17 | ✓      | Compatibility grammar in `src/betwixt/annotations.py:34-78`; recursive type matrix passed.                                                                                                                                         |
| AC18 | ✓      | Nested grammar and tuple/container rules in `src/betwixt/annotations.py:81-125`; shape tests passed.                                                                                                                               |
| AC19 | ✓      | Exact/MRO/built-in lookup and snapshots in `src/betwixt/adapters/registry.py:22-33` and `src/betwixt/betwixt.py:55-62`; registry tests passed.                                                                                     |
| AC20 | ✓      | Native dataclass construction and slotted projection in `src/betwixt/adapters/dataclass.py:29-45`; slotted and ordinary projection tests passed.                                                                                   |
| AC21 | ✓      | Pydantic extras, canonical fields, aliases, coercion, defaults, ClassVar exclusion, reverse mapping, and native validation passed.                                                                                                 |
| AC22 | ✓      | SQLAlchemy mapper discovery, canonical names, loaded state, native construction, reverse mapping, dynamic projection rejection, and no-persistence boundaries passed. Unsupported descriptors remain outside the native field set. |
| AC23 | ⚠      | Betwixt-owned declaration, adapter, partial, unloaded, missing-default, and unmapped errors pass, but an uninspectable default factory leaks `ValueError`; see C06.                                                                |
| AC24 | ✓      | No serialization, schema, source-validation, or persistence layer was added; boundaries are documented in `docs/source/integrations.md:3-5,31-32`.                                                                                 |
| AC25 | ✓      | Phase 1 public declarations, dataclass mapping, diagnostics, and quality gates pass.                                                                                                                                               |
| AC26 | ⚠      | Phase 2 reductions, projections, defaults, nesting, partials, and grammar pass; the invalid-factory declaration edge remains unresolved in C06.                                                                                    |
| AC27 | ✓      | Optional extras, isolated boundary, canonical adapters, both-direction mappings, nested relationships, and examples pass.                                                                                                          |
| AC28 | ✓      | Zensical configuration, generated API, coherent case narrative, runnable examples, adapter boundaries, and variant commands pass.                                                                                                  |
| AC29 | ✓      | Checkout and installed demos preserve User, Payment, and Order output, context, nested values, and sparse patches; wheel and sdist smokes pass.                                                                                    |
| AC30 | ⚠      | CI matrix, reports, retention, package/site gates, release, docs deployment, and 100% test thresholds pass, but reachable production lines are excluded without an allowable no-cover rationale; see S07.                          |


## Scope Verification

Every path listed in the journal's task entries was directly inspected. Generated `docs/site`, `dist`, coverage, and
JUnit outputs remain untracked and are not implementation scope.

| Files                                                                                                           | Justification                                                                              | Status |
| --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------ |
| `src/betwixt/__init__.py`, `version.py`, `annotations.py`, `refs.py`, `types.py`, `declaration.py`, `errors.py` | Tasks 01-06 public contracts, annotations, references, and errors                          | ✓      |
| `src/betwixt/adapters/**`                                                                                       | Tasks 01, 02, 07, and 08 registry, dataclass, Pydantic, and SQLAlchemy adapters            | ⚠      |
| `src/betwixt/betwixt.py`, `compiler.py`, `constructs.py`, `engine.py`, `explain.py`, `nested.py`, `partial.py`  | Tasks 03-06 constructs, translation, diagnostics, nested traversal, and partial operations | ⚠      |
| `src/betwixt_demo/**`                                                                                           | Task 09 demo discovery, Rich presentation, feature selection, and installed fallback       | ✓      |
| `examples/**`                                                                                                   | Task 09 deterministic base and optional examples                                           | ✓      |
| `tests/unit/**`                                                                                                 | Tasks 01-06 core, diagnostics, coverage, and demo tests                                    | ✓      |
| `tests/optional/**`                                                                                             | Tasks 07-08 native Pydantic and SQLAlchemy matrices                                        | ✓      |
| `tests/integration/**`                                                                                          | Tasks 09-12 examples, no-extras, package, docs, and configuration gates                    | ✓      |
| `zensical.toml`, `docs/source/**`, `docs/mkdocs.yaml`                                                           | Task 10 Zensical configuration, generated API, content, and MkDocs removal                 | ✓      |
| `pyproject.toml`, `uv.lock`, `Makefile`                                                                         | Tasks 07-11 dependencies, lock resolution, quality, docs, build, and release commands      | ✓      |
| `README.md`, `CONTRIBUTING.md`, `examples/README.md`                                                            | Tasks 09-11 project, documentation, and variant instructions                               | ✓      |
| `.github/workflows/main.yml`, `quality.yml`, `release-verification.yml`, `deploy.yml`, `docs.yml`               | Tasks 11-12 quality, release, and documentation delivery workflows                         | ✓      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md`                                                  | Task 12 execution record                                                                   | ✓      |


## Prior Review Resolution

- **C01** ✓ Fully resolved. `implementation-plan.md:99-114` names `make qa/test/no-extras` as authoritative;
  `Makefile:25-36` implements the fresh-wheel, no-dependency, installed-package recipe and the command passed at 100%.
- **C02** ✓ Fully resolved. `src/betwixt/adapters/pydantic.py:22-24` derives fields from `model_fields`; the ClassVar
  regression and native construction pass in `tests/optional/test_pydantic_adapter.py:170-182`.
- **C03** ✓ Fully resolved for the prior defect. `src/betwixt/adapters/sqlalchemy.py:48-54` rejects unknown public
  instance attributes while allowing private instrumentation state; `tests/optional/test_sqlalchemy_adapter.py:79-87`
  and an independent probe reject `model.extra` before extraction.
- **C04** ✓ Fully resolved. Tag deployment declares `contents: read` with `id-token: write` at
  `.github/workflows/deploy.yml:17-24`; YAML and configuration assertions passed.
- **C05** ✓ Fully resolved. `DataclassAdapter.project()` uses declared-field access at
  `src/betwixt/adapters/dataclass.py:29-41`; slotted and ordinary unknown-field tests passed at
  `tests/unit/test_core_contract.py:229-249`.
- **S01** ✓ Fully resolved. `.github/workflows/release-verification.yml:40-68` builds and uploads exactly one wheel and
  sdist under distinct names, while `.github/workflows/deploy.yml:28-50` downloads, counts, and publishes those exact
  files without `uv build`.
- **S02** ✓ Fully resolved. `Makefile:77-104` has no `publish` target or phony entry, and
  `tests/integration/test_project_config.py:64-83` asserts that neither `publish:` nor `git push` remains.
- **S03** ✓ Fully resolved. The semantic documentation assertions at `tests/integration/test_docs.py:72-128`, the
  complete taxonomy and behavior narrative, corrected case claims, and all executable Python fences pass.
- **S04** ✓ Fully resolved. Bundled runtime examples at `src/betwixt_demo/runtime_examples/` preserve the native User,
  context-aware Payment, and nested/partial Order scenarios; `test_package_install.py:13-46` checks both artifacts and
  all feature output outside the checkout. An independent base-extra installed smoke also passed.
- **S05** ✓ Fully resolved. The reachable Pydantic detection path in `src/betwixt/adapters/base.py:15-18` has no
  coverage pragma and is measured by the optional adapter discovery test.
- **S06** ✓ Fully resolved. Pydantic reverse tests are at `tests/optional/test_pydantic_adapter.py:36-52`, SQLAlchemy
  reverse tests at `tests/optional/test_sqlalchemy_adapter.py:192-210`, valid `nested_leftward` tests at
  `tests/unit/test_tasks_01_06_exhaustive.py:114-151`, and valid reverse suppression at lines 153-165.


## Findings

### Summary

| Finding | Title                                                                  | Outcome |
| ------- | ---------------------------------------------------------------------- | ------- |
| C06     | Uninspectable default factories leak a raw exception                   |         |
| S07     | Reachable optional-import branches use unjustified coverage exclusions |         |


### Critical

#### C06: Uninspectable default factories leak a raw exception


#### Where

`src/betwixt/compiler.py:35-43`


#### Issue

`validate_factory()` calls `signature(function)` without catching `TypeError` or `ValueError`. A callable whose
`__signature__` is unavailable therefore raises raw `ValueError` while the class declaration is being built. The plan
requires invalid default factories to raise Betwixt-owned declaration errors.

An independent probe declared a `default_rightward` with a callable whose `__signature__` property raised
`ValueError("signature unavailable")`; declaration failed with that raw ValueError rather than `DeclarationError`.


#### Impact

Declaration validation leaks an implementation-level inspection exception and violates the stable error ownership
contract. Callers cannot handle invalid default factories through the documented Betwixt declaration-error boundary.


#### Fix

Catch `TypeError` and `ValueError` around default-factory signature inspection and raise an actionable
`DeclarationError`
with the original exception as its cause. Add a regression test using an uninspectable callable, then rerun the full
coverage and variant gates.


#### Outcome


----

### Significant

#### S07: Reachable optional-import branches use unjustified coverage exclusions


#### Where

`src/betwixt/adapters/pydantic.py:16-17` and `src/betwixt/adapters/sqlalchemy.py:17-18`


#### Issue

Both missing-dependency `ImportError` branches carry `# pragma: no cover` with comments saying they are exercised by the
isolated no-extras job. They are reachable and directly exercised by
`tests/unit/test_core_coverage.py:351-367`, which imports each optional adapter and forces the corresponding dependency
import to fail. Coverage analysis independently reported these lines as excluded: Pydantic `[16, 17]` and SQLAlchemy
`[17, 18]`.

The design and implementation plans permit no-cover only for structural, trivial, or intentionally untestable lines.
These branches are testable and already have a test path, so the current 100% result excludes measurable production code
without an allowable rationale.


#### Impact

The repository claims 100% measured coverage while omitting reachable adapter error handling. A regression in either
missing-extra message or exception chaining can pass the gate even though the isolated boundary explicitly exercises
that
behavior.


#### Fix

Remove both pragmas and retain the existing missing-extra tests as measured coverage. If an exclusion is retained,
replace
it with a precise justification that satisfies the local no-cover rule and demonstrate why the existing tests cannot
measure
the lines. Rerun `make qa/full`, `make qa/test/no-extras`, and every matrix cell.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED — CHANGES REQUIRED**

C06 and S07 must be resolved before approval.
