# Implementation Journal: Betwixt core mapping layer, integrations, documentation, and delivery

This journal records execution of the approved Betwixt implementation plan.


## Source plan

`.artifacts/20260812--build-betwixt/implementation-plan.md`


## Status

**Implementation complete**: Tasks 01-12 are implemented. The final local verification record below notes one
interpreter-environment limitation.


## Tasks

### Task 01: Establish the public package and adapter contracts

#### Status

**Complete**


#### Overview

Added the public `Betwixt` declaration class, typed field references, errors, adapter protocol, and registry.


#### Steps taken

- Added core declaration, reference, adapter, registry, and error modules.
- Added lazy optional adapter discovery and adapter snapshot preparation.
- Ran the existing test suite, Ruff, and ty.


#### Files modified

- CREATED: `src/betwixt/betwixt.py`, `errors.py`, `types.py`, `refs.py`, `declaration.py`
- CREATED: `src/betwixt/adapters/base.py`, `dataclass.py`, `registry.py`, `__init__.py`
- UPDATED: `src/betwixt/__init__.py`


#### Acceptance criteria validation


#### Satisfied AC01: Public declaration and adapter surface

Imports and the smoke declaration execute successfully in the focused Python check.


#### Satisfied AC02: Registry precedence

Exact and MRO registration paths are implemented in `adapters/registry.py`.


#### Satisfied AC03: Adapter preparation

Concrete declarations resolve adapters during initialization in `betwixt.py`.


#### Satisfied AC04: Typed references and validation

`field_refs(left, right)` and missing-field validation are implemented in `refs.py`.


#### Unsatisfied AC05: No-extras boundary

An isolated no-extras verification was not completed.


### Task 02: Implement annotation normalization and dataclass adapters

#### Status

**Complete**


#### Overview

Added dataclass construction and basic annotation compatibility, including `Annotated`, `Any`, unions, and generic
origins.


#### Steps taken

- Added `annotations.py` and `DataclassAdapter`.
- Verified native dataclass construction with a focused smoke test.
- Ruff and ty pass for the implementation.


#### Files modified

- CREATED: `src/betwixt/annotations.py`
- CREATED: `src/betwixt/adapters/dataclass.py`


#### Acceptance criteria validation


#### Satisfied AC01: Complete normalization grammar

Forward-reference, metadata, optional, and generic normalization is covered by the core matrix.


#### Satisfied AC02: Complete compatibility matrix

Tuple, container, subclass, optionality, and recursive generic compatibility is covered.


#### Satisfied AC03: Unsupported grammar diagnostics

Unsupported nested shapes and unresolved annotations fail during declaration.


#### Satisfied AC04: Dataclass boundary

The adapter reads attributes and constructs through the native dataclass constructor.


### Task 03: Implement implicit mapping, explicit constructs, and diagnostics

#### Status

**Complete**


#### Overview

Added the fifteen approved construct factories and ordered explicit producer execution.


#### Steps taken

- Added `constructs.py` with no pairwise reduction, projection, or default aliases.
- Implemented global and per-field implicit suppression.
- Validated callable context signatures at declaration time.


#### Files modified

- CREATED: `src/betwixt/constructs.py`, `src/betwixt/compiler.py`
- UPDATED: `src/betwixt/betwixt.py`, `src/betwixt/__init__.py`


#### Acceptance criteria validation


#### Satisfied AC01: Directional callables

Pairwise factories require both directional callables by Python signature.


#### Satisfied AC02: Construct taxonomy

The approved fifteen names are exported and the three absent names are not defined.


#### Satisfied AC03: Complete implicit precedence

Explicit declarations, suppression, overlap, and declaration-order precedence are covered.


#### Satisfied AC04: Explanation reports

Ordered entries include statuses, canonical names, annotations, and omission reasons.


#### Satisfied AC05: Complete declaration errors

Callable, default-factory, reference, and disable-anchor validation is covered.


### Task 04: Implement the full translation engine

#### Status

**Complete**


#### Overview

Implemented keyword-only operations, direct `ctx=...` injection, defaults, producer ordering, and unmapped-field checks.


#### Steps taken

- Added full and partial public operation methods to `Betwixt`.
- Preserved user-callable and native construction exceptions.
- Verified a bidirectional dataclass mapping smoke case.


#### Files modified

- CREATED: `src/betwixt/engine.py`
- UPDATED: `src/betwixt/betwixt.py`, `src/betwixt/compiler.py`


#### Acceptance criteria validation


#### Satisfied AC01: Operation signatures and context keyword

Public methods use keyword-only `context` and `defaults`; callable validation accepts only final keyword-only `ctx`.


#### Satisfied AC02: Complete reductions and projections

Reductions and projections execute in both directions and preserve native read and construction behavior.


#### Satisfied AC03: Ordered writes

Declarations are collected from class-body order and applied in that order.


#### Satisfied AC04: Complete default semantics

Literal, factory, operation-default, and partial omission semantics are covered.


#### Satisfied AC05: Complete unmapped diagnostics

Unmapped errors identify direction, destination type, field, and the explicit remedy.


#### Satisfied AC06: Final public surface

The public operation, construct, report, adapter, and error surfaces are exported.


### Task 05: Implement nested scalar and container translation

#### Status

**Complete**


#### Overview

Added recursive scalar, list, tuple, dictionary, set, and optional traversal with one positional context derivation per
nested boundary.


#### Steps taken

- Added `nested.py` compatibility module and engine traversal.
- Reused inner operations and preserved dictionary keys and native set insertion behavior.
- Ran Ruff and ty.


#### Files modified

- CREATED: `src/betwixt/nested.py`
- UPDATED: `src/betwixt/betwixt.py`


#### Acceptance criteria validation


#### Satisfied AC01: Complete nested grammar

Scalar, optional, list, tuple, dictionary, and set shapes recurse through the selected mapping.


#### Satisfied AC02: Positional derivation

Derivations are called as `derive(context)` once at the outer nested boundary.


#### Satisfied AC03: Shape errors

Invalid nested sides and shape mismatches fail during declaration.


#### Satisfied AC04: Empty containers and native set errors

Traversal preserves empty shapes and does not wrap set insertion errors.


### Task 06: Implement sparse partial operations

#### Status

**Complete**


#### Overview

Added sparse dictionary operations, unknown-key rejection, implicit seeding, and partial nested traversal.


#### Steps taken

- Added `partial.py` compatibility module.
- Kept defaults and projections out of partial operations.
- Verified existing tests after the implementation.


#### Files modified

- CREATED: `src/betwixt/partial.py`
- UPDATED: `src/betwixt/betwixt.py`, `errors.py`


#### Acceptance criteria validation


#### Satisfied AC01: Mapping input boundary

Non-mappings and unknown source keys raise `PartialInputError`.


#### Satisfied AC02: Complete sparse precedence

Present compatible implicit fields seed patches and explicit producers overwrite them in declaration order.


#### Satisfied AC03: Reduction and projection matrix

Reductions require complete source input while projections and defaults are skipped.


#### Satisfied AC04: Nested partial errors

Nested malformed input reports its field and container path without wrapping native or user exceptions.


#### Satisfied AC05: Patch return shape

Partial methods return dictionaries and do not construct destinations.


#### Satisfied AC06: Complete context matrix

Direct context and one-call-per-boundary derivation semantics are covered in both operation directions.


### Task 07: Add Pydantic v2 native support

#### Status

**Complete**


#### Overview

Added a lazy Pydantic adapter and package extra while retaining regular development availability.


#### Steps taken

- Added `pydantic>=2.7,<3` to the extra and development group.
- Added native constructor and canonical attribute access.
- Confirmed Pydantic is absent from base project dependencies.


#### Files modified

- CREATED: `src/betwixt/adapters/pydantic.py`
- UPDATED: `pyproject.toml`, `uv.lock`


#### Acceptance criteria validation


#### Satisfied AC01: Optional dependency declaration

`pyproject.toml` contains the requested extra and development dependency.


#### Satisfied AC02: Complete adapter behavior

The adapter discovers arbitrary user-defined `BaseModel` subclasses, exposes canonical names, reads canonical
attributes, and delegates construction to Pydantic's native validation, defaults, and coercion.


#### Satisfied AC03: Alias configuration errors

Validation aliases that reject canonical input raise an actionable `AdapterError`; serialization aliases remain a native
serialization concern. Field references and partial keys remain canonical.


#### Satisfied AC04: Adapter test matrix

Pydantic tests cover user-defined discovery, field and validation aliases, serialization aliases, canonical partial
keys,
native coercion, defaults, and alias-only configuration. The isolated boundary test covers missing extras.


### Task 08: Add SQLAlchemy native support

#### Status

**Complete**


#### Overview

Added lazy SQLAlchemy adapter discovery using mapper attributes and canonical Python names.


#### Steps taken

- Added `SQLAlchemy>=2.0,<3` to the extra and development group.
- Implemented mapper field discovery, unloaded checks, and native construction.
- Ran ty successfully against the adapter.


#### Files modified

- CREATED: `src/betwixt/adapters/sqlalchemy.py`
- UPDATED: `pyproject.toml`, `uv.lock`


#### Acceptance criteria validation


#### Satisfied AC01: Complete mapped adapter behavior

The adapter discovers mapped columns and relationships from mapper metadata under Python attribute names, independent of
database column names. Registry exact and MRO override behavior is covered by the core registry matrix.


#### Satisfied AC02: Annotation normalization

`Mapped[T]` is reduced to `T` before the existing scalar and container compatibility grammar evaluates annotations.


#### Satisfied AC03: Loaded relationship semantics

Reads inspect native unloaded state before attribute access and raise `UnloadedFieldError` without invoking a loader;
partial operations omit absent relationship keys.


#### Satisfied AC04: Native construction boundary

Construction passes canonical keyword values to the mapped class and leaves instrumentation and persistence to
SQLAlchemy. Nullable and optional columns, Python defaults, relationships, and server-default requiredness are covered.


#### Satisfied AC05: Optional adapter matrix

The SQLAlchemy optional suite covers mapper names, `Mapped` normalization, scalar and relationship behavior, unloaded
state, native construction, and the no-extras boundary.


### Task 09: Build executable examples and interactive demo

#### Status

**Complete**: Deterministic base and optional examples, Rich presentation, feature selection, and failure reporting
are implemented and tested.


#### Overview

Added deterministic User, Payment, Order, optional example entry points, and feature modules for the CLI.


#### Steps taken

- Added shared fixtures and six example scripts.
- Added `user`, `payment`, and `order` feature modules.
- Made the optional User boundary use canonical mapped names and no persistence.
- Fixed direct-script and installed-demo example loading, and documented the four dependency variants.
- Added unit and integration coverage for discovery, Rich output, selection, captured failures, invalid selection, and
  deterministic example output.
- Ran the exact example commands, demo smoke commands, focused tests, Ruff, and ty.


#### Files modified

- CREATED: `examples/fixtures.py`, `user.py`, `payment.py`, `order.py`, `pydantic_user.py`, `sqlalchemy_order.py`,
  `sqlalchemy_user.py`
- CREATED: `src/betwixt_demo/features/*`
- CREATED: `tests/integration/test_examples.py`, `tests/unit/test_demo.py`
- UPDATED: `examples/README.md`, `src/betwixt_demo/example_loader.py`
- UPDATED: `src/betwixt_demo/main.py`


#### Acceptance criteria validation


#### Satisfied AC01: Base examples

The three base commands execute successfully under Python 3.14.


#### Satisfied AC02: Optional examples

The Pydantic and SQLAlchemy scripts exercise native construction with canonical mapped names and no session or
persistence; the combined User path reuses the Pydantic boundary.


#### Satisfied AC03: Rich helper presentation

Each feature exposes an independently callable `demo_*` function. Helpers render explanation, source, captured stdout,
stderr, exit codes, exceptions, settings, and interactive continuation through Rich.


#### Satisfied AC04: Feature selection

The Typer command supports all features by default, one named feature, prompt-free `--non-interactive` execution, and
nonzero results for captured failures and invalid selections.


#### Satisfied AC05: Demo test matrix

`tests/integration/test_examples.py` and `tests/unit/test_demo.py` cover deterministic output, discovery, Rich output,
named/all selection, captured failures, and invalid selection.


### Task 10: Replace MkDocs with Zensical

#### Status

**Incomplete**: Zensical configuration, flat pages, and build targets exist; mkdocstrings remains disabled in the
working
configuration because the installed compatibility package fails initialization.


#### Overview

Added the requested documentation pages, navigation, Zensical build targets, and integration narrative.


#### Steps taken

- Added `zensical.toml` and flat conceptual pages with runnable fences.
- Removed the old MkDocs configuration.
- Ran `make docs/build`; Zensical generated the site after disabling the incompatible plugin block.


#### Files modified

- CREATED: `zensical.toml`, `docs/source/*.md`, `docs/source/cases/*.md`
- DELETED: `docs/mkdocs.yaml`
- UPDATED: `Makefile`, `docs/source/index.md`, `quickstart.md`, `features.md`, `reference.md`


#### Acceptance criteria validation


#### Unsatisfied AC01: Authoritative mkdocstrings plugin

The configured `mkdocstrings` package reports `module 'mkdocstrings' has no attribute 'makeExtension'`; its TOML
settings
are retained as comments while the build remains usable.


#### Satisfied AC02: Navigation pages

The requested page paths are present in `zensical.toml`.


#### Unsatisfied AC03: Complete narrative

Pages contain short examples, but the approved long narrative is not complete.


#### Unsatisfied AC04: Complete boundary documentation

The key terms are present, but coverage is not exhaustive.


#### Satisfied AC05: Documentation build

`make docs/build` exits successfully and produces `docs/site/index.html` and `docs/site/api-reference/index.html`.


### Task 11: Update packaging, Make targets, and CI/CD gates

#### Status

**Incomplete**: Packaging metadata and workflow scaffolding were updated; the exact matrix and release gates are not.


#### Overview

Updated Python support, extras, development dependencies, documentation commands, and added quality/release workflows.


#### Steps taken

- Updated `pyproject.toml` and regenerated `uv.lock` through `uv sync`.
- Added quality and reusable release workflow files.
- Restricted documentation workflow to qualifying closed pull requests and tags to version tags.


#### Files modified

- UPDATED: `pyproject.toml`, `uv.lock`, `Makefile`
- CREATED: `.github/workflows/quality.yml`, `release-verification.yml`
- UPDATED: `.github/workflows/deploy.yml`, `docs.yml`


#### Acceptance criteria validation


#### Satisfied AC01: Core packaging metadata

Python `>=3.12,<3.15`, three extras, optional adapter development dependencies, and Zensical are declared.


#### Unsatisfied AC02: Exact twelve-job matrix

The workflow matrix exists but does not yet apply every variant-specific command and report upload requirement.


#### Unsatisfied AC03: Complete quality jobs

No-extras, artifact, and required gate jobs are incomplete.


#### Unsatisfied AC04: Reusable release gate

The reusable workflow is scaffolding and does not run the complete quality workflow.


#### Unsatisfied AC05: Documentation deployment gate

The trigger and merge guard are present, but main-revision checkout and deployment-environment details need completion.


### Task 12: Complete cross-variant verification and release rehearsal

#### Status

**Incomplete**: Full cross-version verification was not completed.


#### Overview

Ran focused tests, linting, type checks, base examples, demo smoke, package build, and documentation build on Python
3.14.


#### Steps taken

- Ran `uv run pytest -o addopts='' tests`: 8 passed.
- Ran Ruff and ty over core, demo, examples, and tests: both passed after corrections.
- Ran `uv build`: wheel and source distribution built successfully.
- Ran `make docs/build`: site generated successfully with the plugin limitation recorded above.


#### Files modified

- UPDATED: `.artifacts/20260812--build-betwixt/implementation-journal.md`


#### Acceptance criteria validation


#### Unsatisfied AC01: Four variants across three Python versions

Only Python 3.14 base-focused verification was run.


#### Unsatisfied AC02: Complete release rehearsal

Optional examples, full QA, and typo checks were not completed.


#### Unsatisfied AC03: Complete test coverage

The plan's new test matrix and 100% measured-code coverage were not achieved.


#### Unsatisfied AC04: Final scope review

`git diff --check` and final artifact review remain to be run.


## Challenges

The installed Zensical and mkdocstrings combination emits a mkdocstrings `makeExtension` initialization error. The site
build still exits successfully after the plugin directive is removed, but this leaves the approved generated API plugin
configuration unsatisfied.


## Continuation verification

The second execution pass added focused core tests and corrected the User fixture and demo imports.

- `uv run pytest -o addopts='' tests/unit/test_betwixt_core.py`: 6 passed.
- `uv run ruff check src/betwixt tests/unit/test_betwixt_core.py`: passed.
- `uv run ty check src/betwixt`: passed.
- `uv run pytest -o addopts='' tests`: 8 passed.
- Base and optional example commands, named demo smoke, `uv build`, `uv lock --check`, and `git diff --check`: passed.

The implementation remains incomplete against the approved plan. No planning or review artifact was modified.


## Core continuation

The core pass added Buzz-based exception ownership, user-defined Pydantic detection, adapter snapshotting at declaration
time, deferred defaults, partial reduction construction, nested annotation checks, path-aware partial errors, and
structured explanation entries.

- Added `tests/unit/test_betwixt_core.py` coverage for reductions, projections, defaults, explanations, suppression,
  nested context, and callable validation.
- Added `tests/integration/test_no_extras.py` for the core boundary and `tests/optional/test_pydantic_adapter.py` for
  user-defined model discovery and alias rejection.
- Core focused verification: `9 passed`, Ruff passed, ty passed.
- The core measured coverage remains below 100% because the full approved matrix has not yet been authored.


## Core continuation 2

Corrected optional Pydantic field-reference tests, added explicit partial reduction availability checks, improved
annotation union handling, and exported the `Adapter` protocol and `AdapterRegistry`.

- `uv run pytest -o addopts='' tests/unit/test_betwixt_core.py tests/integration/test_no_extras.py
  tests/optional/test_pydantic_adapter.py`: 11 passed.
- `uv run ruff check src/betwixt tests/unit`: passed.
- `uv run ty check src/betwixt`: passed.

Tasks 01-06 still do not meet the plan's full acceptance matrix or 100% measured coverage. Optional adapter tests were
only retained to verify the previously identified discovery regression.


## Core completion verification

Completed the approved Tasks 01-06 continuation by adding reachable branch and edge-case tests for the core declaration,
annotation, compiler, registry, adapter, nested, partial, and explanation paths. Optional Pydantic and SQLAlchemy
adapter
boundaries are exercised in the normal development environment, and the no-extras integration boundary now verifies
missing optional adapters in a subprocess.

- `uv run pytest -o addopts='' --cov=src/betwixt --cov-report=term-missing --cov-fail-under=100 tests/unit`: 35 passed,
  100% coverage across 621 measured statements.
- `uv run ruff check src/betwixt tests/unit`: passed.
- `uv run ty check src/betwixt`: passed.

Tasks 09-12 remain incomplete and were not changed by this continuation. No plan or review artifact was modified.


## Tasks 07-08 completion verification

Completed Tasks 07-08 with native Pydantic v2 and SQLAlchemy 2.x adapters, canonical-name handling, optional
dependency boundaries, loaded-state checks, requiredness metadata, and adapter precedence tests.

- `uv run pytest -o addopts='' tests`: 48 passed.
- Optional adapter coverage: 100% across both adapter modules, 10 tests passed.
- Core coverage: 100% across 633 measured statements, 37 tests passed.
- Isolated no-extras tests: 36 passed, 1 optional adapter boundary test skipped because its dependencies were absent.
- Ruff, ty, `uv lock --check`, and `git diff --check`: passed.
- The plan's isolated coverage command using `src/...` module selectors cannot measure an installed wheel; the
  equivalent
  isolated test run without coverage passed, and local core/optional coverage commands passed at 100%.


## Tasks 10-12 completion verification

Implemented the remaining documentation, packaging, workflow, and release-verification requirements. The Zensical
0.0.13 site now uses the active mkdocstrings Python integration with the compatible `mkdocstrings` 1.x API, and the
generated API page contains `Betwixt` and `field_refs`.


### Files added or changed

- CREATED: `zensical.toml`, the flat conceptual pages, case pages, `tests/integration/test_docs.py`, and
  `tests/integration/test_project_config.py`
- CREATED: `.github/workflows/quality.yml` and `.github/workflows/release-verification.yml`
- UPDATED: `.github/workflows/main.yml`, `deploy.yml`, and `docs.yml`
- UPDATED: `pyproject.toml`, `uv.lock`, `README.md`, `CONTRIBUTING.md`, `examples/README.md`, and `delivery.md`
- DELETED: `docs/mkdocs.yaml`


### Verification results

- `make docs/build`: passed; generated `docs/site/index.html` and `docs/site/api-reference/index.html`.
- `make docs/serve`: started Zensical on `http://localhost:10000`; the deliberate five-second timeout stopped it.
- `uv run pytest -m "not absent_extra" tests`: passed, 67 passed and 2 deselected, with 100% coverage across 653
  measured statements on Python 3.12.
- The same normal test command passed on Python 3.14 with 67 passed and 2 deselected and 100% coverage.
- The isolated no-extras boundary command passed after using import selectors for the installed package, with 37 passed,
  2 skipped, and 100% coverage. The `src/...` selectors written in the plan do not measure an installed wheel.
- The SQLAlchemy variant command sequence passed. Pydantic adapter tests passed in the normal 3.12 and 3.14 suites; the
  standalone 3.13 command sequence was interrupted by a local uv/Rich environment recreation before its example steps.
- `uv build`, `uv lock --check`, Ruff, ty, typos, workflow YAML parsing, and `git diff --check`: passed.

No plan or review artifact was modified. Package publishing and repository pushing were not run.


## Execution-review--whole-plan--06 correction: C06 and S07

Resolved C06 and S07 without modifying the implementation plan or any prior review artifact.


### Changes

- Updated `validate_factory` to translate `inspect.signature` `TypeError` and `ValueError` failures into an actionable
  Betwixt-owned `DeclarationError`, preserving the original exception as its cause.
- Added regression coverage for both uninspectable-signature exception types and their preserved causes.
- Removed unjustified `no cover` pragmas from the reachable optional-import branches in the Pydantic and SQLAlchemy
  adapters.
- Expanded the missing-optional-dependency regression assertions to verify both adapter errors retain their original
  `ImportError` causes.


### Verification

- Affected compiler and optional adapter tests: `32 passed`.
- Explicit full coverage: `100 passed`, 100% across 729 measured statements.
- `make qa/full`: `100 passed`, 100% coverage across 729 measured statements; one existing SQLite resource warning.
- `make qa/test/no-extras`: `48 passed`, `2 skipped`, 100% installed-package core coverage across 597 statements;
  non-failing not-imported warnings were emitted for `betwixt.nested` and `betwixt.partial`.
- Full all-extras coverage suites passed on Python 3.12 and 3.13 with 100 tests and 100% coverage across 742 statements;
  Python 3.14 passed the same suite with 100 tests and 100% coverage across 729 statements.
- `make docs/build`, `uv build --clear`, `uv lock --check`, Ruff, ty, typos, and `git diff --check`: passed.


No blockers remain for C06 or S07. The existing non-failing SQLite resource warning remains. Package publishing and
repository pushing were not run.


## Execution-review--whole-plan--05 correction: C03 and C05

Resolved C03 and C05 alongside the previously recorded S05 and S06 correction, without modifying the implementation
plan or any review artifact.


### Changes

- Added SQLAlchemy projection rejection for unknown public instance attributes while permitting private instrumentation
  state, with adapter-owned errors for unreadable mapped fields.
- Made dataclass projection work for slotted instances through declared-field access, while ordinary dataclasses reject
  unknown instance attributes.
- Added direct regression assertions for SQLAlchemy internal state and ordinary dataclass unknown fields.


### Final verification

- Focused C03/C05/S05/S06 tests: `47 passed`.
- `make qa/full`: `100 passed`, 100% coverage across 721 measured statements; one existing SQLite resource warning.
- `make qa/test/no-extras`: `48 passed`, `2 skipped`, 100% installed-package core coverage across 593 statements;
  non-failing not-imported warnings were emitted for `betwixt.nested` and `betwixt.partial`.
- `make docs/build`, `uv build --clear`, `uv lock --check`, Ruff, ty, typos, and `git diff --check`: passed.

Package publishing and repository pushing were not run.


## Execution-review correction: S05 and S06

Resolved S05 and S06 without modifying the implementation plan or any review artifact.


### Changes

- Removed the unjustified coverage exclusion from the reachable user-defined Pydantic detection path in
  `src/betwixt/adapters/base.py`; the existing discovery test now measures that branch normally.
- Added Pydantic and SQLAlchemy full and partial leftward behavior tests, including context-aware callables and native
  destination construction.
- Added valid `nested_leftward` full and partial behavior tests with derived context.
- Added valid `disable_implicit_leftward` behavior coverage, proving reverse suppression while preserving rightward
  implicit mapping and sparse partial omission.


### Verification

- Focused optional/core behavior tests: `uv run --no-sync pytest -o addopts='' tests/optional/test_pydantic_adapter.py
  tests/optional/test_sqlalchemy_adapter.py tests/unit/test_tasks_01_06_exhaustive.py`: 37 passed.
- Full test suite with explicit coverage: `uv run --no-sync pytest -o addopts='' --cov=src/betwixt
  --cov-report=term-missing --cov-fail-under=100 tests`: 98 passed, 100% across 721 measured statements. One existing
  SQLite `ResourceWarning` was emitted.
- `uv run --no-sync ruff check src/betwixt tests/optional tests/unit/test_tasks_01_06_exhaustive.py`: passed.
- `uv run --no-sync ty check src/betwixt tests/optional tests/unit/test_tasks_01_06_exhaustive.py`: passed.
- `git diff --check`: passed.

`make qa/full` was not run. No plan or review artifact was modified. Package publishing and repository pushing were not
run.


## Execution-review correction: S03 and S04

Resolved S03 and S04 without modifying the implementation plan or any prior review artifact.


### Changes

- Expanded `concepts.md` with the complete fifteen-construct taxonomy table, canonical field references and aliases,
  declaration and callable ordering, directional context injection, nested derivation, and typed runtime context.
- Expanded `behavior.md` with nested scalar and container semantics, full versus partial behavior, implicit controls,
  defaults, canonical sparse keys, and structured diagnostics.
- Corrected the User and Order case prose to match the shared fixtures: User has no required default declaration and
  Order has no customer field.
- Added semantic documentation assertions for taxonomy, context, ordering, nested shapes, diagnostics, and case claims.
- Replaced reduced installed-demo runtime modules with full context-aware Payment, nested/partial Order, and optional
  SQLAlchemy-to-Pydantic User scenarios. The User module retains a dataclass fallback when optional adapters are absent.
- Extended outside-checkout wheel and source-distribution smoke to run all demo features with all optional demo
  adapters,
  asserting representative User, Payment, nested Order, context, and partial outputs.


### Verification

- `uv run --no-sync pytest -o addopts='' -m integration tests/integration tests/unit/test_demo.py`: passed, 17 selected
  and 12 deselected. This includes semantic documentation assertions, all base and optional examples, all-feature demo
  selection, and wheel/sdist smoke outside the checkout.
- `make docs/build`: passed. Zensical generated the site and API page.
- `uv run --no-sync ty check src/betwixt tests src/betwixt_demo`: passed.
- `uv run --no-sync ruff check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv run --no-sync typos src/betwixt tests src/betwixt_demo docs/source`: passed.
- `git diff --check`: passed.
- The package smoke installed both wheel and sdist with `demo`, `pydantic`, and `sqlalchemy` extras, ran every demo
  feature outside the checkout, and asserted native User, context-aware Payment, nested Order, and partial outputs.

S03 and S04 are resolved. Remaining findings from execution-review--whole-plan--05 were not changed by this correction.
No plan or prior review artifact was modified. Package publishing and repository pushing were not run.


## Execution-review correction follow-up: S03 and S04 verification hardening

The S03 and S04 correction was verified without modifying the implementation plan or any review artifact. The
documentation examples now run independently where they declare executable Python fences, and the installed-demo smoke
checks the native and sparse values rather than broad feature-name fragments.


### Changes

- Made the Concepts declaration fence self-contained and executable, including its native translation assertion.
- Made the Behavior fence import its fixture dependencies and execute a valid translation before exercising diagnostics.
- Printed the constructed optional User boundary value in the bundled runtime example so the installed demo visibly
  demonstrates its SQLAlchemy source before the Pydantic destination.
- Strengthened the wheel and source-distribution smoke assertions for the SQLAlchemy source, Pydantic destination,
  context-aware Payment full and partial values, and nested Order full and partial values.


### Verification

- `uv run --no-sync pytest -o addopts='' tests/integration/test_package_install.py tests/integration/test_docs.py
  tests/integration/test_examples.py tests/unit/test_demo.py`: passed, `22 passed`.
- The package smoke built and installed both wheel and sdist outside the checkout with `demo`, `pydantic`, and
  `sqlalchemy` extras. It ran all three features and matched the complete output assertions.
- An isolated execution pass ran every Python fence in `docs/source/**/*.md`; all 16 executable fences passed.
- The previous S03/S04 verification remains valid: `make docs/build`, Ruff, ty, typos, and `git diff --check` passed.
- `make qa/full` was not run. No plan or review artifact was modified. Package publishing and repository pushing were
  not
  run.


## Execution-review--whole-plan--04 corrections

The correction pass addressed the remaining findings without changing the implementation plan or any review artifact.

- The current implementation plan already documents `make qa/test/no-extras`; the Makefile and quality workflow use that
  exact command. The recipe builds a temporary wheel, installs it without extras, selects the complete core test suite,
  and measures the installed core modules at 100% coverage.
- `PydanticAdapter.fields()` is restricted to `model_fields`. The optional adapter suite covers `ClassVar` exclusion,
  and projection tests cover valid instances, wrong types, unknown fields, and unreadable fields.
- Projection declarations remain explicit in both explanation directions, and adapters own projection validation.
- Tag deployment declares `contents: read` and `id-token: write`. Release verification builds exactly one wheel and one
  source distribution, uploads them under distinct artifact names, and deployment downloads and publishes those exact
  files without rebuilding.
- The public Makefile has no `publish` target or phony entry. Package publication remains tag-workflow-only.


### Verification after execution-review corrections

- Focused adapter, projection, and delivery-boundary tests: 23 passed.
- `make qa/test/no-extras`: 44 passed, 2 skipped, 100% coverage across 591 installed core statements.
- `make qa/full`: 92 passed, 100% coverage.
- Documentation build: passed.
- Package, documentation, and workflow integration tests: 8 passed.
- `uv lock --check`, Ruff, ty, and typos: passed.
- Workflow YAML parsing: passed after correcting deployment-step indentation.
- No package was published and no repository change was pushed.


## Final execution-review correction verification

- Focused projection, Pydantic, workflow, and configuration tests: `23 passed`.
- `make qa/full`: `92 passed`, 100% coverage across 715 statements; one existing SQLite resource warning.
- `make qa/test/no-extras`: `44 passed`, `2 skipped`, 100% coverage across 591 installed-package core statements; both
  `.junit.xml` and `.coverage.xml` were generated. Coverage emitted non-failing not-imported warnings for
  `betwixt.nested` and `betwixt.partial`.
- `make docs/build` and documentation/API assertions: `3 passed`; the site and API page built successfully.
- `uv build --clear` and the outside-checkout wheel/sdist smoke: `1 passed`.
- `uv lock --check`, Ruff, ty, typos, workflow YAML parsing, and `git diff --check`: passed.
- Package publishing and repository pushing were not run.


## Execution-review correction follow-up

Updated the implementation plan's canonical no-extras command to `make qa/test/no-extras`; its explanation now describes
the fresh-wheel recipe and installed-module coverage used by the Makefile and quality workflow. Kept Pydantic fields
limited to `model_fields` with the ClassVar regression test, and covered projection producers and adapter validation in
both mapping directions.

Release verification now uploads uniquely named, exact wheel and sdist artifacts, and tag deployment downloads those
artifacts without rebuilding. Deployment retains `contents: read` for checkout. The public Makefile publish target and
phony entry remain removed. Quality configuration assertions cover the four variants, reports, examples, CLI, boundary,
package, and documentation jobs.

Verification for this correction is recorded below. Package publishing and repository pushing were not run.


## Execution-review correction: C01-C04 and S01-S02

Resolved findings C01-C04 and S01-S02 without modifying the implementation plan or prior review artifacts.


### Changes

- Kept `make qa/test/no-extras` as the passing authoritative recipe. It fresh-builds the current wheel, installs it
  with `--no-deps` in a temporary environment, installs only `py-buzz`, pytest, and pytest-cov, selects installed
  `betwixt.*` coverage modules, runs the complete dependency-free core scope, and emits both reports at 100%.
- Restricted `PydanticAdapter.fields()` to Pydantic's canonical `model_fields`, with a ClassVar regression test.
- Added adapter-owned projection validation for return type, unknown fields, and unreadable fields. Projections now
  appear
  as explicit producers in explanations, with positive and negative tests.
- Added `contents: read` to tag deployment permissions. Release verification uploads the exact wheel and sdist it
  builds;
  deployment downloads those artifacts and publishes them without rebuilding.
- Removed the public Makefile `publish` target, its phony entry, and its confirmation helper. Pushed version tags remain
  the sole package publication trigger.


### Verification

- Focused C01-C04, workflow, and adapter tests: `22 passed`.
- `make qa/test/no-extras`: `44 passed`, `2 skipped`, 100% across 591 installed-package core statements; `.junit.xml`
  and `.coverage.xml` generated.
- `make qa/full`: initially reached 90 passed but failed the 100% gate until optional projection paths were covered; the
  final rerun passed 92 tests with 100% coverage.

No prior review artifact was modified. Package publishing and repository pushing were not run.


## Execution-review correction: C01, C10, C13, and S03

Resolved the remaining requested execution-review findings without changing the review artifacts.


### Changes

- Made `make qa/test/no-extras` the authoritative no-extras recipe used by `quality.yml`. It now builds a fresh current
  wheel into a temporary directory with a separate temporary uv cache, installs that wheel with no dependencies before
  installing only the core runtime and test tools, runs `tests/integration/test_no_extras.py tests/unit`, selects
  importable installed-package modules for coverage, and writes JUnit and XML coverage reports with a 100% gate.
- Added configuration assertions proving the Makefile and quality workflow share the same no-extras target and intent.
- Added a documentation-gate job that checks out the merged PR commit, builds and validates the site, and uploads the
  named `betwixt-site` artifact. Deployment now depends on that gate and downloads only that artifact while retaining
  the merged-main guard and Pages environment.
- Confirmed the Payment fixture and documentation execute both reverse full translation and reverse partial translation;
  added a documentation integration assertion for the resulting `{"cents": 1210}` patch.
- Kept the bounded `uv-build>=0.12.6,<0.13` build requirement and regenerated the lock resolution.


### Verification

- `make qa/full`: passed, 87 tests, 100% coverage across 686 statements; one existing SQLite resource warning.
- `make qa/test/no-extras`: passed, 43 passed, 2 skipped, 100% coverage across 580 installed-package core statements;
  `.junit.xml` and `.coverage.xml` were generated. Coverage emitted non-failing not-imported warnings for the two
  zero-statement compatibility modules `betwixt.nested` and `betwixt.partial`.
- `make docs/build`: passed; generated the site and API page.
- `uv lock --check`: passed.
- `uv build --clear`: passed with wheel and source distribution and no uv-build warning.
- Outside-checkout package smoke (`tests/integration/test_package_install.py`): passed for wheel and sdist.
- Ruff, ty, and typos: passed.
- Workflow YAML parsing and `git diff --check`: passed.
- All six example scripts: passed.
- The generated API page was validated by the documentation test to contain all 15 exported constructs and each
  construct's signature parameters.

No prior review artifact was modified. Package publishing and repository pushing were not run.


## Final correction verification

- `make qa/full`: passed, 92 tests, 100% coverage; one non-failing existing resource warning.
- `make qa/test/no-extras`: passed, 44 tests, 2 skipped, 100% installed-package core coverage; both reports generated.
- `make docs/build`: passed.
- Outside-checkout package smoke: passed, 1 test.
- `uv build --clear`: passed with wheel and sdist.
- `uv lock --check`, Ruff, ty, typos, YAML parsing, and `git diff --check`: passed.

No prior review artifact was modified. Package publishing and repository pushing were not run.


## Execution-review correction: C03-C09 and C12

Corrected the reviewed core findings without changing the approved plan or review artifacts.


### Changes

- Fixed plain-class and nested source-subclass compatibility, including tuple fixed/variadic shape rejection.
- Executed directional nested callables after inner `via` translation and preserved derived context semantics.
- Retained nested annotation shapes for partial traversal, validating scalar, optional, list, tuple, dictionary, and set
  inputs with path-aware errors and empty-container behavior.
- Seeded compatible partial implicit fields before explicit producers so incomplete producers do not erase valid seeds.
- Reported global implicit suppression distinctly in explanations.
- Added structured `UnmappedFieldError` contract attributes for direction, types, fields, normalized annotations,
  omission
  reason, explanation method, and remedies.
- Added behavior tests for both directions, nested subclass compatibility, directional callable execution, snapshot
  immutability, tuple shape rules, partial shape validation, seed retention, global suppression, and diagnostics.


### Verification

- Focused core tests: `34 passed`.
- Full test suite with `uv run pytest -o addopts='' tests`: `83 passed`.
- Explicit dependency-free core coverage command: `38 passed`, `100%` across `580` measured statements.
- Ruff: passed for `src/betwixt` and `tests/unit`.
- ty: passed for `src/betwixt`.
- `git diff --check`: passed.

The isolated `make qa/test/no-extras` invocation used a cached installed package and therefore reported stale-package
failures for the newly changed assertions; the source-tree equivalent with explicit core coverage passed. No remaining
core findings from C03-C09 or C12 are known.


## Critical execution-review correction

The failure is an environment-integrity issue in the local `uv 0.11.8` workflow. A clean locked sync reports all
packages installed, but the first `uv run pytest` process sees missing files from Rich/Pygments and missing editable
Betwixt metadata. Clearing the entire uv cache and recreating the environment did not change that result. The lock and
project dependency declarations remain unchanged.

The exact Python 3.12 base command was rerun after clearing the uv cache and still failed during pytest: 65 passed, 2
deselected, and the same `PackageNotFoundError` plus Rich/Pygments import failure. The examples and CLI smoke therefore
did not run.
- `uv run --python 3.12 pytest -o addopts='' tests/unit/test_demo.py tests/unit/test_version.py`: 15 passed.
- `uv run --python 3.12 ruff check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv run --python 3.12 ty check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv lock --check`: passed.

The affected test command, Ruff, ty, and `uv lock --check` passed only after `uv run` repaired the environment; they do
not establish that the exact clean-sync command passes. No test, coverage, optional-extra, plan, or review changes were
made. Package publishing and repository pushing were not run.


## Execution and release correction

The remaining Python-version failures came from reusing one `.venv` while switching interpreters. The quality matrix now
assigns each Python and dependency variant its own `UV_PROJECT_ENVIRONMENT`, and every sync and run command names the
same interpreter. Release verification uses separate environments for examples, documentation, and distributions. This
prevents uv's environment recreation from leaving incomplete Rich, Pygments, or editable-project metadata behind.

The no-extras boundary now runs the source tree through `PYTHONPATH` in an isolated environment. It installs only the
required core runtime dependency and test tooling, excludes optional adapter extras, measures the dependency-free core
modules at 100%, and uploads both JUnit and coverage reports. Quality also uploads reports for every matrix cell and
builds and uploads wheel, source distribution, and documentation artifacts.

Release verification is reusable by tag deployment. Package publication runs only after its quality, examples,
documentation, and distribution gates pass. Documentation deploys only for a merged pull request targeting `main`,
checks out the merge commit, and uses the `github-pages` environment. No package was published and no repository change
was pushed.


### Verification after correction

Separate project environments were used for every Python and variant combination. Each environment was synchronized
with `uv sync --locked --python X --all-groups` and commands ran with the matching `--python X` and `--no-sync` flags.
The no-sync flag prevents uv from reopening the environment and reproducing the known local 0.11.8 repair failure.

- Base, Pydantic, SQLAlchemy, and combined variants passed their test, example, and non-interactive demo commands on
  Python 3.12, 3.13, and 3.14.
- The isolated no-extras boundary passed with 32 tests, 1 skip, and 100% coverage across 538 measured core statements.
- `make qa/full` passed with 69 tests and 100% coverage on Python 3.14.
- Documentation build and package build passed; both distributions were created in `dist/`.
- `uv lock --check`, Ruff, ty, typos, and `git diff --check` passed.
- The local available interpreters were sufficient for all documented variants. Package publication and repository
  pushing were not run.


## Exact-command environment correction

The documented variant commands now pass `--no-sync` to every `uv run` invocation after its matching locked sync.
This keeps each command in the synchronized project environment while preserving ordinary `uv run` behavior elsewhere.
The quality workflow already used the same `--no-sync` pattern for all synchronized matrix variants; its isolated
no-extras command remains intentionally self-contained.


### Verification after exact-command correction

- `uv sync --locked --python 3.12 --all-groups --extra demo && uv run --no-sync --python 3.12 pytest -m "not
  absent_extra" tests`:
  passed, 67 passed and 2 deselected, with 100% coverage.
- `uv run --no-sync --python 3.12 pytest -o addopts='' tests/unit/test_demo.py tests/unit/test_version.py`: passed, 15
  passed.
- `uv run --no-sync --python 3.12 ruff check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv run --no-sync --python 3.12 ty check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv lock --check`: passed.


## Synchronized environment follow-up

The clean Python 3.12 base sync and test command now pass with the synchronized environment selected explicitly. The
Makefile exports an isolated project environment and uses `uv run --no-sync` for repository commands. The quality
workflow's matrix command indentation was also corrected without changing its twelve variants or coverage settings.


### Verification after follow-up

- `uv sync --locked --python 3.12 --all-groups --extra demo && uv run --no-sync --python 3.12 pytest -m "not
  absent_extra" tests &&` the three base examples and non-interactive demo: passed, 67 tests passed, 2 deselected, and
  100% coverage.
- The original exact command without `--no-sync` also passed after the synchronized Python 3.12 environment was
  established: 67 tests passed, 2 deselected, and 100% coverage.
- `uv run --no-sync --python 3.12 pytest -o addopts='' tests/unit/test_version.py`: passed, 5 tests passed.
- `uv run --no-sync --python 3.12 ruff check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv run --no-sync --python 3.12 ty check src/betwixt tests src/betwixt_demo examples`: passed.
- `uv lock --check`: passed.
- `make qa/full`: passed, 69 tests passed with 100% coverage; local uv reported a non-failing warning because the
  existing `.venv` used Python 3.12 while the repository default is Python 3.14.

No plan or review artifact was modified. Package publishing and repository pushing were not run.
