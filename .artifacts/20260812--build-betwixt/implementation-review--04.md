# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 04**

This re-review checks the implementation plan against implementation-review--03.md, the approved design plan, the
canonical artifact definitions, repository standards, and the requested public naming and module contract.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review rechecked all 16 findings carried into implementation-review--03.md. It found no unresolved prior finding and
identified three new Significant findings:

- **Critical**: 0
- **Significant**: 3
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✓: Task 01 technical-note subsections use the required `#####` heading level.
- **C02** ✓: Project Commands gives each documented command its own `###` subsection and command/output record.
- **S01** ✓: Task 03 AC02 enumerates the exact 15 constructs and names all three forbidden pairwise constructs.
- **S02** ✓: Task 03 permits ordinary duplicate destinations with declaration-order last-write-wins semantics, including
  projections in Task 04.
- **S03** ✓: Task 01 explicitly stages construct exports to Task 03 and operation exports to Task 04.
- **S04** ✓: The technical-notes command table defines all 12 Python/dependency-variant combinations with exact sync,
  pytest, example, and CLI commands, and Tasks 11-12 require those commands verbatim.
- **S05** ✓: Tasks 07-08 define both optional markers, import-safe collection, absent-extra subprocess checks, and the
  base, Pydantic, SQLAlchemy, and combined selectors.
- **S06** ✓: Project Commands and Task 09 define a non-interactive Typer smoke for all features, named selection, and
  invalid selection while preserving the interactive default.
- **S07** ✓: Task 08 defines mapped Parent/Child fixtures, unloaded-state inspection and loader-proof checks, plus the
  nullable, optional, Python-default, relationship-default, and server-default requiredness rows.
- **S08** ✓: Task 07 includes the required field-name, validation-alias, serialization-alias, canonical-reference,
  canonical-partial-key, native-default/coercion, and alias-only failure cases.
- **S09** ✓: Task 10 names the Zensical version, plugin, source/output directories, navigation pages, and generated-page
  and content assertions.
- **S10** ✓: Task 11 specifies the 12-job matrix, report and build artifacts, reusable release verification, separate
  package/site publication, success outputs, and tag/manual-only triggers.
- **S11** ✓: Task 11 explicitly updates `uv.lock`, checks locked synchronization for staleness, and updates
  `CONTRIBUTING.md`, `README.md`, and `examples/README.md` for the Zensical toolchain.
- **S12** ✓: Unknowns now record concrete resolutions for optional collection, demo smoke, documentation, and release
  gating rather than claiming unresolved decisions do not exist.
- **T01** ✓: Code tasks include applicable task-level Ruff and `ty` commands, with optional extras named for adapter
  tasks, and the final cross-variant gate remains separate.
- **T02** ✓: The package-build expectation distinguishes the three optional extras from the four supported installation
  variants.


## Findings

### Summary

| Finding ID | Title                                                       | Outcome |
| ---------- | ----------------------------------------------------------- | ------- |
| S01        | Nested pairwise declarations omit the no-inverse contract   |         |
| S02        | Projection extraction omits unknown and unreadable failures |         |
| S03        | Betwixt class ownership is not assigned at the first task   |         |


### Significant

#### S01: Nested pairwise declarations omit the no-inverse contract

##### Where

Execution — Task 03 — Acceptance Criteria — AC01, approximately lines 331-338; Task 05 — Acceptance Criteria and Steps,
approximately lines 410-432.


##### Issue

The approved design requires `nested_pairwise` to receive independently supplied `rightward` and `leftward` callables
and never synthesize an inverse. Task 03 states that rule only for `map_pairwise` and directional map constructs. Task
05
tests nested shapes and both directions, but does not state or test the declaration rule for `nested_pairwise`.


##### Impact

An implementation can accept one nested callable and derive the other while satisfying the written nested acceptance
criteria. That violates the public construct contract and can make one translation direction behave differently from the
declared API.


##### Suggestion

Extend Task 03 AC01 to state that `nested_pairwise` also requires independently supplied `rightward` and `leftward`
callables and never synthesizes an inverse. Add missing-direction and direction-specific execution tests to
`tests/unit/test_constructs.py` and `tests/unit/test_nested_full.py`.


##### Outcome

Accepted and applied: Task 03 now requires independent `rightward` and `leftward` callables for both `map_pairwise` and `nested_pairwise`, with missing-direction and independent-execution tests.

#### S02: Projection extraction omits unknown and unreadable failures

##### Where

Execution — Task 04 — Acceptance Criteria — AC02 and Steps — Step 4, approximately lines 373-400.


##### Issue

The approved design requires unknown or unreadable fields on a projected destination instance to raise a declaration or
adapter error rather than be silently discarded. The plan says only that projections return complete instances whose
readable fields seed the result and that projection extraction is implemented. It does not define the failure contract
or
require tests for unknown and unreadable projected fields.


##### Impact

The executor can implement projection extraction as a permissive filter. That silently loses projected data and can
allow
a final destination to construct successfully with an incomplete projection while all listed projection tests pass.


##### Suggestion

Add a Task 04 acceptance criterion requiring every field exposed by a projected destination instance to be known and
readable through the destination adapter, with a Betwixt-owned declaration or adapter error for unknown or unreadable
fields. Add tests for both failures and assert that no incomplete projection is silently accepted.


##### Outcome

Accepted and applied: Task 04 now requires projection extraction to reject unknown or unreadable projected fields and adds both failure cases to its tests.

#### S03: Betwixt class ownership is not assigned at the first task

##### Where

Execution — Task 01 — Steps 3-4, approximately lines 277-281; Task 04 — Step 3, approximately lines 395-396; Technical
Notes — Public module ownership, approximately lines 735-740.


##### Issue

Task 01 requires the foundational package to export `Betwixt`, but its file list creates `declaration.py` and does not
create or assign the class to `src/betwixt/betwixt.py`. Task 04 later refers to methods in that module without stating
whether it creates the module, moves the class, or extends the class established in Task 01. The technical note names
the
module but does not resolve this task boundary.


##### Impact

An executor can define the public class in `declaration.py`, create a second class in `betwixt.py`, or defer the export
until Task 04. Any of those choices risks duplicate class identity, unstable imports, or a foundational task that cannot
meet its own acceptance criteria.


##### Suggestion

Make Task 01 create `src/betwixt/betwixt.py` with the sole public `Betwixt` class and re-export that class from
`src/betwixt/__init__.py`. State that later tasks extend the same class in that module and that no alternate class or
legacy module name is created.


##### Outcome

Accepted and applied: Task 01 now creates the sole `Betwixt` class in `src/betwixt/betwixt.py`, re-exports it from `__init__.py`, and requires later tasks to extend that same class without an alternate module or class.

## Notes

An exact-word scan of the implementation plan found no standalone `Twixt` or `twixt` occurrence. Class and identifier
references use `Betwixt`; the implementation module is explicitly `src/betwixt/betwixt.py` at line 396, and the public
module ownership note names `betwixt.py` at line 737. Lowercase `betwixt` occurrences are package paths or package
commands, not alternate class terminology.

The Markdown checker reports the `##### Declaration representation` heading at line 286 as level five. The canonical
implementation-plan artifact requires that level for task technical-note subsections, so this is an intentional
structural exception and not a new finding. It also reports the level-five review field headings required by the
canonical implementation-review artifact; those headings are likewise intentional.
