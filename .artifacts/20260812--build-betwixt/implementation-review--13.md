# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 13**

This re-review checks the implementation plan against implementation-review--12.md, all earlier implementation and
design reviews, the approved design plan, and the requested configuration, dependency, and variant contracts.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review resolved the two prior Critical findings and found one new Markdown conformance issue:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 1


## Prior Review Resolution

- **C01** ✓: Task 10 now names the valid Zensical hierarchy, `variant = "classic"`, source and output directories,
  `dev_addr`, the `::: betwixt` directive, and all six required mkdocstrings Python options with exact values.
- **C02** ✓: The local Pydantic, SQLAlchemy, and combined commands and all 12 command-table rows exclude
  `absent_extra` with the exact variant selectors. The base selector intentionally omits that exclusion so it alone
  collects the absent-extra modules.
- **T01** ✓: The two previously reported overlong task-step lines remain wrapped within the 120-character limit.
- **Earlier contracts** ✓: The sole `Betwixt` class in `src/betwixt/betwixt.py`, direct and derived context call forms,
  native SQLAlchemy boundaries, documentation and demo scope, CI and release gates, lockfile work, and package
  metadata remain consistent with the approved design. Pydantic remains explicitly optional as
  `pydantic>=2.7,<3` in the `pydantic` package extra and absent from base requirements.


## Findings

### Summary

| Finding ID | Title                                       | Outcome |
| ---------- | ------------------------------------------- | ------- |
| T01        | Exact command table columns are not aligned |         |


### Trivial

#### T01: Exact command table columns are not aligned

##### Where

Technical Notes — Exact CI and final-verification command table — line 812


##### Issue

The Markdown formatter reports that the table columns are not aligned. The table is the authoritative 12-row command
matrix, so its delimiters and cell padding should remain mechanically and visually consistent without changing any
selector or command text.


##### Impact

The implementation plan still violates the repository Markdown table-format requirement and is harder to audit for
differences between the 12 variant rows.


##### Suggestion

Align the header, delimiter, and every body cell in the command table to the widest cell in each column. Preserve these
exact selectors while doing so: base `not optional_pydantic and not optional_sqlalchemy`; Pydantic
`not optional_sqlalchemy and not absent_extra`; SQLAlchemy `not optional_pydantic and not absent_extra`; and combined
`not absent_extra`.


##### Outcome

Accepted and applied: the authoritative 12-row command table was aligned mechanically without changing its selectors or command text.

## Notes

The exact Zensical configuration contract is now executable: `[project]` carries the site settings and navigation,
`[project.theme]` uses `variant = "classic"`, and
`[project.plugins.mkdocstrings.handlers.python]` uses `paths = ["src"]` plus `heading_level = 3`,
`show_root_heading = true`, `separate_signature = true`, `show_signature_annotations = true`, `show_source = false`,
and `docstring_style = "google"` in its options table.

The four local variant selectors and their 12 table rows match. The base rows collect both absent-extra modules;
Pydantic rows use `not optional_sqlalchemy and not absent_extra`, SQLAlchemy rows use
`not optional_pydantic and not absent_extra`, and combined rows use `not absent_extra`. No regression remains in the
Betwixt class/module, construct, annotation, full/partial, adapter, SQLAlchemy, documentation, example, demo, CI,
release, lockfile, or package contracts. The implementation-plan formatter also reports the required level-five task
technical-note heading; that is an intentional exception required by the artifact definition.
