# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

**Iteration 15**

This re-review checks the implementation plan against the available implementation reviews 01 through 13, the approved
design plan, repository standards, and the requested Makefile and optional-package contracts. The requested
`implementation-review--14.md` is not present beside the plan, so its findings could not be independently reconciled.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The available review history is resolved, and this pass found no new implementation-plan findings:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--13.md` T01 ✓: The authoritative 12-row command table remains aligned without changing any
  selector or command text.
- `implementation-review--12.md` C01-C02 ✓: Task 10 names the valid Zensical hierarchy and handler options, and the
  installed-extra selectors exclude `absent_extra` while the base selector collects the absent-extra tests.
- `implementation-review--11.md` C01-C02 and T01 ✓: The Zensical configuration, absent-extra boundary, and Markdown
  line lengths remain corrected.
- `implementation-review--10.md` S01-S03 ✓: The Zensical serve configuration, optional-test selectors, and public
  full/partial keyword-only operation signatures remain explicit.
- `implementation-review--08.md` S01 ✓: Partial nested derivations still require exactly one positional
  `derive(outer_context)` call with no `ctx=` injection and reuse the result per boundary.
- `implementation-review--07.md` S01-S02 ✓: Direct callable validation remains declaration-time and family-complete,
  while nested derivations retain their distinct positional invocation contract.
- `implementation-review--06.md` S01-S03 ✓: Direct and nested context behavior remains explicit in both full and partial
  operations.
- `implementation-review--04.md` S01-S03 ✓: Nested pairwise directions, projection extraction failures, and sole
  `Betwixt` class ownership remain assigned to executable tasks.
- `implementation-review--01.md` C01-C02, S01-S12, and T01-T02 ✓: The structural, API, variant, adapter, documentation,
  CI, release, lockfile, unknowns, quality-check, and package-metadata findings remain resolved through the later
  reviews.
- `implementation-review--14.md`: The requested artifact is absent from the artifact directory and could not be
  reviewed.


## Findings

### Summary

No new findings were identified.

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |


## Notes

The Goal and Task 11 Step 2 explicitly require the requested style from the referenced Makefile examples: grouped
section
banners; shortcut hierarchy such as `qa: qa/full` and `docs: docs/serve`; slash-separated subtargets; inline `##` help
comments and a shared `help` printer; `.ONESHELL`; `.PHONY`; the standard color table and variables; and hidden
`_guard_*` or `_confirm` helpers where applicable. The requirement matches the fetched reference structure.

Task 07 keeps Pydantic at `pydantic>=2.7,<3` in the optional `pydantic` extra only, preserves core imports without the
extra, and tests the missing-extra declaration boundary in a subprocess. Task 08 applies the same boundary to
`SQLAlchemy>=2.0,<3`, with lazy imports and absent-extra coverage. Installed-extra selectors exclude `absent_extra`, so
those tests remain base-only.

The Markdown checker reports only the required level-five `##### Declaration representation` heading at line 291 of the
implementation plan. The implementation-plan artifact definition requires that level for task technical-note
subsections, so this is an intentional exception rather than a finding.
