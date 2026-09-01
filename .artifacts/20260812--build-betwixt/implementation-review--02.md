# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the revised implementation plan against implementation-review--01.md, the approved design plan,
the canonical implementation-plan and implementation-review artifact definitions, and repository context.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review verified all 16 findings from implementation-review--01.md. It surfaced no new findings:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✓: Task 01 technical-note subsections now use the required `#####` heading level.
- **C02** ✓: Project Commands now gives each documented command its own `###` subsection and command/output record.
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
- **T01** ✓: Code tasks now include applicable task-level Ruff and `ty` commands, with optional extras named for adapter
  tasks, and the final cross-variant gate remains separate.
- **T02** ✓: The package-build expectation distinguishes the three optional extras from the four supported installation
  variants.


## Findings

### Summary

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |


## Notes

No new structural, acceptance-criteria, task-ordering, scope, standards, skills, or markdown finding warrants carrying
forward. The formatter reports the required `##### Declaration representation` heading as a level-five heading, but the
canonical implementation-plan artifact explicitly requires that level for subsections within task technical notes.
