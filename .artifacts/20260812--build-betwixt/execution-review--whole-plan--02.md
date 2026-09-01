# Execution Review: Betwixt core mapping layer, integrations, documentation, and delivery

This whole-plan re-review independently checks the implementation, prior finding, executable gates, acceptance criteria,
and release artifacts after the Python 3.12 environment correction.


## Source Artifacts

- **Implementation journal**: `.artifacts/20260812--build-betwixt/implementation-journal.md`
- **Implementation plan**: `.artifacts/20260812--build-betwixt/implementation-plan.md`
- **Approved design plan**: `.artifacts/20260812--build-betwixt/design-plan.md`
- **Prior execution review**: `.artifacts/20260812--build-betwixt/execution-review--whole-plan--01.md`


## Scope

**whole-plan** - Iteration 02


## Issue Summary

- **Critical**:    13
- **Significant**: 4
- **Trivial**:     0


## Verification Evidence

- `uv sync --locked --python 3.14 --all-groups --extra demo` -> passed in an isolated `UV_PROJECT_ENVIRONMENT`.
- `make qa/full` -> passed on Python 3.14.4: 69 passed, 100% coverage across 640 measured statements; Ruff, typos,
  and ty passed.
- The exact Python 3.12 base command from the plan, run after a clean isolated sync, -> passed: 67 passed, 2 deselected,
  100% coverage; all three base examples and the non-interactive CLI smoke passed.
- The current documented 12-cell matrix commands, each with a separate `UV_PROJECT_ENVIRONMENT` and `--no-sync`, ->
  passed for all 12 cells. Every cell reported 67 passed, 2 deselected, 100% coverage, its required examples, and the
  non-interactive CLI smoke.
- The original Python 3.12 base command without `--no-sync`, after its isolated environment was synchronized, -> passed:
  67 passed, 2 deselected, 100% coverage, examples passed, and CLI smoke passed. Prior review C01 is therefore resolved.
- The exact no-extras command documented in `implementation-plan.md:104` -> **failed**. The tests passed but the command
  exited nonzero because its `--cov=src/betwixt/...` selectors did not match the installed package modules:

  ```text
  WARNING: Failed to generate report: No data to report.
  ERROR: Coverage failure: total of 0 is less than fail-under=100
  Module src/betwixt/annotations.py was never imported. (module-not-imported)
  Module src/betwixt/adapters/base.py was never imported. (module-not-imported)
  Module src/betwixt/adapters/dataclass.py was never imported. (module-not-imported)
  Module src/betwixt/adapters/registry.py was never imported. (module-not-imported)
  Module src/betwixt/betwixt.py was never imported. (module-not-imported)
  Module src/betwixt/compiler.py was never imported. (module-not-imported)
  Module src/betwixt/constructs.py was never imported. (module-not-imported)
  Module src/betwixt/declaration.py was never imported. (module-not-imported)
  Module src/betwixt/engine.py was never imported. (module-not-imported)
  Module src/betwixt/errors.py was never imported. (module-not-imported)
  Module src/betwixt/explain.py was never imported. (module-not-imported)
  Module src/betwixt/nested.py was never imported. (module-not-imported)
  Module src/betwixt/partial.py was never imported. (module-not-imported)
  Module src/betwixt/refs.py was never imported. (module-not-imported)
  Module src/betwixt/types.py was never imported. (module-not-imported)
  FAIL Required test coverage of 100% not reached. Total coverage: 0.00%
  ======================== 37 passed, 2 skipped in 0.85s =========================
  ```

- The corrected no-extras command currently used by `quality.yml` -> passed: 32 passed, 1 skipped, 100% coverage across
  538 measured core statements. This is not the same command as the plan's documented gate and selects five named unit
  files rather than `tests/unit`.
- `uv run --no-sync --python 3.14 pytest -o addopts="" -m unit tests/unit` -> passed: 21 passed, 25 deselected.
- `uv run --no-sync --python 3.14 pytest -o addopts="" -m integration tests/integration` -> passed: 11 passed, 2
  deselected.
- `uv run --no-sync --python 3.14 betwixt-demo --feature user --non-interactive` -> passed.
- `uv run --no-sync --python 3.14 betwixt-demo --feature does-not-exist --non-interactive` -> exited 2 as required;
  Typer reported the invalid feature without prompting.
- `make docs/build` -> passed; Zensical built the site and generated API page.
- `make docs/serve` -> started Zensical at `http://localhost:10000`; a deliberate five-second timeout stopped it.
- `uv build` -> passed and produced the wheel and source distribution. It emitted the existing unbounded `uv-build`
  warning. An independent install smoke of `betwixt[demo]` then failed with `ModuleNotFoundError: No module named
  'betwixt_demo'` because neither distribution contains the console-script module or repository examples.
- `uv lock --check` -> passed.
- `uv run --no-sync --python 3.14 ruff check src/betwixt tests src/betwixt_demo examples` -> passed.
- `uv run --no-sync --python 3.14 ty check src/betwixt tests src/betwixt_demo examples` -> passed.
- `uv run --no-sync --python 3.14 typos src/betwixt tests src/betwixt_demo docs/source` -> passed.
- PyYAML parsing of all five workflow files -> passed.
- `git diff --check` -> passed for tracked changes.
- `buzz.Buzz` inspection -> `BetwixtError -> Buzz -> Exception`; inherited `Buzz` utilities such as
  `DeclarationError.require_condition()` produced a `DeclarationError` with Buzz's normalized message behavior.
- The built API page contains `Betwixt`, `MappingExplanation`, and `field_refs`, but contains zero occurrences of all 15
  construct factory names. The build smoke checks only two symbols and therefore does not establish a complete generated
  API.


## Acceptance Criteria Verification

| AC      | Status | Evidence                                                                                                                                                             |
| ------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 01/AC01 | ✓      | `src/betwixt/__init__.py:1-19`; `tests/unit/test_core_coverage.py::test_low_level_declaration_validation_and_constructor_paths`                                      |
| 01/AC02 | ✓      | `src/betwixt/adapters/registry.py:16-32`; `tests/unit/test_core_contract.py::test_registry_precedence_duplicate_and_replace`                                         |
| 01/AC03 | ⚠      | Snapshot code is at `src/betwixt/betwixt.py:54-61`; no test changes the registry after an existing mapping is declared                                               |
| 01/AC04 | ✓      | `src/betwixt/refs.py:18-36` and `src/betwixt/betwixt.py:64-75`; core declaration validation tests                                                                    |
| 01/AC05 | ✓      | Corrected isolated boundary: `tests/integration/test_no_extras.py:12-47`; 32 passed, 1 skipped                                                                       |
| 02/AC01 | ✓      | `src/betwixt/annotations.py:11-31`; `tests/unit/test_core_contract.py::test_annotations_cover_forward_optional_generics_and_any`                                     |
| 02/AC02 | ✗      | `src/betwixt/annotations.py:50-56` rejects plain-class subclasses; fixed/variadic nested tuple mismatch is accepted at `:98-109` (C03, C07)                          |
| 02/AC03 | ✓      | `src/betwixt/annotations.py:75-125`; `tests/unit/test_core_coverage.py::test_nested_declaration_validation_and_explanation_omissions`                                |
| 02/AC04 | ⚠      | `src/betwixt/adapters/dataclass.py:14-36`; native construction is tested, but the planned `__post_init__` failure case is absent                                     |
| 03/AC01 | ✗      | `src/betwixt/constructs.py:56-69` stores nested callables, but `src/betwixt/betwixt.py:148-157` never invokes them (C04)                                             |
| 03/AC02 | ✓      | `src/betwixt/constructs.py:28-89`; `betwixt.__all__` surface at `src/betwixt/__init__.py:12-19`                                                                      |
| 03/AC03 | ✓      | `src/betwixt/betwixt.py:114-128`; `tests/unit/test_betwixt_core.py::test_implicit_mapping_and_directional_explicit_write`                                            |
| 03/AC04 | ✗      | `src/betwixt/betwixt.py:224-245` ignores global suppression when producing explanations (C08)                                                                        |
| 03/AC05 | ✓      | Declaration checks at `src/betwixt/betwixt.py:62-92` and callable checks at `src/betwixt/compiler.py:22-54`; core validation tests                                   |
| 04/AC01 | ✓      | `src/betwixt/betwixt.py:196-210` and `src/betwixt/compiler.py:22-62`; `test_context_is_keyword_only_and_injected_by_name`                                            |
| 04/AC02 | ✓      | `src/betwixt/betwixt.py:134-157`; `test_reduce_projection_default_and_explanation` and exhaustive direction tests                                                    |
| 04/AC03 | ✓      | `src/betwixt/betwixt.py:129-157`; `test_all_directional_construct_families`                                                                                          |
| 04/AC04 | ✓      | `src/betwixt/betwixt.py:159-171`; `test_defaults_and_implicit_controls`                                                                                              |
| 04/AC05 | ✗      | `src/betwixt/betwixt.py:174-177` omits source type, omission reason, and the required explanation pointer (C09)                                                      |
| 04/AC06 | ✓      | Public exports at `src/betwixt/__init__.py:1-19`; `test_declaration_validation_and_explanation_are_side_effect_free`                                                 |
| 05/AC01 | ✗      | `src/betwixt/annotations.py:98-109` accepts fixed/variadic mismatch and runtime output can violate fixed arity (C07)                                                 |
| 05/AC02 | ⚠      | `src/betwixt/betwixt.py:148-153` derives once, but the required both-direction/identity/explicit-None matrix is not tested                                           |
| 05/AC03 | ✓      | `src/betwixt/betwixt.py:81-92`; `test_nested_declaration_validation_and_explanation_omissions`                                                                       |
| 05/AC04 | ⚠      | Empty list/tuple/set traversal is present at `src/betwixt/betwixt.py:287-302`; empty partial dictionaries still call the inner operation                             |
| 06/AC01 | ✗      | `src/betwixt/betwixt.py:282-300` accepts a mapping for a declared list field instead of raising `PartialInputError` (C05)                                            |
| 06/AC02 | ✗      | `src/betwixt/betwixt.py:114-128` suppresses implicit seeds whenever an explicit map targets the destination, even when that map is incomplete (C06)                  |
| 06/AC03 | ✓      | `src/betwixt/betwixt.py:140-171`; `test_partial_operations_are_sparse_and_path_aware`                                                                                |
| 06/AC04 | ✗      | `_nested()` has no compiled shape information and accepts wrong container shapes; `test_nested_mapping_wraps_inner_partial_errors` covers only unknown keys (C05)    |
| 06/AC05 | ✓      | `src/betwixt/betwixt.py:172-177`; `test_partial_preserves_presence_and_skips_defaults`                                                                               |
| 06/AC06 | ⚠      | Context forwarding exists at `src/betwixt/betwixt.py:150-157`; the required partial both-direction derivation matrix is absent                                       |
| 07/AC01 | ✓      | `pyproject.toml:21-28,35-45`; wheel metadata has exactly the three extras and no optional adapter in base requirements                                               |
| 07/AC02 | ✓      | `src/betwixt/adapters/pydantic.py:22-44`; `tests/optional/test_pydantic_adapter.py:22-71`                                                                            |
| 07/AC03 | ⚠      | Alias-only rejection works at `src/betwixt/adapters/pydantic.py:29-41`, but canonical `AliasChoices` is incorrectly rejected (S04)                                   |
| 07/AC04 | ⚠      | `tests/optional/test_pydantic_adapter.py:22-88` covers basic full/partial behavior but not native validation failures or the complete alias matrix                   |
| 08/AC01 | ✓      | `src/betwixt/adapters/sqlalchemy.py:26-35`; `tests/optional/test_sqlalchemy_adapter.py::test_fields_use_python_names_and_normalize_mapped_annotations`               |
| 08/AC02 | ✓      | Mapper-only discovery at `src/betwixt/adapters/sqlalchemy.py:26-35`; optional field and relationship assertions                                                      |
| 08/AC03 | ⚠      | Unloaded read guard exists at `src/betwixt/adapters/sqlalchemy.py:38-42`, but lazy, detached, raise-on-lazy, and partial omission cases are not tested               |
| 08/AC04 | ✓      | Native construction at `src/betwixt/adapters/sqlalchemy.py:44-45`; `test_native_constructor_and_canonical_mapping`                                                   |
| 08/AC05 | ⚠      | `tests/optional/test_sqlalchemy_adapter.py:36-99` lacks nested relationship translations and the required unloaded-state matrix                                      |
| 09/AC01 | ✓      | `examples/user.py:9-18`, `payment.py:9-15`, `order.py:9-19`; `tests/integration/test_examples.py:12-24`                                                              |
| 09/AC02 | ✗      | `examples/sqlalchemy_order.py:1-21` never imports or invokes Betwixt; the SQLAlchemy variant can pass without testing the adapter (C11)                              |
| 09/AC03 | ✓      | `src/betwixt_demo/features/{user,payment,order}.py:6-10`; `src/betwixt_demo/helpers.py:175-314`                                                                      |
| 09/AC04 | ✓      | `src/betwixt_demo/main.py:22-41`; order example includes context, nested values, and a patch at `examples/order.py:11-15`                                            |
| 09/AC05 | ⚠      | `tests/unit/test_demo.py:20-96` checks discovery, selection, and captured failure; optional example integration checks only nonempty output                          |
| 10/AC01 | ✓      | `zensical.toml:1-33`, `docs/source/api-reference.md:1-7`; Zensical build generated the API page                                                                      |
| 10/AC02 | ✓      | Navigation at `zensical.toml:7-19`; `tests/integration/test_docs.py:22-48` checks all named paths                                                                    |
| 10/AC03 | ✗      | Multiple documented fences use undefined objects or wrong field names, for example `why-betwixt.md:17-18`, `cases/order.md:15-16`, and `integrations.md:22-25` (C10) |
| 10/AC04 | ⚠      | Boundary terms appear in `docs/source/behavior.md:12-27` and `integrations.md:14-28`, but canonical names and the four-variant narrative are inconsistent            |
| 10/AC05 | ✓      | `make docs/build` and timed `make docs/serve` passed; `tests/integration/test_docs.py::test_zensical_builds_the_documented_api`                                      |
| 11/AC01 | ✓      | `pyproject.toml:11-57,64-71`; built wheel metadata confirms Python range, extras, and 100% project threshold                                                         |
| 11/AC02 | ✓      | `quality.yml:7-56` has 3 x 4 matrix cells and failure-safe 14-day JUnit/coverage uploads                                                                             |
| 11/AC03 | ⚠      | Current boundary job passes, but the canonical plan command fails and the workflow substitutes a narrower command at `quality.yml:64-72` (C01)                       |
| 11/AC04 | ✓      | `release-verification.yml:3-48` exposes four outputs; `deploy.yml:4-35` is tag-only and gates publication on all outputs                                             |
| 11/AC05 | ⚠      | `docs.yml:4-42` has the merge guard, merge-commit checkout, and environment, but no named docs gate or `betwixt-site` artifact consumption (S02)                     |
| 12/AC01 | ✓      | Independent isolated runs passed all 12 Python/variant cells with 100% line coverage; corrected no-extras job passed 32/1                                            |
| 12/AC02 | ⚠      | All named commands and `uv build` pass, but an installed `betwixt[demo]` console-script smoke fails because the built package is incomplete (C02)                    |
| 12/AC03 | ✗      | Line coverage is 100%, but required subclass, nested, partial, optional-adapter, and real-example behavior is untested or incorrect (C03-C07, C11-C12)               |
| 12/AC04 | ✓      | `git diff --check` passed; generated `docs/site` and `dist` are ignored and no out-of-scope committed path was found                                                 |


## Scope Verification

| File                                                           | Justification                                | Status |
| -------------------------------------------------------------- | -------------------------------------------- | ------ |
| `src/betwixt/__init__.py`                                      | Tasks 01, 03, and 04 public exports          | ✓      |
| `src/betwixt/betwixt.py`                                       | Tasks 01, 03, 04, 05, and 06 engine          | ✗      |
| `src/betwixt/errors.py`                                        | Tasks 01 and 06 error types                  | ✓      |
| `src/betwixt/types.py`                                         | Task 01 adapter protocol                     | ✓      |
| `src/betwixt/refs.py`                                          | Task 01 typed references                     | ✓      |
| `src/betwixt/declaration.py`                                   | Task 01 declaration record export            | ✓      |
| `src/betwixt/adapters/__init__.py`                             | Task 01 adapter exports                      | ✓      |
| `src/betwixt/adapters/base.py`                                 | Task 01 optional lookup                      | ✓      |
| `src/betwixt/adapters/dataclass.py`                            | Tasks 01 and 02 dataclass boundary           | ✓      |
| `src/betwixt/adapters/registry.py`                             | Task 01 registry                             | ✓      |
| `src/betwixt/annotations.py`                                   | Task 02 annotation grammar                   | ✗      |
| `src/betwixt/constructs.py`                                    | Task 03 construct factories                  | ✗      |
| `src/betwixt/compiler.py`                                      | Tasks 03 and 04 callable validation          | ✓      |
| `src/betwixt/engine.py`                                        | Task 04 engine module surface                | ✓      |
| `src/betwixt/nested.py`                                        | Task 05 nested module surface                | ⚠      |
| `src/betwixt/partial.py`                                       | Task 06 partial module surface               | ⚠      |
| `src/betwixt/adapters/pydantic.py`                             | Task 07 Pydantic adapter                     | ⚠      |
| `src/betwixt/adapters/sqlalchemy.py`                           | Task 08 SQLAlchemy adapter                   | ⚠      |
| `src/betwixt/version.py`                                       | Journal continuation version changes         | ✓      |
| `src/betwixt/explain.py`                                       | Task 03 explanation export                   | ✓      |
| `examples/__init__.py`                                         | Task 09 importable examples                  | ⚠      |
| `examples/fixtures.py`                                         | Task 09 shared fixtures                      | ✓      |
| `examples/user.py`                                             | Task 09 User example                         | ✓      |
| `examples/payment.py`                                          | Task 09 Payment example                      | ✓      |
| `examples/order.py`                                            | Task 09 Order example                        | ✓      |
| `examples/pydantic_user.py`                                    | Task 09 optional User example                | ✓      |
| `examples/sqlalchemy_order.py`                                 | Task 09 SQLAlchemy example                   | ✗      |
| `examples/sqlalchemy_user.py`                                  | Task 09 combined User example                | ✓      |
| `src/betwixt_demo/features/__init__.py`                        | Task 09 feature package                      | ✓      |
| `src/betwixt_demo/features/user.py`                            | Task 09 User feature                         | ✓      |
| `src/betwixt_demo/features/payment.py`                         | Task 09 Payment feature                      | ✓      |
| `src/betwixt_demo/features/order.py`                           | Task 09 Order feature                        | ✓      |
| `src/betwixt_demo/example_loader.py`                           | Task 09 example loading                      | ✗      |
| `src/betwixt_demo/main.py`                                     | Task 09 CLI                                  | ✓      |
| `src/betwixt_demo/helpers.py`                                  | Task 09 Rich presentation                    | ✓      |
| `examples/README.md`                                           | Task 09 variant commands                     | ⚠      |
| `tests/integration/test_examples.py`                           | Task 09 executable examples                  | ⚠      |
| `tests/integration/test_no_extras.py`                          | Task 07 and 08 package boundary              | ✓      |
| `tests/integration/test_docs.py`                               | Task 10 docs build and content               | ⚠      |
| `tests/integration/test_project_config.py`                     | Task 10 and 11 config assertions             | ⚠      |
| `tests/integration/conftest.py`                                | Journal continuation isolated fallback       | ✓      |
| `tests/integration/steps/main_steps.py`                        | Journal continuation BDD step                | ✓      |
| `tests/unit/test_demo.py`                                      | Task 09 demo test matrix                     | ⚠      |
| `tests/unit/test_main.py`                                      | Journal continuation existing CLI tests      | ✓      |
| `tests/unit/test_betwixt_core.py`                              | Tasks 01-06 continuation tests               | ⚠      |
| `tests/unit/test_core_contract.py`                             | Tasks 01-06 contract tests                   | ⚠      |
| `tests/unit/test_core_coverage.py`                             | Tasks 01-06 reachability tests               | ⚠      |
| `tests/unit/test_tasks_01_06_exhaustive.py`                    | Tasks 01-06 exhaustive tests                 | ⚠      |
| `tests/optional/test_pydantic_adapter.py`                      | Task 07 optional tests                       | ⚠      |
| `tests/optional/test_sqlalchemy_adapter.py`                    | Task 08 optional tests                       | ⚠      |
| `zensical.toml`                                                | Task 10 authoritative site config            | ✓      |
| `docs/source/index.md`                                         | Task 10 home page                            | ✓      |
| `docs/source/quickstart.md`                                    | Task 10 quickstart                           | ✓      |
| `docs/source/why-betwixt.md`                                   | Task 10 narrative                            | ✗      |
| `docs/source/concepts.md`                                      | Task 10 concepts                             | ✗      |
| `docs/source/behavior.md`                                      | Task 10 behavior                             | ✗      |
| `docs/source/cases/user.md`                                    | Task 10 User case                            | ✗      |
| `docs/source/cases/payment.md`                                 | Task 10 Payment case                         | ✗      |
| `docs/source/cases/order.md`                                   | Task 10 Order case                           | ✗      |
| `docs/source/integrations.md`                                  | Task 10 integrations                         | ✗      |
| `docs/source/comparison.md`                                    | Task 10 comparison                           | ✗      |
| `docs/source/limits.md`                                        | Task 10 limits                               | ✗      |
| `docs/source/api-reference.md`                                 | Task 10 generated API page                   | ⚠      |
| `docs/source/delivery.md`                                      | Task 10 delivery page                        | ✓      |
| `docs/source/reference.md`                                     | Task 10 reference page                       | ⚠      |
| `docs/mkdocs.yaml`                                             | Task 10 MkDocs removal                       | ✓      |
| `Makefile`                                                     | Tasks 10 and 11 build and QA targets         | ✓      |
| `pyproject.toml`                                               | Tasks 07, 08, and 11 packaging/configuration | ⚠      |
| `uv.lock`                                                      | Tasks 07, 08, and 11 locked dependencies     | ✓      |
| `README.md`                                                    | Task 11 project documentation                | ✓      |
| `CONTRIBUTING.md`                                              | Task 11 project documentation                | ✓      |
| `.github/workflows/quality.yml`                                | Task 11 matrix and quality gates             | ⚠      |
| `.github/workflows/release-verification.yml`                   | Task 11 reusable release gate                | ✓      |
| `.github/workflows/main.yml`                                   | Task 11 quality caller                       | ✓      |
| `.github/workflows/deploy.yml`                                 | Task 11 tag deployment                       | ✓      |
| `.github/workflows/docs.yml`                                   | Task 11 merged-PR docs deployment            | ⚠      |
| `.artifacts/20260812--build-betwixt/implementation-journal.md` | Task 12 execution record                     | ✓      |


## Prior Review Resolution

- **C01** ✓ Fully resolved. The exact Python 3.12 base command now passes after a clean isolated sync. The current
  variant documentation and quality workflow consistently select a per-cell `UV_PROJECT_ENVIRONMENT` and use `uv run
  --no-sync`; the original no-`--no-sync` command also passed once its matching environment was established.


## Findings

### Summary

| Finding | Title                                                                   | Outcome |
| ------- | ----------------------------------------------------------------------- | ------- |
| C01     | Documented no-extras gate still fails after package installation        |         |
| C02     | Built distributions omit the demo entry point and examples              |         |
| C03     | Accepted source subclasses are rejected by implicit compatibility       |         |
| C04     | Nested directional callables are stored but never executed              |         |
| C05     | Partial nested operations accept wrong container shapes                 |         |
| C06     | Incomplete explicit partial maps erase valid implicit seeds             |         |
| C07     | Nested fixed and variadic tuples are treated as compatible              |         |
| C08     | Global implicit suppression is absent from explanations                 |         |
| C09     | Unmapped-field diagnostics omit required contract context               |         |
| C10     | Documentation fences are not runnable and contradict the fixtures       |         |
| C11     | The SQLAlchemy example does not exercise Betwixt                        |         |
| C12     | 100% line coverage masks missing required behavior tests                |         |
| C13     | Documentation deployment has no named site gate or artifact handoff     |         |
| S01     | Pydantic canonical `AliasChoices` is incorrectly rejected               |         |
| S02     | Generated API omits every construct factory                             |         |
| S03     | Release builds leave `uv-build` unbounded                               |         |
| S04     | Optional adapter tests do not cover the approved native boundary matrix |         |


### Critical

#### C01: Documented no-extras gate still fails after package installation


#### Where

`implementation-plan.md:99-113` and the no-extras command copied by the plan. The current substitute is
`.github/workflows/quality.yml:64-72`.


#### Issue

The exact documented command installs the local wheel and then asks coverage to measure `src/betwixt/...` module names.
The process imports the installed modules under `betwixt...`, so coverage collects no data and exits with a 0% failure.
The
workflow's `PYTHONPATH=src` command is a different command and selects five named unit files instead of the documented
complete `tests/unit` path.


#### Impact

The canonical no-extras gate is not executable. The passing 32-test workflow substitute does not prove that the
documented
package-boundary command or its complete core test scope works, so the 100% report and release evidence are not
reproducible from the plan.


#### Fix

Make one no-extras command authoritative. Use importable `betwixt...` coverage selectors with an explicit source
checkout
path, or run the installed package without `src/...` selectors. Preserve the complete core test set, both report files,
and the 100% threshold, then use that same command in the plan and workflow.


#### Outcome


----

#### C02: Built distributions omit the demo entry point and examples


#### Where

`pyproject.toml:30-31`, `src/betwixt_demo/example_loader.py:9-21`, and the `uv build` wheel and source-distribution file
inventories.


#### Issue

Both built artifacts contain `betwixt/` only. They contain neither `betwixt_demo` nor `examples`, even though the wheel
advertises `betwixt-demo = "betwixt_demo.main:main"`. An isolated install smoke of `betwixt[demo]` failed immediately:

```text
Traceback (most recent call last):
  File ".../bin/betwixt-demo", line 4, in <module>
    from betwixt_demo.main import main
ModuleNotFoundError: No module named 'betwixt_demo'
```

Even if the demo package were included alone, `example_loader.py` searches the installed file's parent directories for a
repository `examples` directory, which does not exist in a normal installation.


#### Impact

The release package's advertised console script cannot start. Release verification currently uses an editable checkout
and
therefore misses the broken wheel and sdist boundary.


#### Fix

Configure the build to include the demo package and the example modules it loads, or make the installed demo independent
of
repository-only files. Add a wheel and sdist install smoke that runs the console script in a directory outside the
checkout.


#### Outcome


----

#### C03: Accepted source subclasses are rejected by implicit compatibility


#### Where

`src/betwixt/annotations.py:41-56`, especially the plain-class path after both `get_origin()` calls return `None`.


#### Issue

The compatibility function only attempts `issubclass()` when the origins differ. Two ordinary classes have equal `None`
origins, so a source subclass is returned as incompatible. An independent reproduction printed `compatible subclass:
False` and then raised `UnmappedFieldError` for a required destination field when translating a child instance.


#### Impact

The accepted-subclass rule in Task 02 and design AC17 fails. Compatible same-name fields disappear from implicit
mappings,
causing otherwise valid translations to fail or require unnecessary explicit declarations.


#### Fix

Handle plain class annotations before the generic-origin branch and return the approved `issubclass(source,
destination)`
result with safe `TypeError` handling. Add a positive subclass test, including the nested grammar path.


#### Outcome


----

#### C04: Nested directional callables are stored but never executed


#### Where

`src/betwixt/constructs.py:56-69`, `src/betwixt/betwixt.py:148-157`, and `src/betwixt/betwixt.py:282-307`.


#### Issue

Nested factories require `rightward` and/or `leftward`, and the declaration validator checks their signatures. Runtime
code
instead selects the inner mapping operation directly. A nested `rightward` callable that deliberately raised an
assertion
was never called; translation succeeded through the inner mapping.


#### Impact

The public nested declaration contract silently discards user behavior. Direction-specific nested transforms cannot run,
and the required independent-callable behavior is not real despite passing signature and derivation tests.


#### Fix

Define and implement the nested callable invocation contract in the designated direction, preserving the inner `via`
mapping and context semantics. Add both-direction tests that change the value and tests that fail if the declared
callable
is skipped.


#### Outcome


----

#### C05: Partial nested operations accept wrong container shapes


#### Where

`src/betwixt/betwixt.py:282-300`.


#### Issue

`_nested()` has no compiled outer annotation shape. For a field declared as `list[Leaf]`, a partial value such as
`{"value": 1}` is treated as a scalar inner patch because its key happens to be an inner field name. The operation
returns `{"values": {"value": 1}}` instead of raising `PartialInputError` for the list/dict shape mismatch.


#### Impact

Malformed untrusted partial input crosses the boundary with the wrong shape. Consumers receive patches that do not match
the destination annotation, and nested path validation is unreliable.


#### Fix

Compile and retain the nested shape for each declaration. Validate scalar, optional, list, tuple, dictionary, and set
containers before traversal; never infer a scalar patch from an arbitrary mapping. Ensure empty containers make no inner
call.


#### Outcome


----

#### C06: Incomplete explicit partial maps erase valid implicit seeds


#### Where

`src/betwixt/betwixt.py:114-128`.


#### Issue

`explicit_names` removes every destination targeted by a map or nested declaration before partial implicit seeding. A
map
from `(value, other)` to `value` therefore suppresses the compatible `value` seed even when a partial input contains
only
`value` and cannot run the explicit producer. The observed results were `{}` for `{"value": 7}` and `{"value": 9}` only
after `other` was supplied.


#### Impact

Partial updates lose caller-provided compatible fields solely because an unavailable explicit producer exists. This
violates
the sparse precedence rule and can silently drop fields from update patches.


#### Fix

Seed compatible present implicit fields first. Apply a successful explicit producer in declaration order as an
overwrite;
an explicit producer that lacks required source keys must contribute nothing without deleting the seed.


#### Outcome


----

#### C07: Nested fixed and variadic tuples are treated as compatible


#### Where

`src/betwixt/annotations.py:98-109`; the contradictory assertions are in `tests/unit/test_core_coverage.py:147-148`.


#### Issue

`nested_compatible()` explicitly compares a variadic tuple against each fixed element and returns true. The approved
nested
grammar says fixed and variadic tuples do not match. A declared `tuple[Leaf, ...]` to `tuple[Leaf, Leaf]` mapping
accepted a
three-element source and returned a three-element destination tuple.


#### Impact

Declaration-time shape validation permits an output that violates the destination's fixed arity. The dataclass boundary
does not enforce annotations at runtime, so the mismatch escapes as apparently valid data.


#### Fix

Reject exactly one variadic/fixed tuple pair in `nested_compatible()` while retaining recursive checks for two variadic
or two
fixed tuples. Replace the current positive mismatch tests with rejection and runtime declaration tests.


#### Outcome


----

#### C08: Global implicit suppression is absent from explanations


#### Where

`src/betwixt/betwixt.py:119-128` applies global suppression, but `_explain()` at `src/betwixt/betwixt.py:224-245` never
checks `self.disable_implicit_mapping`.


#### Issue

For a mapping with `disable_implicit_mapping = True` and a compatible `value` field, `explain_rightward()` reports
`('value', 'implicit', None)`. Runtime translation correctly omits the value and raises `UnmappedFieldError`.


#### Impact

The required troubleshooting report lies about the producer that is active. Callers cannot distinguish global
suppression
from an active implicit mapping, defeating the explanation and remedy contract.


#### Fix

Report compatible fields as `omitted` with an explicit global-suppression reason before considering compatibility. Keep
the
per-field reason distinct and add a global suppression explanation test in both directions.


#### Outcome


----

#### C09: Unmapped-field diagnostics omit required contract context


#### Where

`src/betwixt/betwixt.py:174-177`.


#### Issue

The raised message contains only the direction, destination field, destination type, and generic remedies. It omits the
source type, relevant same-name source field, normalized source/destination annotations, omission reason, and an
explicit
`explain_rightward()` or `explain_leftward()` pointer required by the plan.


#### Impact

Required-field failures are not actionable enough to diagnose incompatible or suppressed same-name candidates. This
fails
Task 04 AC05 and the design's UnmappedFieldError contract even though tests assert only that an exception is raised.


#### Fix

Build the error from the direction-specific explanation entry and include both type names, canonical field names,
normalized annotations, omission reason, explanation method, and the explicit/default remedies. Assert the complete
message.


#### Outcome


----

#### C10: Documentation fences are not runnable and contradict the fixtures


#### Where

`docs/source/why-betwixt.md:17-18`, `behavior.md:9-23`, `cases/user.md:17-20`, `cases/payment.md:14-16`,
`cases/order.md:14-16`, `integrations.md:22-25`, `comparison.md:8-9`, and `limits.md:8-9`.


#### Issue

The fences use undefined `mapping`, `left`, `source`, `user_mapping`, `payment`, `order`, and `orm_user` objects.
Several
also use field names absent from the real fixtures: the User mapping has canonical `email` rather than `email_address`,
the
Payment fixture has `cents` rather than `amount`, and the Order fixture has `items` rather than `lines`. The docs build
test
checks for fence delimiters and phrases, not execution or narrative consistency.


#### Impact

The site promises runnable examples and a coherent User, Payment, and Order narrative but sends readers into NameError
and
invalid-key failures. The documentation cannot serve as a reliable public contract or onboarding path.


#### Fix

Use complete snippets that import and construct the shared fixtures, or link directly to executable example functions
and
label genuinely illustrative fragments. Correct every canonical field name and add an integration check that executes
the
documented snippets or validates their referenced symbols.


#### Outcome


----

#### C11: The SQLAlchemy example does not exercise Betwixt


#### Where

`examples/sqlalchemy_order.py:1-21` and `tests/integration/test_examples.py:27-33`.


#### Issue

The SQLAlchemy-only example defines an ORM class, constructs it, and prints an f-string. It never imports `Betwixt`,
creates
a mapping, performs translation, or exercises canonical adapter field access. Its integration test asserts only that
stdout
is nonempty and lacks the word `Session`.


#### Impact

The SQLAlchemy variant can pass while the required native adapter example path is absent. Task 09 AC02 and the release
matrix's SQLAlchemy example gate do not verify the product behavior they claim to verify.


#### Fix

Replace the construction-only script with a real mapped source/destination Betwixt translation using canonical Python
attributes and native construction. Assert deterministic translated fields in the integration test, and keep the
no-session
boundary explicit.


#### Outcome


----

#### C12: 100% line coverage masks missing required behavior tests


#### Where

Core tests in `tests/unit/test_betwixt_core.py`, `test_core_contract.py`, `test_core_coverage.py`, and
`test_tasks_01_06_exhaustive.py`; optional tests in `tests/optional/test_pydantic_adapter.py:22-88` and
`tests/optional/test_sqlalchemy_adapter.py:36-99`; example assertions in `tests/integration/test_examples.py:27-33`.


#### Issue

The 100% line result is achieved with direct reachability tests and does not cover several approved behaviors:
post-declaration
registry snapshot immutability, positive subclass compatibility, global explanation suppression, fixed/variadic
rejection,
nested callable execution, malformed nested container shapes, partial explicit-map availability, the complete context
matrix,
Pydantic native validation failures, SQLAlchemy lazy/detached/raise-on-lazy relationship behavior, nested relationship
translation, or semantic SQLAlchemy example output.


#### Impact

Line coverage reports 100% while multiple acceptance criteria remain incorrect or unproved. The current suite can
certify a
release with a large portion of the declared contract missing, as the failures above demonstrate.


#### Fix

Add behavior assertions for every listed matrix row and boundary, including both directions and negative cases. Keep the
100% measured-code threshold and local pragma justifications; do not use reachability-only tests or broaden exclusions
as a
replacement for contract coverage.


#### Outcome


----

#### C13: Documentation deployment has no named site gate or artifact handoff


#### Where

`.github/workflows/quality.yml:106-119` builds/uploads `betwixt-site`, while `.github/workflows/docs.yml:11-42` rebuilds
`docs/site` and publishes that directory directly.


#### Issue

The merged-PR deployment workflow does not consume the `betwixt-site` artifact or depend on a separate docs gate. It
performs
its own build and immediately publishes the local directory in the same job. The repository environment and merge guard
are
present, but the named artifact and gate required by Task 11 AC05 are not connected to deployment.


#### Impact

The published site is not the output of the named CI docs gate, and the workflow has no independently addressable
deployment
check for branch protection or release evidence.


#### Fix

Create an explicit docs verification job that builds and validates the site, uploads `betwixt-site`, and make the
guarded
deployment job depend on that gate and download only that artifact. Retain the merge-commit checkout and
`github-pages` environment.


#### Outcome


### Significant

#### S01: Pydantic canonical `AliasChoices` is incorrectly rejected


#### Where

`src/betwixt/adapters/pydantic.py:29-41`.


#### Issue

The adapter rejects every non-string-equal `validation_alias` when `populate_by_name` is false. A Pydantic field
declared
with `AliasChoices("wire_value", "value")` accepts canonical `value`, but `PydanticAdapter.construct({"value": 1})`
raises
the unsupported-configuration error anyway.


#### Impact

A valid native Pydantic validation configuration cannot be used through Betwixt, contrary to the rule that canonical
input
should be passed to native validation whenever the model accepts it.


#### Fix

Inspect Pydantic's validation-alias types and accept a canonical field when it is one of the choices. Retain rejection
for
alias-only paths that truly reject the canonical name, and add the case to the alias matrix.


#### Outcome


----

#### S02: Generated API omits every construct factory


#### Where

`docs/source/api-reference.md:3-7`, `src/betwixt/constructs.py:28-89`, and the generated
`docs/site/api-reference/index.html`.


#### Issue

The active `::: betwixt` directive generates `Betwixt`, errors, adapters, `MappingExplanation`, and `field_refs`, but
none of
the 15 construct factory names. The factory functions have no docstrings and the current docs test checks only `Betwixt`
and
`field_refs`.


#### Impact

The public API reference claims to document constructs but omits the declarations that make the mapping API usable. The
generated page is not a complete representation of the public surface.


#### Fix

Document each public factory and configure mkdocstrings to include the public construct members, or add explicit
generated
API directives for the construct module. Extend the docs test to assert all 15 names and their signatures.


#### Outcome


----

#### S03: Release builds leave `uv-build` unbounded


#### Where

`pyproject.toml:96-98`.


#### Issue

`uv build` warns that `build_system.requires = ["uv-build>=0.1.0"]` has no upper bound and that a future breaking
release
can break the source distribution.


#### Impact

A future build can produce or fail to install an incompatible source distribution even with the lockfile unchanged. The
release gate currently records the warning but does not prevent this reproducibility failure.


#### Fix

Pin `uv-build` to a tested compatible upper bound and regenerate the lockfile, then keep package build and isolated
install
smokes in the release gate.


#### Outcome


----

#### S04: Optional adapter tests do not cover the approved native boundary matrix


#### Where

`tests/optional/test_pydantic_adapter.py:22-88` and `tests/optional/test_sqlalchemy_adapter.py:36-99`.


#### Issue

The Pydantic suite covers basic fields, one alias rejection, and one coercion case, but not native validation failures,
combined paths, or all validation-alias forms. The SQLAlchemy suite covers mapper names and one unloaded relationship,
but
not full/partial nested relationship translation, detached or `lazy="raise"` states, loader-proof counters, or
requiredness
rows for Python and server defaults.


#### Impact

The optional adapter acceptance matrix is materially untested. Passing normal development jobs and 100% line coverage do
not
establish the native ownership, loading, or persistence boundaries promised by Tasks 07 and 08.


#### Fix

Add the plan's full Pydantic alias/native-error matrix and SQLAlchemy in-memory mapped relationship matrix, including
full and
partial operations, detached and raise-on-lazy cases, requiredness rows, and exact/MRO overrides. Keep the no-extras
test
separate from optional imports.


#### Outcome


## Skills Applied

- `review-implementation-execution`: global fallback


## Decision

**BLOCKED - CHANGES REQUIRED**

C01-C13 must be resolved before approval. The exact documented no-extras quality gate fails, and independent inspection
found
additional incorrect API semantics, an unusable built console script, incomplete examples, and incomplete delivery
evidence.
