# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the implementation plan against implementation-review--10.md, the approved design plan, and the
requested optional-dependency, documentation, variant-selection, API-signature, adapter, example, CI, and lockfile
contracts.

**Iteration 11**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

Two findings from implementation-review--10.md remain unresolved and are carried forward as Critical findings. The
Markdown checker also reports two overlong prose lines.

- **Critical**: 2
- **Significant**: 0
- **Trivial**: 1


## Prior Review Resolution

- `implementation-review--10.md` S01 ✗: Task 10 still prescribes `theme = "material"` and `plugins = ["mkdocstrings"]`
  without the required Zensical table hierarchy or Python handler configuration, and it still omits the `dev_addr` that
  would make `zensical serve` use the documented `localhost:10000` address.
- `implementation-review--10.md` S02 ✗: The plan still collects both absent-extra modules in the Pydantic, SQLAlchemy,
  and combined variants. It has no `absent_extra` marker or selector exclusion for those installed-extra jobs.
- `implementation-review--10.md` S03 ✓: Full operations specify keyword-only `context` and `defaults`, partial
  operations specify keyword-only `context`, and the tests require positional arguments to raise `TypeError`.
- `implementation-review--09.md` was clean and introduced no finding requiring resolution.
- `implementation-review--08.md` S01 ✓ and `implementation-review--07.md` S01-S02 ✓: Direct callable context uses a
  final keyword-only `ctx` with `ctx=...` injection, rejects both positional forms at declaration time, and nested
  derivations use the distinct exact positional call contract in both full and partial paths.
- `implementation-review--06.md` S03 ✓: Partial direct callables and nested derivations retain the shared context
  contract.
- `implementation-review--04.md` S01-S03 ✓: Nested pairwise mappings require independent directions, projection
  extraction rejects unknown or unreadable fields, and Task 01 owns the sole public `Betwixt` class in
  `src/betwixt/betwixt.py`.
- The earlier findings from `implementation-review--01.md` remain resolved for construct naming and overlap, staged
  exports, SQLAlchemy fixtures and native boundaries, examples and demo smoke paths, documentation inventory, CI
  artifact and release topology, lockfile and stale-documentation updates, resolved unknowns, task-level checks, and
  package metadata. The two residual regressions are detailed below.


## Findings

### Summary

| Finding ID | Title                                                    | Outcome |
| ---------- | -------------------------------------------------------- | ------- |
| C01        | Zensical configuration and serve address remain invalid  |         |
| C02        | Absent-extra tests are not base-only                     |         |
| T01        | Two task-step prose lines exceed the Markdown line limit |         |


### Critical

#### C01: Zensical configuration and serve address remain invalid

##### Where

Execution — Task 10 — AC01 and Steps 2–3, approximately lines 631–660; Project Commands — Serve the documentation,
approximately lines 147–157.


##### Issue

The plan still tells the executor to add `site`, `theme = "material"`, and `plugins = ["mkdocstrings"]` to
`zensical.toml`. It does not specify the required `[project]` scope, `[project.theme]` with `variant = "classic"`, or
`[project.plugins.mkdocstrings.handlers.python]` with the `src` path and handler options. It also never adds
`dev_addr = "localhost:10000"`, despite documenting that address while invoking only `zensical serve`.


##### Impact

The generated configuration may fail Zensical validation or omit the Python API plugin. The serve command will otherwise
use Zensical's default address rather than the documented endpoint, so the local documentation workflow is not
reproducible.


##### Suggestion

Rewrite Task 10 to require `[project]` settings for `site_name`, `docs_dir = "docs/source"`, `site_dir = "docs/site"`,
`dev_addr = "localhost:10000"`, and `nav`; require `[project.theme] variant = "classic"`; and configure the Python
handler under `[project.plugins.mkdocstrings.handlers.python]` with `paths = ["src"]` and the required options. Keep
`zensical build --clean` and `zensical serve` as the Make recipes after these settings are defined.


##### Outcome

Accepted and applied: the implementation plan now defines the valid Zensical project hierarchy, theme, Python handler options, source/output paths, and serve address.

#### C02: Absent-extra tests are not base-only

##### Where

Execution — Task 07 marker and selector rules, approximately lines 529–535; Task 08 absent-extra tests, approximately
lines 555–577; Project Commands and the exact CI command table, approximately lines 81–131 and 797–815.


##### Issue

The plan says the base selector collects both absent-extra modules, but the Pydantic selector excludes only
`optional_sqlalchemy`, the SQLAlchemy selector excludes only `optional_pydantic`, and the combined selector collects all
tests. No `absent_extra` marker is registered or excluded from those selectors. The prescribed child process inherits
the
variant's installed environment, so it does not make the target package absent.


##### Impact

The Pydantic and SQLAlchemy jobs can execute the wrong missing-dependency checks with their target package installed,
and
the combined job can do the same for both packages. A passing matrix would therefore fail to prove the base-only
missing-extra boundary and can produce contradictory test results.


##### Suggestion

Register an `absent_extra` marker and mark both absent-extra modules. Make the base selector the only selector that
collects those tests; add `and not absent_extra` to the Pydantic and SQLAlchemy selectors and `not absent_extra` to the
combined selector in every local command and CI table entry. Retain the subprocess assertions that core import succeeds
and the target adapter declaration raises the actionable missing-extra error.


##### Outcome

Accepted and applied: the plan now registers `absent_extra`, restricts absent-extra tests to the base variant, and excludes that marker from every installed-extra selector and command-table row.

### Trivial

#### T01: Two task-step prose lines exceed the Markdown line limit

##### Where

Execution — Task 04 — Steps — Step 1 at line 396 and Task 06 — Acceptance Criteria — AC06 at line 467.


##### Issue

The Markdown checker reports both prose lines as longer than the 120-character limit. The required level-five technical-
note heading at line 288 and this review's level-five field headings remain intentional exceptions required by their
respective artifact structures.


##### Suggestion

Wrap the two reported prose lines at 120 characters or fewer without changing their callable-context requirements.


##### Outcome

Accepted and applied: task-step prose now stays within the Markdown line-length limit.

## Notes

Task 07 AC01 still explicitly states `pydantic>=2.7,<3` only in the optional `pydantic` extra, keeps it out of the base
package's required dependencies, and requires the actionable missing-extra error. That wording remains sufficient and
does not introduce a finding.

The plan retains the approved naming contract: the sole public class is `Betwixt` in `src/betwixt/betwixt.py`, with no
public `Twixt` or `twixt` class/module alternative. Its direct callable `ctx` contract, SQLAlchemy canonical mapped-name
and unloaded-relationship boundary, twelve-job CI matrix and artifact retention, executable examples and demo paths,
documentation page inventory, and `uv.lock` update plus `uv sync --locked` stale-lock check remain present. C01 and C02
must be resolved before those otherwise consistent delivery gates can be considered executable.
