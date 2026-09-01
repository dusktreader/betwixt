# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the implementation plan against `implementation-review--20.md`, the approved design, all earlier
contracts, and the requested boundary, documentation, dependency, Makefile, and release requirements.

**Iteration 21**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The portable no-extras command is now executable from the repository root, and the requested documentation, dependency,
Makefile, package-publication, documentation-publication, and earlier contract boundaries remain explicit and
consistent.
No new findings were identified:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--20.md` **S01** ✓: The isolated boundary command now installs the checkout through the portable
  `--with "betwixt @ file://$PWD"` reference, states the repository-root working directory, retains `--isolated` and
  `--no-project`, installs `pytest` and `pytest-cov`, clears project `addopts`, and writes both required reports. Task
  11
  requires the same command and failure-safe 14-day report uploads.
- `implementation-review--19.md` was clean; its singleton documentation layout, tag-only package publication,
  merged-pull-request documentation publication, optional dependency boundaries, Makefile conventions, and prior
  contract resolutions remain present.


## Findings

### Summary

No new findings were identified.

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |


## Notes

The no-extras boundary is isolated from the regular development environments: the direct checkout reference is resolved
without extras, only the test runners are added, repository pytest defaults are overridden, and the command tests both
missing optional adapters while emitting `.junit.xml` and `.coverage.xml`. The normal matrix retains the regular
Pydantic
and SQLAlchemy development dependencies, while package metadata exposes those adapters only through their respective
extras and keeps them out of base requirements.

The documentation plan keeps `concepts.md`, `behavior.md`, and `integrations.md` as flat singleton source files, retains
`cases/` for its multiple pages, names those files in navigation, and checks the matching `docs/site/index.html` and
`docs/site/api-reference/index.html` smoke paths for `index.md` and `api-reference.md`.

Package publication remains automatic and tag-only: `deploy.yml` has only the pushed `v*.*.*` trigger, no manual or
branch
publication path, and requires the reusable `quality`, `examples`, `docs`, and `distributions` success outputs.
Documentation publication remains separate and is limited to closed pull requests whose changed paths include
`docs/source/**` or `zensical.toml`, whose merged flag is true, and whose base branch is `main`; it builds the resulting
main revision and publishes only `betwixt-site` after the docs gate.

The plan retains the requested Makefile section banners, shortcut and slash-separated targets, inline help comments,
`.ONESHELL`, `.PHONY`, standard color/help infrastructure, and hidden guard or confirmation helpers. Earlier contracts
for
the sole public `Betwixt` class, construct taxonomy and overlap, full and partial context calls, nested traversal,
adapter precedence and native boundaries, diagnostics and error ownership, examples and demo paths, the twelve-job
matrix,
artifact retention, lockfile updates, and Zensical configuration remain explicit. The plan's only Markdown check result
is
the intentional level-five task technical-note heading required by the implementation-plan artifact definition.
