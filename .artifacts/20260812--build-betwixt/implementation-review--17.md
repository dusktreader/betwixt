# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 17**

This re-review checks the updated design and implementation plans against implementation-review--16.md, all earlier
findings, and the requested tag-only package and merged-pull-request documentation deployment contracts.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The documentation trigger revision is now explicit, but stale manual-publication wording still contradicts the required
delivery contract. The isolated no-extras command also cannot run with the repository's configured pytest options.

- **Critical**: 1
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--16.md` **C01** ✗: The design Goal and Documentation Architecture still allow an explicit
  manual
  approval, and the implementation-plan Goal still allows an explicitly approved manual workflow.
- `implementation-review--16.md` **S01** ✓: `docs.yml` now uses only `pull_request` `closed` events with the exact
  `docs/source/**` and `zensical.toml` paths, guards deployment with merged status and `main` as the base branch, and
  explicitly supports merge-commit, squash, and rebase merges while excluding direct and unrelated pushes.
- Earlier implementation findings remain resolved: the public API and staged class ownership, construct and overlap
  contracts, full and partial context rules, dependency matrix, adapter boundaries, Zensical configuration, examples,
  CI artifacts, lockfile work, and task-level checks remain present.
- `design-review--06.md` remains clean; no earlier design finding requires separate resolution.


## Findings

### Summary

| Finding ID | Title                                                         | Outcome |
| ---------- | ------------------------------------------------------------- | ------- |
| C01        | Manual publication wording still contradicts tag-only release |         |
| S01        | Isolated no-extras verification cannot run as documented      |         |


### Critical

#### C01: Manual publication wording still contradicts tag-only release

##### Where

Design Plan — Goal line 20 and Documentation Architecture line 554; Implementation Plan — Goal lines 16–22.


##### Issue

The design says package and documentation publishing may use “an explicit manual approval” and later describes “tag or
manual release gates.” The implementation Goal likewise permits “an explicitly approved manual workflow.” These
statements
remain broader than the task-level tag-only package contract and also conflict with the merged-pull-request-only
documentation contract.


##### Impact

An executor can retain or add `workflow_dispatch` or another manual publication path while satisfying the Goal. Package
publication could then occur without a pushed `v*.*.*` tag, and documentation publication could bypass the required
closed, merged pull-request event and its path and base-branch guards.


##### Suggestion

Replace every manual-publication alternative with one unambiguous contract: package publication occurs only from
`deploy.yml` after a pushed tag matching `v*.*.*` and successful `quality`, `examples`, `docs`, and `distributions`
gates;
`deploy.yml` has no `workflow_dispatch`, branch-push, or other non-tag publication trigger. Documentation publication
occurs only from the guarded closed merged pull-request event already specified in the task-level contract.


##### Outcome


### Significant

#### S01: Isolated no-extras verification cannot run as documented

##### Where

Project Commands — Verify the package without optional extras — lines 98–109; Execution — Task 07 — Steps 1 and the
following test-collection note — lines 541–557; Task 11 — AC03 — lines 719–723.


##### Issue

The isolated command installs only `pytest`, but the repository's pytest configuration adds `--cov`, coverage XML, and
JUnit options. `--no-project` prevents uv from installing the development group; it does not stop pytest from
discovering
the repository configuration. The isolated environment therefore lacks `pytest-cov` and fails before collecting the
no-extras test. The plan also requests only a JUnit upload for this test job even though the design requires every test
job to upload JUnit and coverage reports.


##### Impact

The no-extras boundary cannot verify that core imports work without either optional adapter package, so the
package-versus-
development dependency distinction is not an executable release gate. The boundary job also cannot produce the required
retained reports.


##### Suggestion

Make the isolated command self-contained without installing Pydantic or SQLAlchemy: provide `pytest-cov` as an isolated
test-runner dependency, explicitly override or reproduce the required pytest options, and set a non-blocking coverage
threshold for this narrow boundary test if it still uploads coverage. Configure `no-extras-boundary` to upload both
`.junit.xml` and `.coverage.xml` with `if: ${{ !cancelled() }}` and 14-day retention. Keep the normal jobs on the
regular
development dependency group and the isolated job as the only environment that omits both optional packages.


##### Outcome


## Notes

The optional dependency distinction itself remains correct: Pydantic and SQLAlchemy are regular development
dependencies,
are exposed to consumers only through their respective package extras, and are absent from the base package
requirements.
The normal four-variant jobs use the development dependency set, while the isolated boundary job omits both adapters.

The Markdown check passes for the design plan. The implementation plan reports only its intentional level-five task
technical-note heading required by the implementation-plan artifact definition.
