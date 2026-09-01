# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the updated design and implementation plans against `implementation-review--22.md` and the
earlier contracts. It confirms the threshold and focused-command corrections, but finds that the isolated no-extras
coverage command cannot substantiate its 100% gate.

**Iteration 23**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review found one Critical and one Significant finding. The active plans contain no stale 85% threshold or zero
coverage threshold, and the documented full-suite versus focused-test command split is now explicit.

- **Critical**: 1
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--22.md` S01 ⚠: The isolated command now uses `--cov-fail-under=100` instead of zero, but it
  still measures `src/betwixt` while selecting only `tests/integration/test_no_extras.py`; the coverage-scope defect
  remains.
- `implementation-review--22.md` S02 ✓: Explicit focused pytest commands now clear project `addopts`, while the
  complete variant commands and `make qa/full` retain the project-wide coverage gate.
- `implementation-review--21.md` and `design-review--06.md` were clean; their dependency, documentation, deployment,
  Makefile, naming, adapter, and translation contracts remain present.


## Findings

### Summary

| Finding ID | Title                                                                          | Outcome |
| ---------- | ------------------------------------------------------------------------------ | ------- |
| C01        | No-extras 100% coverage gate measures the whole package with one boundary test |         |
| S01        | Exception-preservation step contradicts the error-ownership contract           |         |


### Critical

#### C01: No-extras 100% coverage gate measures the whole package with one boundary test

##### Where

Project Commands, “Verify the package without optional extras,” line 104; Task 11 AC03, lines 731–735; and the CI
command table, lines 863–865. The corresponding design requirement is AC30, lines 466–475.


##### Issue

The isolated command clears project `addopts`, measures all of `src/betwixt`, and selects only
`tests/integration/test_no_extras.py`. The plan describes that file as the two missing-adapter boundary assertions; it
does not make it a complete test suite for the core implementation. The command therefore leaves the core modules and
optional-adapter implementation lines unexecuted while `--cov-fail-under=100` and Task 11 require 100% on measured code.
No executable coverage scope or local exclusion plan resolves that contradiction.


##### Impact

The boundary job will fail under a normal implementation, or an executor will weaken the threshold or add broad
coverage omissions to make it pass. Either outcome violates the 100% measured-code contract and makes the retained
coverage report unreliable evidence of the no-extras boundary.


##### Suggestion

Define a self-contained no-extras test suite that covers every line in its measured source scope in addition to both
missing-adapter assertions, and state that scope in the command and Task 11. If `src/betwixt` remains the scope, the
plan must explain how every measurable line is executable without optional dependencies. Any unavoidable exclusions
must be local `# pragma: no cover` lines with nearby justifications; do not use a broad omit or lower the threshold.


##### Outcome

Accepted and applied: the no-extras command now measures the complete core test scope with the 100% threshold while retaining both missing-adapter assertions.

----

### Significant

#### S01: Exception-preservation step contradicts the error-ownership contract

##### Where

Task 04 AC05, lines 411–413; Task 04 Step 4, lines 434–437; and Technical Notes, lines 832–835. The design contract is
AC23, lines 384–391.


##### Issue

The acceptance criterion and technical notes require user-callable, field-access, and native construction exceptions to
propagate unchanged, but Step 4 permits catching them “to attach Betwixt boundary context.” The plan does not define
that context or identify an exception class for which modification is allowed. Wrapping, re-raising, or adding a cause
would change the exception behavior that the other sections promise to preserve.


##### Impact

Implementers can produce different exception types, identities, or causes at the same translation boundary while still
claiming to satisfy Step 4. Callers lose the stable native and user-error ownership promised by the design, and tests
cannot determine which behavior is authoritative.


##### Suggestion

Rewrite Step 4 to say: “Do not catch, wrap, or re-raise user-callable, derivation, field-access, set-insertion, or
native construction and validation exceptions. Raise only the specified Betwixt-owned errors before native construction;
otherwise preserve the original exception type, cause, and traceback.” Test each listed boundary without allowing the
step to authorize an exception wrapper.


##### Outcome

Accepted and applied: Task 04 now forbids catching, wrapping, or re-raising user, derivation, field-access, set-insertion, and native construction exceptions.

----

## Notes

The active design and implementation plans contain no `85%`, `--cov-fail-under=0`, or zero coverage threshold. Their
other uses of “zero” describe zero-argument defaults and are unrelated to coverage. All explicit focused pytest commands
use `-o addopts=""`; the full variant commands, the exact 12-row matrix, and `make qa/full` retain the project-wide
100% gate.

The plans still require local pragma-only exclusions with nearby justifications, regular development dependencies for
Pydantic and SQLAlchemy, package-optional `pydantic` and `sqlalchemy` extras, and both JUnit and coverage reports for
the isolated boundary job. Tag-only package publication, merged-main-pull-request documentation deployment, the flat
singleton documentation layout, the requested Makefile conventions, the sole public `Betwixt` naming, and the earlier
construct, context, nested, adapter, example, CLI, and native-boundary contracts show no regression. The design-plan
Markdown check passes; the implementation-plan check reports only the intentional level-five task technical-note
heading required by its artifact definition.
