# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the updated design and implementation plans against implementation-review--18.md, the full
earlier contract history, and the requested package, documentation, and no-extras delivery rules.

**Iteration 19**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The no-extras correction is complete. The updated plans contain no unresolved or new findings:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--18.md` S01 ✓: The isolated command installs `pytest` and `pytest-cov`, disables repository
  pytest defaults, writes explicit JUnit and coverage XML reports, and uses a non-blocking coverage threshold. Task 11
  also requires both reports with failure-safe 14-day retention.
- `implementation-review--17.md` C01 ✓: Both plans now prohibit manual package publication and require automatic package
  publication only from the validated pushed `v*.*.*` tag path.
- `implementation-review--17.md` S01 ✓: Documentation publication now uses only a closed `pull_request` event with
  `docs/source/**` and `zensical.toml` filters, plus merged and `main` guards and excluded-event coverage.
- Earlier findings remain resolved: the public `Betwixt` surface, construct and overlap rules, full and partial context
  contracts, adapter boundaries, Zensical configuration, examples and demo, CI matrix and artifacts, lockfile work,
  Makefile conventions, and error ownership remain explicit and aligned with the design.
- `design-review--06.md` remains clean; no unresolved design finding requires separate implementation-plan action.


## Findings

### Summary

No new findings were identified.

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |

The implementation plan now uses flat files for singleton documentation sections and retains directories only for
multi-page sections.


## Notes

The no-extras command is self-contained: it uses `uv run --isolated --no-project`, installs the package from the
explicit
workspace path plus `pytest` and `pytest-cov`, clears configured pytest `addopts`, and explicitly emits `.junit.xml` and
`.coverage.xml`. The command does not install either optional adapter, and the boundary job uploads both reports after
failure with 14-day retention.

Package publication is automatic and tag-only. The implementation plan requires `deploy.yml` to have only the pushed
`v*.*.*` tag trigger, no `workflow_dispatch` or branch-push trigger, and successful `quality`, `examples`, `docs`, and
`distributions` outputs before publishing.

Documentation publication is automatic only for a closed pull request whose changed paths include `docs/source/**` or
`zensical.toml`, whose `merged` flag is true, and whose base branch is `main`. The plans explicitly exclude direct main
pushes, feature-branch pushes, tag pushes, and unrelated merges while keeping package and site publication separate.

The design Markdown check passes. The implementation-plan check reports only the required level-five task technical-note
heading, which is an intentional exception mandated by the implementation-plan artifact definition.
