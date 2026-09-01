# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the design and implementation plans against `implementation-review--23.md`, with particular
attention to the no-extras coverage scope, exception ownership, coverage exclusions, and earlier contracts.

**Iteration 24**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```

The approved design plan cross-checked for alignment is:

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/design-plan.md
```


## Overview

The review found one Critical finding. The plans now preserve exception propagation and state the 100% measured-code
threshold with local pragma-only exclusions and nearby justification, but the no-extras command still does not execute
the complete core test scope.

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--23.md` C01 ✗: The command adds `tests/unit`, but its `-m absent_extra` selector still
  deselects those tests because the plan says only `tests/integration/test_no_extras.py` is marked `absent_extra`.
  The command also measures `src/betwixt` without defining a source scope limited to core modules.
- `implementation-review--23.md` S01 ✓: Task 04 now forbids catching, wrapping, or re-raising user-callable,
  derivation, field-access, set-insertion, and native construction or validation exceptions, and preserves their
  original type, cause, and traceback.
- Earlier clean review contracts remain present in the active design and implementation plans.


## Findings

### Summary

| Finding ID | Title                                                    | Outcome |
| ---------- | -------------------------------------------------------- | ------- |
| C01        | No-extras command still excludes the complete core suite |         |


### Critical

#### C01: No-extras command still excludes the complete core suite

##### Where

Project Commands, “Verify the package without optional extras,” line 104; Task 07 notes, lines 562–566; Task 11 AC03,
lines 731–738; and the corresponding design requirements in AC30, lines 466–476.


##### Issue

The no-extras command passes `tests/unit` but also applies `-m absent_extra`. The implementation plan explicitly says
to mark only `tests/integration/test_no_extras.py` as `absent_extra`, so pytest deselects the unit tests. The command
therefore runs the boundary test rather than the complete core suite it claims to cover. It also measures
`src/betwixt` as a whole without defining whether optional adapter modules are part of the no-extras measured scope;
the plan provides no way for a dependency-free job to execute dependency-dependent adapter lines while retaining the
100% threshold.


##### Impact

The no-extras job cannot substantiate the required 100% core coverage or the retained coverage report. It either fails
because unexecuted source remains measured, or an executor weakens the threshold or adds a broad omission, violating
the design's 100% measured-code and local-exclusion contract. Task 11 AC03 remains unsatisfied, so the Critical
finding from the prior review is not resolved.


##### Suggestion

Make the no-extras command select both the boundary and core unit tests, for example by removing the marker selector
from this path-scoped command or by using `-m "unit or absent_extra"` after ensuring the core tests carry the `unit`
marker. Define an explicit core-only coverage source scope, or document how every line in `src/betwixt` is executable
without optional dependencies. Keep `--cov-fail-under=100`, `--junitxml=.junit.xml`, and
`--cov-report=xml:.coverage.xml`; retain the workflow uploads of both reports with failure-safe 14-day retention. Any
unavoidable exclusions must remain local `# pragma: no cover` lines with nearby justification comments.


##### Outcome

Accepted and applied: the isolated no-extras command now selects the boundary test by path together with the complete core unit suite, so its 100% measured-code gate is meaningful.

----

## Notes

The exception contract is unchanged: design AC23 and implementation Task 04 require Betwixt-owned errors only for the
specified validation boundaries and require user, derivation, field-access, set-insertion, and native construction or
validation exceptions to propagate unchanged.

Both active plans require 100% coverage on measured code and allow only local `# pragma: no cover` exclusions with
nearby justification comments. The implementation plan also repeats that requirement in the partial-operation,
packaging/CI, and cross-variant acceptance criteria.

The earlier construct taxonomy, sole public `Betwixt` class, full and partial semantics, context and nested traversal,
adapter precedence and native boundaries, optional dependency split, documentation structure, examples and CLI paths,
twelve-job matrix, report retention, lockfile, Makefile, and tag-only or merged-main release gates remain explicit.
The plans do explicitly configure both no-extras report files, but the test-selection defect above prevents the job from
proving the promised core coverage.
