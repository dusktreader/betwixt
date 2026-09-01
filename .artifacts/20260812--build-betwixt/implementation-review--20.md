# Implementation Plan Review: Betwixt core mapping layer, documentation, and delivery

This re-review checks the implementation plan against `implementation-review--19.md`, the approved design contracts,
and the requested documentation, packaging, dependency, naming, context, Makefile, example, and CI constraints.

**Iteration 20**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The plan retains the prior contract coverage and fixes the singleton documentation layout, but the isolated no-extras
command is not portable to the CI job that is required to run it:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--19.md` was clean, so no prior findings require resolution.


## Findings

### Summary

| Finding ID | Title                                             | Outcome |
| ---------- | ------------------------------------------------- | ------- |
| S01        | Isolated no-extras command hardcodes a local path |         |


### Significant

#### S01: Isolated no-extras command hardcodes a local path

##### Where

Project Commands, “Verify the package without optional extras,” lines 99–111; Execution, Task 11 AC03 and steps 4–5,
lines 722–761.


##### Issue

The isolated command installs `betwixt` from the absolute path
`/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt`. Task 11 requires the CI
no-extras job to run this command, but that path does not exist on a GitHub runner.


##### Impact

The boundary job fails while resolving the package instead of proving that core imports work without Pydantic or
SQLAlchemy. It cannot produce the required reports or validate the package-versus-development dependency boundary.


##### Suggestion

Run the command from the repository root and reference the checkout portably, for example with
`--with "betwixt @ file://$PWD"`. State the working-directory requirement in the command and use the same portable
form in the CI job, while retaining `--isolated`, `--no-project`, `pytest-cov`, cleared `addopts`, and both report
paths.


##### Outcome

Accepted and applied: the no-extras command now uses the portable `$PWD` checkout reference so it can run on CI runners as well as locally.

## Notes

The documentation layout is internally consistent: navigation names `concepts.md`, `behavior.md`, and
`integrations.md` as flat singleton source files, while `cases/` remains directory-backed for multiple pages. The docs
smoke paths `docs/site/index.html` and `docs/site/api-reference/index.html` agree with `index.md` and
`api-reference.md`.

Package publication remains tag-only and gated by the reusable quality outputs. Documentation publication remains
limited
to qualifying closed, merged pull requests targeting `main`. The plan keeps Pydantic and SQLAlchemy in regular
development dependencies while exposing them only through package extras, and isolates the no-extras boundary.

The sole public class remains `Betwixt`, canonical mapped names remain distinct from database names, and direct and
nested
context propagation retain the approved keyword-only and positional derivation contracts. Makefile conventions, all four
example variants, the twelve-job CI matrix, artifact retention, and the earlier construct, adapter, error, partial, and
native-construction contracts remain explicit. The plan's only Markdown check finding is the intentional level-five task
technical-note heading required by the implementation-plan artifact definition.
