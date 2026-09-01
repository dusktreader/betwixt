# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 01**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review checked the implementation-plan structure, repository standards, execution order, and coverage of all 30
approved design acceptance criteria. It surfaced findings:

- **Critical**: 2
- **Significant**: 12
- **Trivial**: 2


## Findings

### Summary

| Finding | Title                                                                     | Outcome |
| ------- | ------------------------------------------------------------------------- | ------- |
| C01     | Task technical notes use an invalid heading level                         |         |
| C02     | Project Commands groups multiple commands under one subsection            |         |
| S01     | The public construct count is wrong                                       |         |
| S02     | Duplicate-destination rejection contradicts overlap semantics             |         |
| S03     | Task 01 acceptance criteria depend on later tasks                         |         |
| S04     | The dependency-variant verification commands are not concrete             |         |
| S05     | Optional test collection and variant selection are unspecified            |         |
| S06     | The interactive demo has no documented non-blocking smoke path            |         |
| S07     | SQLAlchemy unloaded-state and requiredness tests lack executable fixtures |         |
| S08     | Pydantic alias behavior lacks a concrete test matrix                      |         |
| S09     | The Zensical site plan does not name its pages or API integration         |         |
| S10     | CI artifact and release-gate topology is incomplete                       |         |
| S11     | Lockfile and stale repository documentation are outside the file plan     |         |
| S12     | `Unknowns` incorrectly claims that no execution decisions remain          |         |
| T01     | Per-task lint and type-check steps are inconsistent                       |         |
| T02     | The package-build expected output confuses extras with variants           |         |


### Critical

#### C01: Task technical notes use an invalid heading level

##### Where

Execution — Task 01 — Technical Notes, approximately line 195.


##### Issue

The `#### Technical Notes` section contains `**Declaration representation**` as a faux subsection heading. The
canonical implementation-plan artifact requires subsections inside task technical notes to use `#####`, not a bold
subject.


##### Impact

The artifact does not conform to its required hierarchy. Consumers that parse task notes by heading level can treat the
declaration representation as ordinary paragraph text.


##### Suggestion

Rewrite `**Declaration representation**` as `##### Declaration representation`. Keep `#### Technical Notes` as the
task-level heading.


##### Outcome


#### C02: Project Commands groups multiple commands under one subsection

##### Where

Project Commands — Run the four dependency variants, approximately lines 81-95, and Build and serve the documentation,
approximately lines 98-109.


##### Issue

The canonical artifact requires one `###` subsection per command. The plan places four example commands in one
subsection and two documentation commands in another, so each command does not have its own prerequisites, command, and
expected-output record.


##### Impact

The command inventory is not structurally verifiable. An executor can run only one variant or only the build half of the
documentation workflow while still appearing to have followed the corresponding subsection.


##### Suggestion

Split the four variant commands into separate `###` subsections and split `make docs/build` and `make docs/serve` into
separate subsections. Give each subsection its own exact command and expected output.


##### Outcome


### Significant

#### S01: The public construct count is wrong

##### Where

Execution — Task 01 — Acceptance Criteria — AC01, approximately line 168.


##### Issue

The approved design enumerates 15 public constructs: the three map, two reduce, two project, three nested, two default,
and three `disable_implicit_*` names. The plan says that `betwixt` exports "all 14 approved construct names" and does
not
enumerate the names in this criterion.


##### Impact

An implementation can omit one public construct, most likely one of the implicit-mapping suppression declarations, while
still satisfying the written count. That would violate design AC03 and leave the public API incompletely tested.


##### Suggestion

Change the count to 15 and list every required export in AC01. Add an explicit assertion that
`reduce_pairwise`, `project_pairwise`, and `default_pairwise` are absent.


##### Outcome


#### S02: Duplicate-destination rejection contradicts overlap semantics

##### Where

Execution — Task 03 — Acceptance Criteria — AC05, approximately line 247, versus Task 04 — AC03, approximately lines
275-277.


##### Issue

Task 03 says duplicate destinations raise a Betwixt-owned declaration error. The approved design AC11 and Task 04 say
declarations may overlap, execute in class-body order, and let the later write win, including projections.


##### Impact

An executor following Task 03 will reject valid declarations that Task 04 is required to execute. This is a direct
contract contradiction, not an implementation detail.


##### Suggestion

Remove "duplicate destinations" from the declaration-error criterion. If only a narrower duplicate is invalid, name that
case precisely and add it to the design-approved overlap rule without rejecting ordinary later-write-wins declarations.


##### Outcome


#### S03: Task 01 acceptance criteria depend on later tasks

##### Where

Execution — Task 01 — AC01 and steps, approximately lines 168-190; construct implementation starts in Task 03 and public
translation methods start in Task 04.


##### Issue

Task 01 requires all public constructs and four operations to be exported, but its steps create only foundational files.
The constructs are not added until Task 03, and `Twixt.rightward`/`leftward` plus the explanation methods are added in
Task 04.


##### Impact

Task 01 cannot meet its own acceptance criteria at its boundary without undocumented placeholder exports and later
replacement. That weakens the promised test-driven sequence and makes the task result ambiguous.


##### Suggestion

Either move the final public-surface AC to the tasks that add each symbol, or explicitly add the required stubs and
their
temporary contract tests in Task 01, with a stated replacement boundary in Tasks 03 and 04.


##### Outcome


#### S04: The dependency-variant verification commands are not concrete

##### Where

Project Commands — Run the four dependency variants, approximately lines 81-95; Task 11 steps, approximately lines
526-535; Task 12 steps, approximately lines 560-565.


##### Issue

The plan gives exact commands for four example scripts, but not for the four test environments under each of Python
3.12, 3.13, and 3.14. Task 12 says to add extras "where required" and Task 11 merely requests explicit install
commands. It does not name the `uv run --python` invocations, test selections, or CLI/example commands for each
variant.


##### Impact

The executor cannot reproduce the twelve-job matrix or prove the AC29 assignment of base, Pydantic-only,
SQLAlchemy-only,
and combined checks. CI may run the same dependency set in every job or silently omit an optional path.


##### Suggestion

Add a variant command table with exact Python selector, extras, install/sync command, pytest selection, required example
commands, and core CLI smoke command for each variant. Use the same commands in the local verification section and the
workflow steps.


##### Outcome


#### S05: Optional test collection and variant selection are unspecified

##### Where

Execution — Tasks 07 and 08, approximately lines 381-424; Project Commands — complete local quality gate, approximately
lines 42-52.


##### Issue

The plan places optional tests under `tests/optional`, while the repository's `pytest` configuration discovers all of
`tests` and `make qa/full` runs `uv run pytest`. "Variant markers" are mentioned, but no marker names, skip/import
strategy, pytest configuration, or per-variant selectors are defined. The absent-extra tests also need to run in an
environment where the corresponding package is genuinely absent.


##### Impact

The base quality command can collect tests that import missing optional packages, or the executor can skip optional
tests
and still report a passing base suite. Both outcomes invalidate the four-variant gate.


##### Suggestion

Define the marker names and registration, the collection rule for each variant, and the absent-extra subprocess
strategy.
Document exact commands that run core tests in every variant plus only the applicable optional tests, while retaining
explicit missing-dependency coverage in the base environment.


##### Outcome


#### S06: The interactive demo has no documented non-blocking smoke path

##### Where

Project Commands — Run the interactive demo, approximately lines 112-123; Execution — Task 09 — AC04 and steps,
approximately lines 441-459; Task 12, approximately lines 549-563.


##### Issue

The existing Typer/Rich demo asks `Confirm` continuation questions. The documented `betwixt-demo` command supplies no
input, and final verification only invokes `betwixt-demo --help`. The plan never defines a deterministic stdin
transcript
or a non-interactive smoke option for the required core CLI path in all four variants.


##### Impact

CI can hang waiting for input and cannot verify all-feature execution, named feature selection, or the required nonzero
unexpected-result behavior. The typerdrive-style presentation contract is therefore not executable as a gate.


##### Suggestion

Document an exact non-blocking smoke invocation, either by specifying the prompt input consumed by the interactive
command
or by adding a non-interactive option that preserves the interactive default. Test named and all-feature selection,
deterministic output, and the nonzero failure path with that invocation.


##### Outcome


#### S07: SQLAlchemy unloaded-state and requiredness tests lack executable fixtures

##### Where

Execution — Task 08 — AC03/AC04 and steps, approximately lines 400-424; Dependency matrix notes, approximately lines
601-602.


##### Issue

The plan requires lazy, detached, and raise-on-lazy unloaded relationship cases, but says the normal path uses no engine
or
session and only vaguely refers to mapper instrumentation. It does not specify how each unloaded state is created, how
the test proves no loader ran, or how the full-error and partial-omission assertions inspect the same object. It also
does
not turn the approved constructibility rules into tests for nullable, optional, Python-defaulted,
relationship-defaulted,
and server-defaulted fields.


##### Impact

The adapter can accidentally trigger lazy loading or treat a server-side default as satisfying pre-construction
requiredness while the tests still appear to cover relationships. Detached and raise-on-lazy behavior can also be
reduced
to unrelated native exceptions instead of the required Betwixt-owned error.


##### Suggestion

Define mapped fixtures for each loader strategy and detached state, assert the relationship is in
`inspect(obj).unloaded`
before translation and remains unaccessed, then assert the full error and partial omission. Add a requiredness matrix
that
explicitly excludes server-side defaults before construction.


##### Outcome


#### S08: Pydantic alias behavior lacks a concrete test matrix

##### Where

Execution — Task 07 — AC02/AC03 and steps, approximately lines 371-389.


##### Issue

The plan says "canonical alias and validation tests" but does not enumerate source aliases, validation aliases,
serialization aliases, canonical patch keys, or the exact alias-only destination failure. The approved design requires
each Pydantic interface to remain native while Betwixt always uses canonical names.


##### Impact

An adapter can pass a single alias example while incorrectly reading a serialization alias, emitting alias patch keys,
or
bypassing native validation for a destination that rejects canonical input.


##### Suggestion

List separate tests for field-name input, source validation and serialization aliases, canonical field references and
partial keys, destination defaults/coercion, and the actionable error for alias-only or validation-alias-only
destinations.


##### Outcome


#### S09: The Zensical site plan does not name its pages or API integration

##### Where

Execution — Task 10 — AC01-AC05 and steps, approximately lines 469-495.


##### Issue

The plan names conceptual categories and directory globs, but not the concrete Markdown files, navigation entries,
output
directory, Zensical package/version, or API-reference integration configuration. The smoke test checks that navigation
and
one generated API page exist, but not that every required page contains the required runnable example, case narrative,
partial contract, adapter boundary, and dependency commands.


##### Impact

An implementation can produce a valid Zensical site with a minimal navigation and one API page while omitting required
AC28 content or using an unsupported API plugin configuration. Documentation can pass the proposed test without teaching
the approved design.


##### Suggestion

List the exact `docs/source` files and navigation tree, identify the Zensical dependency and API integration settings,
define the site output path, and add content assertions or fixture checks for the required case-study, boundary,
troubleshooting, and four-variant command content.


##### Outcome


#### S10: CI artifact and release-gate topology is incomplete

##### Where

Execution — Task 11 — AC02-AC05 and steps, approximately lines 509-535.


##### Issue

The approved design requires a package-build job that uploads source and wheel distributions for 14 days, twelve test
jobs that each upload JUnit and coverage reports after failure, and release workflows that require the completed
quality,
example, distribution, and docs gates. The plan says to run `uv build` and rewrite three workflows, but does not name a
package-build job, artifact-upload actions/names, or a mechanism for a tag/manual deploy workflow to depend on jobs in
the
separate main and docs workflows.


##### Impact

The final workflows may publish without the twelve-job quality result, may not retain the required reports, or may build
distributions without uploading them. A separate workflow cannot enforce another workflow's completion with an implicit
`needs` relationship.


##### Suggestion

Specify the workflow/job topology, including the package-build job, `actions/upload-artifact` paths and 14-day
retention,
the `if: ${{ !cancelled() }}` report uploads, and a reusable workflow or explicit release verification mechanism that
actually gates tag/manual publication on the required jobs.


##### Outcome


#### S11: Lockfile and stale repository documentation are outside the file plan

##### Where

Execution — Tasks 07, 08, and 10-11, approximately lines 385-386, 418-419, and 490-535; Project Standards, approximately
lines 140-149.


##### Issue

The repository contains `uv.lock`, but the plan changes project dependencies and extras without a lockfile update or a
locked-resolution check. The plan also requires MkDocs references to be removed from repository documentation while
naming
`CONTRIBUTING.md` as a governing standard; that file currently says the project uses `mkdocs-material`, yet it is not an
explicit update target.


##### Impact

CI or local sync can resolve a stale dependency graph, and contributors can receive documentation that contradicts the
Zensical-only toolchain. The planned standards and delivered configuration would disagree.


##### Suggestion

Add `uv.lock` and `CONTRIBUTING.md` to the affected-file steps. Specify the lock/update command and a locked CI check,
and
update or explicitly deprecate the MkDocs statement along with any other repository references.


##### Outcome


#### S12: `Unknowns` incorrectly claims that no execution decisions remain

##### Where

Unknowns, approximately lines 568-571.


##### Issue

The section says `None`, but the plan leaves answerable implementation decisions unresolved: the optional-test
collection policy, the non-interactive CLI smoke input, the Zensical API integration and page inventory, and the
cross-workflow release gate are all unspecified in the execution tasks.


##### Impact

Different executors can make incompatible choices while each claims to follow the same plan. This is especially risky
for
the AC27-AC30 delivery and dependency boundaries, where a late choice changes CI behavior rather than internal
structure.


##### Suggestion

Resolve these choices in the relevant tasks and remove them from `Unknowns`, or list each as a specific question with
its
owner, decision, and verification command before execution begins. Do not retain `None` while the task text remains
open.


##### Outcome


### Trivial

#### T01: Per-task lint and type-check steps are inconsistent

##### Where

Execution — Tasks 02, 03, 05-11. Several tasks end after focused tests and omit the lint/type checks required by the
`execute-implementation-plan` and `execute-implementation-task` skills.


##### Issue

Task 01, Task 04, and the final rehearsal mention lint or type checks, but most code tasks do not run them after
implementation. The plan therefore does not consistently follow its declared execution skills.


##### Impact

Type or lint regressions can survive several task boundaries and be discovered only at the final gate, making failures
harder to localize.


##### Suggestion

Add the exact applicable Ruff and `ty` commands after each code task, with the appropriate dependency variant for
optional
adapter tasks. Keep the final cross-variant gate as a separate check.


##### Outcome


#### T02: The package-build expected output confuses extras with variants

##### Where

Project Commands — Build package distributions — Expected Output, approximately line 136.


##### Issue

The plan says the wheel has "the four extras." The design defines four dependency variants, but the package has the
`demo`, `pydantic`, and `sqlalchemy` optional extras; base is a variant, not an extra, and combined is not a separate
extra.


##### Impact

The expected metadata assertion can reject a correct package or encourage an invalid fourth optional dependency name.


##### Suggestion

Change the expected output to three optional extras and four supported installation variants, or state the exact
metadata
keys that `uv build` must contain.


##### Outcome


## Notes

The plan covers the broad implementation surface for design AC01-AC30, including the core engine, both optional
adapters,
Zensical, examples, the Typer/Rich demo, and CI. The findings are concentrated in executable detail and in a few direct
contract regressions rather than a missing feature area. S04-S06 and S10 should be resolved together because the local
variant commands, optional test collection, CLI smoke path, and release gates must describe one coherent CI matrix.
