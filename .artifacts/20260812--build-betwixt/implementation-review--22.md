# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the updated implementation plan against `implementation-review--21.md`, the design plan, and the
requested 100% coverage, documentation, delivery, dependency, Makefile, naming, and contract boundaries.

**Iteration 22**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review found two Significant findings. The active plans contain no stale `85%` threshold, but the no-extras command
explicitly disables the required coverage gate, and focused test commands inherit a whole-project 100% gate without a
scoped-test exception.

- **Critical**: 0
- **Significant**: 2
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--21.md` was clean. Its no-extras portability resolution, documentation layout, deployment
  triggers, optional dependency strategy, Makefile conventions, and earlier contract resolutions remain present.
- `design-review--06.md` was clean. The design still defines the 100% measured-code requirement, local pragma-only
  exclusions with nearby justification, the singleton documentation layout, tag-only package publication, and merged
  pull-request documentation deployment.


## Findings

### Summary

| Finding ID | Title                                                            | Outcome |
| ---------- | ---------------------------------------------------------------- | ------- |
| S01        | No-extras verification disables the required 100% gate           |         |
| S02        | Focused test commands inherit an incompatible whole-project gate |         |


### Significant

#### S01: No-extras verification disables the required 100% gate

##### Where

Project Commands, “Verify the package without optional extras,” line 104; Execution, Task 11 AC03, lines 725-731; the
design plan's AC30 and CI/CD architecture, lines 466-479 and 587-600.


##### Issue

The isolated command measures `src/betwixt` but passes `--cov-fail-under=0`. Task 11 AC03 says that both the normal
matrix
and `no-extras-boundary` require 100% coverage on measured code, and both plans prohibit reducing that threshold. A zero
threshold makes this boundary report-only and contradicts the task criterion.


##### Impact

The boundary job can pass with uncovered measured code while still producing a coverage report. CI therefore does not
enforce the stated project-wide coverage contract for every job, and the retained report cannot demonstrate 100%
coverage
for the no-extras environment.


##### Suggestion

Make the isolated no-extras test set cover the complete measured scope that remains valid without optional packages,
retain both missing-adapter assertions, and replace `--cov-fail-under=0` with `--cov-fail-under=100`. If the boundary is
intentionally report-only, revise the design and Task 11 to say that only the normal matrix enforces 100%; do not retain
the current contradictory wording.


##### Outcome

Accepted and applied: the isolated no-extras command now enforces the same 100% measured-code threshold as the normal jobs.

#### S02: Focused test commands inherit an incompatible whole-project gate

##### Where

Project Commands, focused unit and integration commands, lines 59-82; the variant commands, lines 85-153; and focused
test steps throughout Tasks 01-11, including lines 297-305, 337-344, 376-384, 418-436, 460-468, 546-556, 594-613,
640-655, 688-705, and 750-770.


##### Issue

After Task 11 changes the project pytest configuration to a 100% threshold, every `uv run pytest` invocation that does
not override `addopts` inherits `--cov=src/betwixt` and `--cov-fail-under=100`. The plan uses such invocations for
focused files, unit-only tests, integration-only tests, adapter-only tests, documentation tests, demo tests, and the
configuration test. Those subsets are not specified to cover every measured line, yet their expected output says they
pass. The no-extras command correctly clears `addopts`, but the other scoped commands do not.


##### Impact

Normal task execution and routine diagnosis can fail because a narrow test selection is held to a whole-project coverage
threshold. An executor may then weaken the threshold or skip the focused check, undermining the required 100% full-suite
gate and making the documented command inventory unreliable.


##### Suggestion

Clear project `addopts` for every focused test command, for example with `-o addopts=""`, or give each focused command
an
explicit coverage source and 100% threshold for its own measured scope. Keep the full-suite commands, including the
variant matrix and `make qa/full`, on the project configuration with `--cov-fail-under=100`.


##### Outcome

Accepted and applied: focused test commands now clear project coverage addopts, while full-suite and matrix commands retain the 100% gate.

## Notes

The active design and implementation plans contain no `85%` text. Historical review artifacts still mention the former
threshold, which is not an active plan. The current pre-implementation `pyproject.toml` still contains
`--cov-fail-under=85`; Task 11 must replace it with an explicit 100% setting and its configuration assertions should
verify that exact value. No broad coverage omission is specified in either plan. Every stated exclusion rule requires a
local `# pragma: no cover` with a nearby justification.

The documentation contract remains internally consistent: `concepts.md`, `behavior.md`, and `integrations.md` are flat
singleton pages, while `cases/` is directory-backed; the build smoke paths match the named `index.md` and
`api-reference.md` pages. Deployment remains separated and guarded: package publication is pushed `v*.*.*` tags only,
and documentation publication is limited to closed, merged pull requests targeting `main` with the exact documentation
path filters.

The optional adapters remain regular development dependencies but package-optional through separate `pydantic` and
`sqlalchemy` extras. The isolated no-extras job remains the only environment without both packages and retains
failure-safe
JUnit and coverage uploads. The Makefile style, sole public `Betwixt` naming, construct taxonomy, context contracts,
nested behavior, adapter precedence, native boundaries, examples, CLI paths, and earlier error and release contracts
show
no regression. The implementation-plan Markdown check still reports only the intentional level-five task technical-note
heading required by the artifact definition.
