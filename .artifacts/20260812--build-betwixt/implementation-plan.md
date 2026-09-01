# Implementation Plan: Betwixt core mapping layer, integrations, documentation, and delivery

This plan turns the approved Betwixt design into an executable sequence of code, test, documentation, example, and
delivery changes. It keeps the core distribution dataclass-only, isolates Pydantic and SQLAlchemy behind separate
extras,
and makes every acceptance criterion observable through focused tests or repository commands.


## Goal

Build the public `Betwixt` declaration API, typed `field_refs`, deterministic construct engine, full and partial
operations,
diagnostics, adapter registry, and native dataclass boundary in `src/betwixt`. Add native Pydantic v2 and SQLAlchemy 2.x
adapters without changing the core import path or taking ownership of validation, loading, or persistence.

Replace the MkDocs skeleton with a Zensical site, executable User, Payment, and Order examples, and a Typer/Rich demo.
Update packaging, the Makefile, and GitHub Actions for Python 3.12, 3.13, and 3.14 across exactly four dependency
variants. Follow the conventions in the [dusktreader Makefile examples](https://github.com/dusktreader/Makefile):
grouped
section banners, shortcut targets, `target/subtarget` naming, help comments, `.ONESHELL`, `.PHONY`, the standard color
table, hidden guard/confirmation targets, and the shared `help` printer. Require 100% coverage on measured code, retain
CI artifacts for 14 days, publish packages only from validated pushed version tags, and deploy documentation only after
qualifying merged pull requests to `main`.


## Project Commands

### Install the development environment

Prerequisites:

- `uv` with Python 3.12, 3.13, and 3.14 available
- Repository root at `/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt`

Command:

```shell
uv sync --locked --all-groups --extra demo
```

Expected Output:

The locked development environment is synchronized and the package is installed in editable mode.


### Run the complete local quality gate

Command:

```shell
make qa/full
```

Expected Output:

Pytest, the 100% measured-code coverage threshold, Ruff, ty, and typos pass with no errors.


### Run focused unit tests

Command:

```shell
uv run pytest -o addopts="" -m unit tests/unit
```

Expected Output:

All selected core unit tests pass.


### Run focused integration tests

Command:

```shell
uv run pytest -o addopts="" -m integration tests/integration
```

Expected Output:

All selected integration tests pass.


### Run the development variant on Python 3.12

Command:

```shell
uv sync --locked --python 3.12 --all-groups --extra demo && uv run --python 3.12 pytest -m "not absent_extra" tests && uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py && uv run --python 3.12 betwixt-demo --non-interactive
```

Expected Output:

All development tests, all base examples, and the all-feature CLI smoke pass. The separate no-extras boundary command
below verifies package behavior without optional dependencies.


### Verify the package without optional extras

Command:

```shell
make qa/test/no-extras
```

Expected Output:

Run this command from the repository root. The Makefile recipe fresh-builds and installs the wheel without extras in a
temporary environment, installs only the test runner dependencies, and measures every dependency-free core module by its
installed import name. The no-extras suite exercises both missing-adapter assertions and writes both `.junit.xml` and
`.coverage.xml` at 100% coverage. Core Betwixt import succeeds while declaring either optional side raises the
actionable
missing-optional-dependency error.


### Run the Pydantic package variant on Python 3.13

Command:

```shell
uv sync --locked --python 3.13 --all-groups --extra demo --extra pydantic && uv run --python 3.13 pytest -m "not absent_extra" tests && uv run --python 3.13 python examples/user.py && uv run --python 3.13 python examples/payment.py && uv run --python 3.13 python examples/order.py && uv run --python 3.13 python examples/pydantic_user.py && uv run --python 3.13 betwixt-demo --non-interactive
```

Expected Output:

All development tests, Pydantic examples, and the non-interactive CLI smoke pass with the Pydantic package extra
selected.


### Run the SQLAlchemy package variant on Python 3.14

Command:

```shell
uv sync --locked --python 3.14 --all-groups --extra demo --extra sqlalchemy && uv run --python 3.14 pytest -m "not absent_extra" tests && uv run --python 3.14 python examples/user.py && uv run --python 3.14 python examples/payment.py && uv run --python 3.14 python examples/order.py && uv run --python 3.14 python examples/sqlalchemy_order.py && uv run --python 3.14 betwixt-demo --non-interactive
```

Expected Output:

All development tests, SQLAlchemy examples, and the non-interactive CLI smoke pass with the SQLAlchemy package extra
selected.


### Run the combined package variant

Command:

```shell
uv sync --locked --python 3.12 --all-groups --extra demo --extra pydantic --extra sqlalchemy && uv run --python 3.12 pytest -m "not absent_extra" tests && uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py && uv run --python 3.12 python examples/pydantic_user.py && uv run --python 3.12 python examples/sqlalchemy_order.py && uv run --python 3.12 python examples/sqlalchemy_user.py && uv run --python 3.12 betwixt-demo --non-interactive
```

Expected Output:

All development tests, combined examples, and the non-interactive CLI smoke pass with both package extras selected.


### Build the documentation

Command:

```shell
make docs/build
```

Expected Output:

Zensical writes the complete site and generated API page to `docs/site`.


### Serve the documentation

Command:

```shell
make docs/serve
```

Expected Output:

The Zensical development server serves `docs/site` at `http://localhost:10000`.


### Run the interactive demo

Command:

```shell
uv run --extra demo betwixt-demo
```

Expected Output:

The interactive default remains unchanged: Rich displays the selected feature(s), source, captured output, and
continuation prompts.


### Run the non-interactive demo smoke

Command:

```shell
uv run --extra demo betwixt-demo --non-interactive
```

Expected Output:

The command runs `user`, `payment`, and `order` and exits 0 without prompting.


### Run the named non-interactive demo smoke

Command:

```shell
uv run --extra demo betwixt-demo --feature user --non-interactive
```

Expected Output:

Only `user` runs, and the command exits 0 without prompting.


### Verify the non-interactive demo failure path

Command:

```shell
uv run --extra demo betwixt-demo --feature does-not-exist --non-interactive
```

Expected Output:

Typer reports an invalid feature and exits nonzero without prompting.


### Build package distributions

Command:

```shell
uv build
```

Expected Output:

`dist/` contains one source distribution and one wheel with exactly the three optional extras `demo`, `pydantic`, and
`sqlalchemy`, four supported installation variants (base, Pydantic, SQLAlchemy, and combined), and Python
`>=3.12,<3.15` metadata.

----

## Project Standards

- [`pyproject.toml`](/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/pyproject.toml)
- [`Makefile`](/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/Makefile)
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
- [`CONDUCT.md`](../../CONDUCT.md)
- [Approved design plan](design-plan.md)
- [Global Markdown guidance](/home/dusktreader/.agents/instructions/markdown.md)
- [Global Python guidance](/home/dusktreader/.agents/instructions/python.md)


## Relevant Skills

- `execute-implementation-plan` at `/home/dusktreader/.agents/skills/execute-implementation-plan/SKILL.md`
- `execute-implementation-task` at `/home/dusktreader/.agents/skills/execute-implementation-task/SKILL.md`
- `review-implementation-execution` at `/home/dusktreader/.agents/skills/review-implementation-execution/SKILL.md`


## Execution

### 01: Establish the public package and adapter contracts

Define the public declaration, errors, adapter protocol, registry, and field-reference primitives before implementing
translation behavior. Keep imports from `betwixt` free of optional dependencies.


#### Acceptance Criteria

1. AC01: The foundational package exports `Betwixt`, `field_refs`, public declaration and adapter protocol types, the
    registry entry points, and Betwixt-owned declaration and adapter errors; construct and operation exports are staged
    in Tasks 03 and 04.
2. AC02: The registry resolves exact registrations, nearest registered MRO bases, and built-in families in that order;
   duplicate registration fails unless replacement is requested.
3. AC03: Each concrete `Betwixt` mapping snapshots resolved adapters when its declaration is built, and later registry
   changes affect only new declarations.
4. AC04: `field_refs(left, right)` returns typed left and right proxies; missing fields, wrong-side references, and
    invalid `disable_implicit_mapping` values fail during declaration. Disable-anchor validation is completed in Task
    03.
5. AC05: Core imports succeed when neither optional package is installed, while optional-side declarations raise an
   actionable missing-extra error.


#### Steps

1. Write failing unit tests in `tests/unit/test_refs.py`, `test_registry.py`, `test_declaration.py`, and
   `test_errors.py` for the five criteria.
2. Run `uv run pytest -o addopts="" -m unit tests/unit/test_refs.py tests/unit/test_registry.py
   tests/unit/test_declaration.py
   tests/unit/test_errors.py` and confirm the tests fail for missing implementation.
3. Add `src/betwixt/errors.py`, `src/betwixt/types.py`, `src/betwixt/refs.py`, `src/betwixt/adapters/base.py`,
   `src/betwixt/adapters/registry.py`, `src/betwixt/declaration.py`, and `src/betwixt/betwixt.py`. Define the sole
   public `Betwixt` class in `betwixt.py`; later tasks extend that same class and no alternate class or legacy module is
   created.
4. Export only the approved public surface from `src/betwixt/__init__.py`, including the `Betwixt` class imported from
   `betwixt.py`; use lazy optional-adapter detection rather than importing Pydantic or SQLAlchemy at module import time.
5. Run the focused tests again, then run `uv run ruff check src/betwixt tests/unit` and `uv run ty check src/betwixt`.


#### Technical Notes


#### Declaration representation

Store ordered immutable declaration records with canonical source and destination field names, direction, callable,
references, and declaration kind. Capture adapters, resolved annotations, and class-level implicit settings once while
building the concrete `Betwixt` mapping.


### 02: Implement annotation normalization and dataclass adapters

Implement the type grammar and native dataclass boundary used by implicit mapping and nested declarations.


#### Acceptance Criteria

1. AC01: Normalization strips `Annotated`, resolves forward references against the declaring type, and treats `Any` as
   compatible without using it to infer a nested element type.
2. AC02: Compatibility handles equal types, accepted subclasses, matching generic origins, recursive generic arguments,
   optionality, lists, variadic and fixed tuples, dictionaries, and sets exactly as approved.
3. AC03: Unsupported custom containers, unresolved references, root wrappers, and discriminated unions require explicit
   callables and produce actionable declaration errors when used as nested grammar.
4. AC04: Dataclass fields expose required/default/optional metadata, read canonical attributes, and construct
   destinations
   through normal dataclass construction without Betwixt coercion.


#### Steps

1. Write the compatibility matrix in `tests/unit/test_annotations.py` and dataclass adapter tests in
   `tests/unit/test_dataclass_adapter.py`, including native constructor and `__post_init__` failures.
2. Run those tests and confirm failure.
3. Add `src/betwixt/annotations.py`, `src/betwixt/adapters/dataclass.py`, and `src/betwixt/adapters/__init__.py`.
4. Register dataclasses as built-in support and validate nested `via` side types against the normalized grammar.
5. Run the focused tests, then `uv run pytest -o addopts="" -m unit tests/unit/test_annotations.py
     tests/unit/test_dataclass_adapter.py`.
6. Run `uv run ruff check src/betwixt tests/unit` and `uv run ty check src/betwixt`.


### 03: Implement implicit mapping, explicit field constructs, and diagnostics

Build the declaration compiler and explanation engine for same-name mapping, suppression, maps, reductions, projections,
and defaults. Preserve class-body order and later-write-wins behavior.


#### Acceptance Criteria

1. AC01: `map_pairwise` and `nested_pairwise` require independently supplied `rightward` and `leftward`; directional map
   and nested constructs use only their declared direction and never synthesize inverses.
2. AC02: `betwixt` exports exactly these 15 constructs: `map_pairwise`, `map_rightward`, `map_leftward`,
    `reduce_rightward`, `reduce_leftward`, `project_rightward`, `project_leftward`, `nested_pairwise`,
    `nested_rightward`,
    `nested_leftward`, `default_rightward`, `default_leftward`, `disable_implicit_pairwise`,
    `disable_implicit_rightward`, and `disable_implicit_leftward`. `reduce_pairwise`, `project_pairwise`, and
    `default_pairwise` are absent.
3. AC03: Same-name implicit candidates require normalized compatibility, honor global and per-field suppression, and
   lose
   to explicit declarations without preventing an explicit write.
4. AC04: `explain_rightward()` and `explain_leftward()` are declaration-time only and return ordered entries with the
   required statuses, canonical names, annotation descriptions, and omission reasons.
5. AC05: Invalid callable direction, missing refs, mismatched disable anchors (a disable declaration must name equal
    canonical fields on both sides), and invalid default factories raise Betwixt-owned declaration errors with
    actionable
    messages. Ordinary duplicate destinations are valid and use declaration-order last-write-wins.


#### Steps

1. Write failing tests in `tests/unit/test_constructs.py`, `test_implicit_mapping.py`, and `test_explanations.py` for
   every construct family and suppression/report status. Cover missing-direction failures and independent direction
   execution for both `map_pairwise` and `nested_pairwise`.
2. Run the tests and confirm they fail.
3. Add `src/betwixt/constructs.py`, `src/betwixt/compiler.py`, and `src/betwixt/explain.py`; compile declarations into
   direction-specific producer records without calling user functions.
4. Add `MappingExplanation` and entry/status types to the public exports.
5. Run focused tests with `uv run pytest -o addopts="" -m unit tests/unit/test_constructs.py
   tests/unit/test_implicit_mapping.py
     tests/unit/test_explanations.py`, then inspect reports for stable declaration order and omission reasons.
6. Run `uv run ruff check src/betwixt tests/unit` and `uv run ty check src/betwixt`.


### 04: Implement the full translation engine

Execute compiled producers against instances, propagate context, enforce callable signatures, apply defaults, and raise
unmapped errors before native construction.


#### Acceptance Criteria

1. AC01: `rightward` and `leftward` have the signatures `rightward(value, *, context=None, defaults=None)` and
   `leftward(value, *, context=None, defaults=None)`, reject positional `context` and `defaults` with `TypeError`,
   pass values in reference order, and recognize a
   final keyword-only parameter named `ctx`. The engine passes context only as `ctx=...`; a positional-only or
   positional-or-keyword `ctx` parameter is an invalid declaration.
2. AC02: Maps run only when all source fields exist; reductions receive complete source instances; projections return
   complete destination instances whose readable fields seed the result.
3. AC03: Declarations execute in class-body order, later writes replace earlier writes, and projections participate in
   the
   same overlap rule.
4. AC04: Literal defaults and zero-argument factories fill only empty fields; `...` reads the operation `defaults`
   mapping;
   partial operations never use any default.
5. AC05: Missing required destination fields raise `UnmappedFieldError` with direction, types, field, and
    remedy/explanation
    information before destination construction; native destination errors propagate unchanged.
6. AC06: The final public surface exports `rightward`, `leftward`, `rightward_partial`, `leftward_partial`,
    `explain_rightward`, `explain_leftward`, `MappingExplanation`, its public entry/status types, all Task 03 construct
    names, the declaration/adapters types, and Betwixt-owned errors. The three absent pairwise names remain absent.


#### Steps

1. Write failing tests in `tests/unit/test_engine_full.py` for keyword-only public operation arguments, including
   rejection
   of positional `context` and `defaults`, and declaration-time context signature validation across map,
   reduce, project, and nested inner callables in both directions. Accept only a final keyword-only `ctx`, inject it
   only
   as `ctx=...`, reject both positional-only and positional-or-keyword `ctx` before translation, and verify valid calls.
   Also cover callable ordering, overlap, projections, defaults, unmapped fields, unknown or unreadable projected
   fields,
   native constructor errors, and both directions.
2. Run the tests and confirm failure.
3. Add `src/betwixt/engine.py` and public `Betwixt.rightward`, `leftward`, `explain_rightward`, and `explain_leftward`
   methods in `src/betwixt/betwixt.py`. Require projection extraction to reject every unknown or unreadable projected
   field with a Betwixt-owned declaration or adapter error rather than silently discarding it.
4. Implement source reads, producer execution, projection extraction, default resolution, and adapter construction in
   that order. Do not catch, wrap, or re-raise user-callable, derivation, field-access, set-insertion, or native
   construction and validation exceptions. Raise only the specified Betwixt-owned errors before native construction;
   otherwise preserve the original exception type, cause, and traceback.
5. Run the focused tests with `uv run pytest -o addopts="" -m unit tests/unit/test_engine_full.py`, then run
   `uv run ty check src/betwixt`.
6. Run `uv run ruff check src/betwixt tests/unit` and `uv run ty check src/betwixt`.


### 05: Implement nested scalar and container translation

Add recursive nested delegation with directional context derivation and the complete supported container grammar.


#### Acceptance Criteria

1. AC01: Nested scalar, optional, list, variadic tuple, fixed tuple, dictionary, and set values preserve shape and
   recurse
   through the selected inner `Betwixt` mapping.
2. AC02: `context_rightward` and `context_leftward` call `derive(outer_context)` with exactly one positional argument,
   never use `ctx=...`, and run once per outer nested value. Their result is passed to every container element. Both
   directions test positional-only selectors, identity, explicit `None`, omitted derivation, and call counts.
3. AC03: Invalid nested side types and mismatched tuple/container/key shapes fail during declaration; callable and
   derivation exceptions propagate unchanged.
4. AC04: Empty containers make no inner calls, dictionary keys pass through, and unhashable translated set values retain
   the native set insertion error.


#### Steps

1. Write failing tests in `tests/unit/test_nested_full.py` for all shapes, both directions, keyword-only context
   propagation, rejection of both positional `ctx` forms in inner translation callables at declaration time,
   `derive(outer_context)` positional-only selectors, explicit identity and `None`, context counters, optional values,
   empty containers, tuple mismatch, dictionary keys, and set hashability.
2. Run the tests and confirm failure.
3. Add `src/betwixt/nested.py` and implement shape planning at declaration time plus recursive runtime traversal.
4. Integrate nested producers into `src/betwixt/engine.py` without duplicating direct callable signature logic.
5. Run `uv run pytest -o addopts="" -m unit tests/unit/test_nested_full.py` and the complete development test suite.
6. Run `uv run ruff check src/betwixt tests/unit` and `uv run ty check src/betwixt`.


### 06: Implement sparse partial operations

Implement mapping-only input validation and sparse producer behavior for maps, reductions, nested constructs, implicit
fields, projections, and defaults.


#### Acceptance Criteria

1. AC01: `rightward_partial` and `leftward_partial` reject non-mappings, unknown source keys, and malformed nested
   values;
   key presence distinguishes absent from present `None`.
2. AC02: Compatible present implicit fields seed the patch, suppressed/incompatible/absent fields do not, and explicit
   declarations overwrite seeded values in declaration order.
3. AC03: Maps require every referenced key; reductions require every source field and construct a source instance;
   projections and defaults are always skipped.
4. AC04: Nested partial patches recurse through scalar, optional, list, tuple, dictionary, and set shapes, preserve
   paths in
   Betwixt-owned errors, and never normalize a present model instance implicitly.
5. AC05: Partial methods return only `dict[str, Any]` patches and never construct a destination instance.
6. AC06: Partial operations have keyword-only `context`, reject positional context with `TypeError`, pass it unchanged
   to
   direct context-aware producers only as `ctx=...`,
   and call each nested derivation as `derive(outer_context)` with exactly one positional argument, never as `ctx=...`,
   once per nested field invocation. The result is reused for all elements. Both directions cover keyword-only `ctx`,
   positional-only derivation selectors, omitted and explicit-`None` derivations, identity derivation, and per-boundary
   call counts.


#### Steps

1. Write failing tests in `tests/unit/test_engine_partial.py` covering the sparse/complete matrix from the design plan,
   including `None`, all nested containers, reduction availability, projection/default skips, input ownership, direct
   keyword-only `ctx=...` injection, rejection of positional `ctx`, and partial nested derivations using exactly
   `derive(outer_context)` with positional-only selectors, omitted and explicit-`None` derivations, identity derivation,
   and per-boundary call counts in both directions.
2. Run the tests and confirm failure.
3. Add `src/betwixt/partial.py` and shared input/path validation helpers in `src/betwixt/errors.py`.
4. Add the two public partial methods and integrate partial producer selection with the compiled declarations.
5. Run the partial tests with `uv run pytest -o addopts="" -m unit tests/unit/test_engine_partial.py`, then run the full
   development test suite. Verify coverage is 100% on measured code. Add local `# pragma: no cover` only to structural,
   trivial, or intentionally untestable lines, with a nearby justification comment.
6. Run `uv run ruff check src/betwixt tests/unit` and `uv run ty check src/betwixt`.


### 07: Add Pydantic v2 native support

Add Pydantic v2 as a package-optional dependency through the `pydantic` extra and add its adapter while preserving
canonical Betwixt names and Pydantic's native validation/default/coercion boundary. Add Pydantic as a regular
development
dependency so normal development and CI test environments can run adapter tests without conditional collection. Keep
Pydantic absent from the base package's required dependencies so consumers install it only when selecting the extra.


#### Acceptance Criteria

1. AC01: `pydantic` is declared only in the optional `pydantic` extra as `pydantic>=2.7,<3`; it is also a regular
   development dependency for the test environment and remains absent from the base package's required dependencies.
   Importing core without it still works, and declaring a Pydantic side without the extra raises the
   missing-optional-dependency error.
2. AC02: The adapter exposes canonical field names, reads canonical source attributes, passes canonical destination
   names,
   and respects Pydantic validation, defaults, and coercion.
3. AC03: Serialization, validation, and field aliases remain Pydantic concerns; alias-only destinations that reject
   canonical input produce an actionable unsupported configuration error.
4. AC04: Combined and Pydantic-only tests cover representative full/partial translations and native validation failures.

The alias test matrix must include: field-name input; a source `validation_alias`; a source `serialization_alias`; field
references and partial keys that remain canonical; Pydantic defaults and native coercion at destination construction;
and
an alias-only or validation-alias-only destination that rejects canonical input and raises the actionable unsupported
configuration error.


#### Steps

1. Add `tests/optional/test_pydantic_adapter.py` and `tests/integration/test_no_extras.py`. Use the regular development
   dependencies for adapter tests. Mark only `test_no_extras.py` as `absent_extra`; run it in an isolated package
   environment and confirm the missing-extra behavior for both adapters.
2. Add `pydantic>=2.7,<3` to both the `pydantic` package extra and the regular development dependency group in
   `pyproject.toml`, then add
   `src/betwixt/adapters/pydantic.py` with lazy import and native `model_validate`/constructor behavior.
3. Add canonical alias and validation tests, then run:
    `uv run --extra pydantic pytest -o addopts="" tests/optional/test_pydantic_adapter.py`.
4. Run the complete development suite with both adapter dependencies installed and confirm no core import regression.
5. Run `uv run --extra pydantic ruff check src/betwixt tests/optional` and `uv run --extra pydantic ty check
   src/betwixt`.

The regular development environment installs both optional adapter packages as development dependencies, so adapter
tests
use ordinary imports without optional-package collection markers. Mark `tests/integration/test_no_extras.py` as
`absent_extra` for reporting, but select it by path in the `make qa/test/no-extras` recipe together with `tests/unit`.
Register
only
`unit`, `integration`, and `absent_extra` in `pyproject.toml`, and keep test collection import-safe in
`tests/conftest.py`.


### 08: Add SQLAlchemy native support

Add SQLAlchemy 2.x as a package-optional dependency through the `sqlalchemy` extra and add its mapped declarative
adapter, including canonical mapped names, relationships, loaded-state checks, and ordinary native construction without
session or persistence integration. Add SQLAlchemy as a regular development dependency so normal development and CI test
environments can run adapter tests without conditional collection. Keep SQLAlchemy absent from the base package's
required
dependencies so consumers install it only when selecting the extra.


#### Acceptance Criteria

1. AC01: `SQLAlchemy>=2.0,<3` is declared in the optional `sqlalchemy` extra and as a regular development dependency for
   the test environment, while remaining absent from the base package's required dependencies. Without the extra,
   declaring a SQLAlchemy side raises the missing-optional-dependency error. With the extra, mapped scalar and supported
   relationship attributes are discovered from the mapper only, using Python attribute names rather than column/key/join
   names.
2. AC02: Mapped `Mapped[T]` annotations normalize into the existing scalar/container nested grammar; unmapped fields,
   hybrid properties, association proxies, and unsupported descriptors are not exposed by the native adapter.
3. AC03: Reading an unloaded relationship raises a Betwixt-owned unloaded-field error in full translation and omits the
   field in partial translation without triggering a loader. Cover lazy, detached, and raise-on-lazy configurations.
4. AC04: Full translation calls the destination mapped class with canonical keyword values and leaves defaults,
   instrumentation, validation, session, flush, commit, refresh, and persistence to SQLAlchemy.
5. AC05: `tests/optional/test_sqlalchemy_adapter.py` covers scalar/relationship translations, database-name divergence,
   loaded checks, native construction, exact/MRO overrides, and absent-extra behavior.


#### Steps

1. Write failing tests with in-memory mapped classes in `tests/optional/test_sqlalchemy_adapter.py`. Define
   `Parent`/`Child` fixtures with a database column named differently from the Python attribute, and a destination
   fixture
   for each requiredness row: nullable, `Optional[...]`, Python constructor default, relationship `default`, and server
   default. Assert that the first four are constructible without a Betwixt value and the server-default row is rejected
   before construction. Cover the missing-extra boundary through the isolated `tests/integration/test_no_extras.py`
   test.
2. Build lazy, detached, and `lazy="raise"` relationship cases. For each case assert
    `"children" in inspect(obj).unloaded` before translation, install a loader-proof counter/event, and assert the
    relationship remains in `inspect(obj).unloaded` afterward. Assert full translation raises the owned unloaded-field
    error and partial translation omits the field from the patch.
3. Add `SQLAlchemy>=2.0,<3` to both the `sqlalchemy` package extra and the regular development dependency group in
   `pyproject.toml`, then implement `src/betwixt/adapters/sqlalchemy.py` with lazy imports, mapper field
    discovery, `Mapped[T]` resolution, `inspect(obj).unloaded` checks, and native keyword construction.
4. Add exact-class and nearest-MRO registration tests to `tests/unit/test_registry.py` and verify custom adapters
    override
    built-in support.
5. Run `uv run --extra sqlalchemy pytest -o addopts="" tests/optional/test_sqlalchemy_adapter.py` and the combined
   adapter tests.
6. Run `uv run --extra sqlalchemy ruff check src/betwixt tests/optional` and `uv run --extra sqlalchemy ty check
   src/betwixt`.


### 09: Build the executable examples and interactive demo

Replace placeholder examples with deterministic fixtures shared by documentation, tests, and the Typer/Rich presentation
layer.


#### Acceptance Criteria

1. AC01: `examples/user.py`, `examples/payment.py`, and `examples/order.py` run in the base environment with fixed
   inputs,
   outputs, context, nested values, and partial patches.
2. AC02: `examples/pydantic_user.py`, `examples/sqlalchemy_order.py`, and `examples/sqlalchemy_user.py` exercise their
   required dependency variants; the combined User path matches the blog scenario and uses no persistence.
3. AC03: `src/betwixt_demo/features/user.py`, `payment.py`, and `order.py` expose independently callable `demo_*`
   functions; `helpers.py` presents explanation, source, captured output, and continuation through Rich.
4. AC04: `src/betwixt_demo/main.py` supports one named feature or all by default, and all three scenarios include
   runtime
   context, nested values, and a patch translation.
5. AC05: `tests/integration/test_examples.py` and `tests/unit/test_demo.py` assert deterministic output, selection,
   discovery, captured failures, and nonzero unexpected-result behavior.


#### Steps

1. Write smoke tests and expected-output fixtures in `tests/integration/test_examples.py`, then run them to establish
   the
   missing-example failures.
2. Add shared case fixtures in `examples/fixtures.py`; implement the six example scripts and update `examples/README.md`
   with the exact four variant commands.
3. Refactor the existing `src/betwixt_demo/basic.py` into feature modules, retain the established `helpers.py` pattern,
   and update `src/betwixt_demo/main.py` and the `Feature` enum.
4. Run all four example commands, `uv run --extra demo pytest -o addopts="" tests/unit/test_demo.py`, and the core CLI
   smoke path in
    each
    dependency variant.
5. Add `--non-interactive` to the Typer command while preserving the current interactive default and prompt sequence.
    In non-interactive mode skip both `Confirm` prompts, run all selected demos, and return nonzero for an unknown
    feature
    or captured unexpected result. Test all-feature selection, `--feature user`, and the unknown-feature failure.
6. Run `uv run --extra demo ruff check src/betwixt_demo examples tests` and `uv run --extra demo ty check
   src/betwixt_demo src/betwixt examples`.


### 10: Replace MkDocs with the Zensical documentation site

Make Zensical authoritative and document the approved contract, blog-distilled narrative, runnable examples,
diagnostics,
and adapter boundaries.


#### Acceptance Criteria

1. AC01: Root `zensical.toml` defines Zensical `0.0.13`, the Material theme variant, `docs/source` as the source
   directory, `docs/site` as the output directory, `dev_addr = "localhost:10000"`, the named navigation below, and the
   `mkdocstrings` Python API plugin with `::: betwixt` configured on `docs/source/api-reference.md`. Its Python handler
   uses `paths = ["src"]` and options `heading_level = 3`, `show_root_heading = true`, `separate_signature = true`,
   `show_signature_annotations = true`, `show_source = false`, and `docstring_style = "google"`. `docs/mkdocs.yaml`
   and MkDocs-only dependencies/targets are removed or explicitly deprecated and unused.
2. AC02: Navigation names these exact pages: `index.md`, `quickstart.md`, `why-betwixt.md`, `concepts.md`,
     `behavior.md`, `cases/user.md`, `cases/payment.md`, `cases/order.md`, `integrations.md`,
    `comparison.md`, `limits.md`, `api-reference.md`, and `delivery.md`.
3. AC03: Every conceptual page contains a short runnable example, and the User, Payment, and Order narrative is
   distilled
   from the approved blog/design scenario with shared fixtures.
4. AC04: Documentation states exact partial semantics, `explain_*`/`UnmappedFieldError` troubleshooting, canonical ORM
   names versus database names, loaded relationships, unsupported descriptors, no session/persistence behavior, and the
   four dependency commands.
5. AC05: `make docs/build` succeeds, produces a representative generated API page, and `make docs/serve` starts
   Zensical.


#### Steps

1. Add a docs build smoke test in `tests/integration/test_docs.py` that checks `zensical.toml`, the navigation pages,
    `docs/site/index.html`, and `docs/site/api-reference/index.html`; assert that every page has a runnable code fence,
    the User/Payment/Order case pages contain their named narrative, and the required pages contain partial semantics,
    `explain_*`/`UnmappedFieldError`, canonical ORM names, loaded-relationship/no-persistence boundaries, and all four
    variant commands. Run it and confirm the initial failure.
2. Add root `zensical.toml` with `[project]` settings for `site_name`, `docs_dir = "docs/source"`,
   `site_dir = "docs/site"`, `dev_addr = "localhost:10000"`, and the exact navigation above. Configure
   `[project.theme]` with `variant = "classic"` and the Python handler under
   `[project.plugins.mkdocstrings.handlers.python]` with `paths = ["src"]` and an `options` table containing
   `heading_level = 3`, `show_root_heading = true`, `separate_signature = true`,
   `show_signature_annotations = true`, `show_source = false`, and `docstring_style = "google"`. Add the named pages and
   keep code snippets synchronized with `examples/`. Keep singleton conceptual sections as flat files (`concepts.md`,
   `behavior.md`, and `integrations.md`); retain directories only for sections with multiple pages, such as `cases/`.
3. Update `pyproject.toml` to pin `zensical==0.0.13` and `mkdocstrings[python]>=0.29,<0.30`; update `Makefile`
    `docs/build`/`docs/serve` to invoke `zensical build --clean` and `zensical serve` only. Remove `docs/mkdocs.yaml`
    and MkDocs references from workflows, `README.md`, `CONTRIBUTING.md`, and `examples/README.md`.
4. Run `make docs/build`, inspect links and the generated API page, then run `uv run pytest -o addopts=""
     tests/integration/test_docs.py`.


### 11: Update packaging, Make targets, and CI/CD gates

Encode the dependency variants, supported Python range, quality requirements, artifact retention, and guarded
package/site
publishing in repository configuration.


#### Acceptance Criteria

1. AC01: `pyproject.toml` declares Python `>=3.12,<3.15`, optional extras `demo`, `pydantic`, and `sqlalchemy`, regular
   development dependencies `pydantic>=2.7,<3` and `SQLAlchemy>=2.0,<3`, Zensical dependencies, and a 100% coverage
   threshold on measured code. The adapter packages remain absent from the base package's required dependencies.
2. AC02: `.github/workflows/quality.yml` expands exactly 12 matrix test jobs from Python 3.12, 3.13, and 3.14 crossed
     with base, `pydantic`, `sqlalchemy`, and combined variants. Each normal job uses the regular development dependency
     set, runs the complete test suite, and uploads
    `junit-{python}-{variant}` from `.junit.xml` and `coverage-{python}-{variant}` from `.coverage.xml` with
    `if: ${{ !cancelled() }}` and `retention-days: 14`.
3. AC03: `quality.yml` also has a named `no-extras-boundary` job that installs the package without optional extras and
    runs `make qa/test/no-extras`, including the complete core test suite; it uploads both `.junit.xml`
   and `.coverage.xml` with `if: ${{ !cancelled() }}` and 14-day retention. The normal matrix and boundary jobs require
   100% coverage on measured code; structural, trivial, or intentionally untestable lines may use only local
   `# pragma: no cover` exclusions with nearby justification comments. It also has a named
     `package-build` job that runs `uv build` and uploads `dist/*.whl` as
    `betwixt-wheel` and `dist/*.tar.gz` as `betwixt-sdist`, each with 14-day retention; a named `docs-build` job uploads
    `docs/site` as `betwixt-site` with 14-day retention. Pull requests and branch pushes require all 12 matrix jobs,
    package-build, docs-build, and the quality/example/SQLAlchemy/CLI checks.
4. AC04: `.github/workflows/release-verification.yml` is a reusable workflow that accepts `workflow_call`, runs the
     same quality workflow and exposes `quality`, `examples`, `docs`, and `distributions` success outputs. `deploy.yml`
     triggers automatically only on pushed tags matching `v*.*.*`, then publishes the package only when every output is
     successful. It has no manual-dispatch or branch-push trigger.
5. AC05: `docs.yml` listens only for `pull_request` events with `types: [closed]` and paths `docs/source/**` and
    `zensical.toml`. Its deployment job runs only when `github.event.pull_request.merged == true` and
    `github.event.pull_request.base.ref == 'main'`; it builds the resulting main revision and publishes only
    `betwixt-site` through the repository deployment environment after the docs gate passes. This supports merge-commit,
    squash, and rebase merges while excluding direct main pushes, feature-branch pushes, tag pushes, and unrelated
    merges.


#### Steps

1. Add configuration assertions to `tests/integration/test_project_config.py`; run them against the current files and
   confirm expected failures.
2. Update `pyproject.toml` and the Makefile for extras, Zensical, coverage/report commands, four-variant targets, and
   exact local commands without weakening the 100% measured-code threshold. Preserve the referenced Makefile style: use
   section
   banners,
   shortcut targets such as `qa: qa/full` and `docs: docs/serve`, slash-separated subtargets, inline `##` help comments,
   `.ONESHELL`, `.PHONY`, the standard color variables/help printer, and hidden `_guard_*` or `_confirm` helpers where
   applicable.
3. Run `uv lock --upgrade`, commit the resulting `uv.lock`, and update `CONTRIBUTING.md`, `README.md`, and
    `examples/README.md` to describe Zensical and the exact variant commands. CI must run `uv sync --locked` and fail
    on a stale lockfile before any test job.
4. Add `.github/workflows/quality.yml` with the exact 12-job matrix, the command-table commands, named
   no-extras-boundary/package-build/docs-build jobs, artifact paths/names above, and `if: ${{ !cancelled() }}` uploads.
    The no-extras job runs `make qa/test/no-extras` and uploads both reports with the same retention policy. Add
   `.github/workflows/main.yml` as a caller on pull requests and branch pushes.
5. Add `.github/workflows/release-verification.yml` as the reusable gate. Configure `deploy.yml` for pushed `v*.*.*`
   tags only, with no `workflow_dispatch`. Configure `docs.yml` for `pull_request` `closed` events with the exact docs
   paths and guard deployment with `merged == true` and base branch `main`. Keep package and site publication separate
   and exclude all other event paths.
6. Run `uv build`, `make qa/full`, `make qa/test/no-extras`, `make docs/build`, and the configuration test. Inspect
   workflow YAML for exactly twelve
   matrix combinations and no push-to-publish path.


### 12: Complete cross-variant verification and release rehearsal

Run the full acceptance matrix, fix integration gaps, and leave the repository in a state that an executor can release
without undocumented steps.


#### Acceptance Criteria

1. AC01: Python 3.12, 3.13, and 3.14 pass the base, Pydantic, SQLAlchemy, and combined test commands with 100% coverage
   on measured code. Structural, trivial, and intentionally untestable code uses local `# pragma: no cover` exclusions
   with nearby justification comments.
2. AC02: Both optional-adapter examples, all base examples, the core CLI in all variants, docs build, package build,
   lint,
   typo checks, and type checks pass.
3. AC03: Tests cover every approved construct family, both directions, implicit controls, explanations, all full/partial
   semantics, adapter snapshots and precedence, loaded relationship failures, and native construction boundaries.
4. AC04: No product code, generated site, distribution, or unrelated artifact is committed outside the approved scope;
   `git diff --check` is clean.


#### Steps

1. Run `uv python install 3.12 3.13 3.14` and execute the exact four variant command-table commands under each
    interpreter; CI must copy these commands verbatim rather than use an implicit "where required" extra.
2. Run `make qa/full`, `make docs/build`, the exact named/all-feature non-interactive demo commands, and `uv build`.
3. Run `git diff --check` and review changed paths against the design plan and this implementation plan.
4. Record any failure as a code or test correction, rerun the smallest failing command, then rerun the complete gate.


## Unknowns

No unresolved implementation questions remain. Package deployment is automatic after a validated pushed `v*.*.*` tag;
documentation deployment is automatic for a closed, merged pull request targeting `main` whose changed paths include
`docs/source/**` or `zensical.toml`. Test merge-commit, squash, and rebase-compatible closed pull requests, unrelated
merges, direct main pushes, feature-branch pushes, and version-tag pushes; assert that only qualifying merged docs
changes
publish the site.


## Technical Notes

### Public module ownership

Keep public imports in `src/betwixt/__init__.py` and place implementation details behind `betwixt.py`, `declaration.py`,
`compiler.py`, `engine.py`, `partial.py`, `nested.py`, and `adapters/`. The adapter registry must snapshot adapter
objects,
not merely type names, so later registration cannot mutate an existing concrete `Betwixt` mapping.


### Error ownership

Use Betwixt-owned errors for declaration validation, adapter lookup/registration, malformed partial inputs, missing
required defaults, unloaded SQLAlchemy fields, and unmapped destination fields. Let user callables, derivations, native
dataclass/Pydantic/SQLAlchemy construction, field access, and set insertion retain their original exception types and
causes.


### Affected repository files

The execution may add or update `uv.lock`, `CONTRIBUTING.md`, `README.md`, `examples/README.md`, `pyproject.toml`,
`Makefile`, root `zensical.toml`, the named `docs/source` pages, `tests/conftest.py`, optional tests, and the workflow
files `main.yml`, `quality.yml`, `release-verification.yml`, `deploy.yml`, and `docs.yml`. It removes or deprecates
`docs/mkdocs.yaml` and every stale MkDocs reference. It must not modify this review artifact or any generated
`docs/site` or `dist/` output in source control.


### Dependency matrix

| Variant    | Package extras selected | Development dependencies available | Required checks                                      |
| ---------- | ----------------------- | ---------------------------------- | ---------------------------------------------------- |
| Base       | none                    | Pydantic, SQLAlchemy               | Core tests, dataclass examples, core CLI             |
| Pydantic   | `pydantic`              | Pydantic, SQLAlchemy               | Core tests, Pydantic adapter/example, core CLI       |
| SQLAlchemy | `sqlalchemy`            | Pydantic, SQLAlchemy               | Core tests, mapped adapter/example, SQLAlchemy tests |
| Combined   | both                    | Pydantic, SQLAlchemy               | All tests, cross-adapter User example, core CLI      |

The matrix is crossed with Python 3.12, 3.13, and 3.14 in CI. Package extras control package metadata and example paths;
regular development dependencies make the complete adapter suite available in every normal job. The separate no-extras
job alone omits both optional packages. No SQLAlchemy test may require a database engine, session, network, or secret.


### Exact CI and final-verification command table

CI and Task 12 must use these commands verbatim. Each row is one of exactly twelve matrix jobs; `demo` is installed in
every job solely so the required CLI smoke is available. Every normal job uses the regular development dependency set
and runs the complete test suite; the separate no-extras job runs the isolated boundary test.

| Python | Variant    | Locked sync command                                                                            | Pytest selector                                           | Required example command                                                                                                                                                                                                                                                                                                           | CLI smoke command                                     |
| ------ | ---------- | ---------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------- |
| 3.12   | base       | `uv sync --locked --python 3.12 --all-groups --extra demo`                                     | `uv run --python 3.12 pytest -m "not absent_extra" tests` | `uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py`                                                                                                                                                                                 | `uv run --python 3.12 betwixt-demo --non-interactive` |
| 3.12   | pydantic   | `uv sync --locked --python 3.12 --all-groups --extra demo --extra pydantic`                    | `uv run --python 3.12 pytest -m "not absent_extra" tests` | `uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py && uv run --python 3.12 python examples/pydantic_user.py`                                                                                                                        | `uv run --python 3.12 betwixt-demo --non-interactive` |
| 3.12   | sqlalchemy | `uv sync --locked --python 3.12 --all-groups --extra demo --extra sqlalchemy`                  | `uv run --python 3.12 pytest -m "not absent_extra" tests` | `uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py && uv run --python 3.12 python examples/sqlalchemy_order.py`                                                                                                                     | `uv run --python 3.12 betwixt-demo --non-interactive` |
| 3.12   | combined   | `uv sync --locked --python 3.12 --all-groups --extra demo --extra pydantic --extra sqlalchemy` | `uv run --python 3.12 pytest -m "not absent_extra" tests` | `uv run --python 3.12 python examples/user.py && uv run --python 3.12 python examples/payment.py && uv run --python 3.12 python examples/order.py && uv run --python 3.12 python examples/pydantic_user.py && uv run --python 3.12 python examples/sqlalchemy_order.py && uv run --python 3.12 python examples/sqlalchemy_user.py` | `uv run --python 3.12 betwixt-demo --non-interactive` |
| 3.13   | base       | `uv sync --locked --python 3.13 --all-groups --extra demo`                                     | `uv run --python 3.13 pytest -m "not absent_extra" tests` | `uv run --python 3.13 python examples/user.py && uv run --python 3.13 python examples/payment.py && uv run --python 3.13 python examples/order.py`                                                                                                                                                                                 | `uv run --python 3.13 betwixt-demo --non-interactive` |
| 3.13   | pydantic   | `uv sync --locked --python 3.13 --all-groups --extra demo --extra pydantic`                    | `uv run --python 3.13 pytest -m "not absent_extra" tests` | `uv run --python 3.13 python examples/user.py && uv run --python 3.13 python examples/payment.py && uv run --python 3.13 python examples/order.py && uv run --python 3.13 python examples/pydantic_user.py`                                                                                                                        | `uv run --python 3.13 betwixt-demo --non-interactive` |
| 3.13   | sqlalchemy | `uv sync --locked --python 3.13 --all-groups --extra demo --extra sqlalchemy`                  | `uv run --python 3.13 pytest -m "not absent_extra" tests` | `uv run --python 3.13 python examples/user.py && uv run --python 3.13 python examples/payment.py && uv run --python 3.13 python examples/order.py && uv run --python 3.13 python examples/sqlalchemy_order.py`                                                                                                                     | `uv run --python 3.13 betwixt-demo --non-interactive` |
| 3.13   | combined   | `uv sync --locked --python 3.13 --all-groups --extra demo --extra pydantic --extra sqlalchemy` | `uv run --python 3.13 pytest -m "not absent_extra" tests` | `uv run --python 3.13 python examples/user.py && uv run --python 3.13 python examples/payment.py && uv run --python 3.13 python examples/order.py && uv run --python 3.13 python examples/pydantic_user.py && uv run --python 3.13 python examples/sqlalchemy_order.py && uv run --python 3.13 python examples/sqlalchemy_user.py` | `uv run --python 3.13 betwixt-demo --non-interactive` |
| 3.14   | base       | `uv sync --locked --python 3.14 --all-groups --extra demo`                                     | `uv run --python 3.14 pytest -m "not absent_extra" tests` | `uv run --python 3.14 python examples/user.py && uv run --python 3.14 python examples/payment.py && uv run --python 3.14 python examples/order.py`                                                                                                                                                                                 | `uv run --python 3.14 betwixt-demo --non-interactive` |
| 3.14   | pydantic   | `uv sync --locked --python 3.14 --all-groups --extra demo --extra pydantic`                    | `uv run --python 3.14 pytest -m "not absent_extra" tests` | `uv run --python 3.14 python examples/user.py && uv run --python 3.14 python examples/payment.py && uv run --python 3.14 python examples/order.py && uv run --python 3.14 python examples/pydantic_user.py`                                                                                                                        | `uv run --python 3.14 betwixt-demo --non-interactive` |
| 3.14   | sqlalchemy | `uv sync --locked --python 3.14 --all-groups --extra demo --extra sqlalchemy`                  | `uv run --python 3.14 pytest -m "not absent_extra" tests` | `uv run --python 3.14 python examples/user.py && uv run --python 3.14 python examples/payment.py && uv run --python 3.14 python examples/order.py && uv run --python 3.14 python examples/sqlalchemy_order.py`                                                                                                                     | `uv run --python 3.14 betwixt-demo --non-interactive` |
| 3.14   | combined   | `uv sync --locked --python 3.14 --all-groups --extra demo --extra pydantic --extra sqlalchemy` | `uv run --python 3.14 pytest -m "not absent_extra" tests` | `uv run --python 3.14 python examples/user.py && uv run --python 3.14 python examples/payment.py && uv run --python 3.14 python examples/order.py && uv run --python 3.14 python examples/pydantic_user.py && uv run --python 3.14 python examples/sqlalchemy_order.py && uv run --python 3.14 python examples/sqlalchemy_user.py` | `uv run --python 3.14 betwixt-demo --non-interactive` |
