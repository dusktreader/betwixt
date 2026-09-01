# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 18**

This re-review checks the updated design and implementation plans against implementation-review--16.md, the earlier
contract history, and the requested tag-only package and merged-pull-request documentation deployment rules.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The deployment-trigger findings are resolved. One significant no-extras verification gap remains:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--16.md` C01 ✓: The active plans no longer permit an alternative package-publication path;
  publication is tied to a validated pushed `v*.*.*` tag.
- `implementation-review--16.md` S01 ✓: The active plans specify `docs.yml` as a `pull_request` `closed` workflow
  with `docs/source/**` and `zensical.toml` paths, merged and `main` guards, resulting-main checkout behavior, and
  merge-commit, squash, and rebase coverage.
- Earlier implementation findings remain resolved: the staged public `Betwixt` class, construct taxonomy and overlap
  rules, full and partial context contracts, adapter boundaries and precedence, Zensical configuration, examples and
  demo paths, CI artifacts, lockfile work, Makefile conventions, and error ownership remain explicit.


## Findings

### Summary

| Finding ID | Title                                             | Outcome |
| ---------- | ------------------------------------------------- | ------- |
| S01        | Isolated no-extras verification is not executable |         |


### Significant

#### S01: Isolated no-extras verification is not executable

##### Where

Project Commands — Verify the package without optional extras — lines 99–110; Execution — Task 07 — lines 542–558;
Task 11 — AC03 — lines 720–724.


##### Issue

The isolated command provides only `pytest`, but the repository's pytest configuration adds `--cov`, coverage XML,
an 85% threshold, and JUnit options. Because the command runs pytest from the repository root, pytest still reads that
configuration even though `uv` uses `--no-project`. The isolated environment therefore lacks `pytest-cov` and fails
before collecting `test_no_extras.py`. Task 11 AC03 also requires only a JUnit upload for this test job, while the
design requires every test job to upload both JUnit and coverage reports.


##### Impact

The no-extras boundary cannot run as the documented package-versus-development-dependency gate. The release checks
cannot prove that either optional adapter is absent, and the boundary job cannot produce the required retained
coverage artifact.


##### Suggestion

Make the isolated command self-contained without installing Pydantic or SQLAlchemy: add `pytest-cov`, clear or
explicitly
reproduce the repository pytest options, and use a non-blocking threshold for this narrow boundary test if coverage is
still uploaded. For example, run pytest with `-o addopts=''`, explicit `.junit.xml` and `.coverage.xml` outputs, and
`--cov-fail-under=0`. Update `no-extras-boundary` to upload both reports with `if: ${{ !cancelled() }}` and
`retention-days: 14`. Keep the regular development dependency group in every normal variant and keep the isolated
boundary job as the only environment that omits both optional packages.


##### Outcome

Accepted and applied: the isolated no-extras command now disables project pytest defaults, installs `pytest-cov`, emits both required reports, and the boundary job uploads both with failure-safe 14-day retention.

## Notes

The active plans satisfy the requested deployment contracts: package publication is restricted to the pushed
`v*.*.*` tag path, and documentation deployment uses only the guarded closed merged-pull-request path with the exact
docs filters. The design's remaining negative statement about manual publication is a prohibition, not a permitted
publication path.

The optional-dependency strategy remains coherent apart from S01: Pydantic and SQLAlchemy are regular development
dependencies for normal adapter-capable jobs, package metadata exposes them only through their respective extras, and
the isolated boundary job omits both. The design plan's Markdown check passes. The implementation plan's only check
finding is the intentional level-five task technical-note heading required by the implementation-plan artifact
definition. This review also uses level-five field headings because the implementation-review artifact definition
requires them.
