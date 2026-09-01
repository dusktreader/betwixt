# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the updated design and implementation plans against `implementation-review--24.md` and the
earlier contracts. The test-selection correction is present, but the no-extras coverage source still includes optional
adapter modules.

**Iteration 25**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```

The design plan cross-checked for alignment is:

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/design-plan.md
```


## Overview

The review found one Critical finding. The no-extras command now selects the boundary test and the complete
`tests/unit` path without a marker exclusion, retains the 100% threshold, and writes both reports. Its
`--cov=src/betwixt` target still does not define a dependency-free core source scope.

- **Critical**: 1
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--24.md` C01 ⚠: The command now path-selects `tests/integration/test_no_extras.py` together with
  `tests/unit` and no longer applies `-m absent_extra`, so the complete core unit scope is selected. The remaining
  source-scope defect is carried forward below: `--cov=src/betwixt` still includes the optional adapter modules, and the
  plans do not define a safe no-extras coverage scope.


## Findings

### Summary

| Finding ID | Title                                                   | Outcome |
| ---------- | ------------------------------------------------------- | ------- |
| C01        | No-extras coverage still measures optional adapter code |         |


### Critical

#### C01: No-extras coverage still measures optional adapter code

##### Where

Project Commands, “Verify the package without optional extras,” lines 99-112; Task 07 Technical Notes, lines 562-567;
Task 11 AC03, lines 733-741; and the corresponding design requirements in AC30, lines 466-476 and 587-600.


##### Issue

The corrected command selects `tests/integration/test_no_extras.py tests/unit`, clears project `addopts`, keeps
`--cov-fail-under=100`, and emits both `.junit.xml` and `.coverage.xml`. However, it still passes `--cov=src/betwixt`.
The plan adds `src/betwixt/adapters/pydantic.py` and `src/betwixt/adapters/sqlalchemy.py`, while this job explicitly
installs neither optional dependency. The plan does not state that those modules are executable in this environment,
exclude them through a defined source scope, or otherwise explain how the selected core tests cover them.


##### Impact

The no-extras job cannot substantiate its 100% measured-code result. Coverage can report unexecuted optional adapter
lines, causing the job to fail or encouraging a broad omission or threshold reduction. Either outcome undermines the
required 100% coverage contract and makes the retained coverage report unreliable evidence of the dependency boundary.


##### Suggestion

Define a dependency-free core source scope and use it explicitly for the isolated command and Task 11 AC03. The scope
must include every core module covered by `tests/unit`, including the dataclass and base/registry adapter modules, but
must not include the Pydantic or SQLAlchemy adapter modules. Keep the corrected path-based test selection, both report
options, and `--cov-fail-under=100`. If the intended scope remains all of `src/betwixt`, add a concrete strategy and
tests that execute every measured optional-adapter line without installing either dependency. Do not lower the threshold
or use a broad omission; retain only local `# pragma: no cover` exclusions with nearby justifications for genuinely
structural, trivial, or intentionally untestable lines.


##### Outcome

Accepted and applied: the no-extras command now measures an explicit dependency-free core module list while retaining the 100% threshold, boundary assertions, reports, and local pragma-only exclusion rule.

----

## Notes

The exception contract remains unchanged. Design AC06 and AC23, implementation Task 04, and the implementation
technical notes require user-callable, derivation, field-access, set-insertion, and native construction or validation
exceptions to propagate with their original type, cause, and traceback. Betwixt-owned errors remain limited to the
specified declaration, adapter, partial-input, unloaded-field, missing-default, and unmapped-field boundaries.

The 100% coverage and pragma rules remain consistent across design AC30, the CI/CD architecture, implementation Task 06,
Task 11, and Task 12. No broad omission or reduced threshold is authorized. The construct taxonomy, sole public
`Betwixt` class, `field_refs`, full and partial semantics, context and nested traversal, adapter precedence and native
boundaries, optional dependency split, documentation and example contracts, CLI behavior, twelve-job matrix, artifact
retention, Makefile and lockfile work, and tag-only or merged-main release gates remain present.

The design Markdown check passed. The implementation-plan check reports only the intentional level-five task technical
note heading required by the implementation-plan artifact definition.
