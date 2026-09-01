# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the implementation plan against implementation-review--07.md, the approved design, and the
requested callable-context and partial-operation coverage.

**Iteration 08**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review rechecked the two findings from implementation-review--07.md and all earlier findings carried into that
review. It found no Critical or Trivial findings and identified one remaining Significant gap:

- **Critical**: 0
- **Significant**: 1
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--07.md` **S01** ✓: Task 04 now requires declaration-time validation across map, reduce,
  project,
  and nested inner callables in both directions, accepts only a final keyword-only `ctx`, injects it as `ctx=...`, and
  rejects both positional-only and positional-or-keyword forms.
- `implementation-review--07.md` **S02** ⚠: Task 05 now states the exact `derive(outer_context)` call and adds
  positional-only selector tests, but Task 06 still reduces the partial-path contract to “positionally once” and does
  not require the same exact call-shape or positional-only selector test.
- The earlier findings from implementation-review--01.md and implementation-review--04.md, plus S03 from
  implementation-review--06.md, remain resolved. Their command, API, overlap, variant, adapter, documentation, CI,
  lockfile, unknowns, quality-check, and partial-context resolutions remain present.


## Findings

### Summary

| Finding ID | Title                                                            | Outcome |
| ---------- | ---------------------------------------------------------------- | ------- |
| S01        | Partial derivation tests do not preserve the exact call contract |         |


### Significant

#### S01: Partial derivation tests do not preserve the exact call contract

##### Where

Execution — Task 06 — Acceptance Criteria — AC06 and Steps — Step 1, approximately lines 464-474.


##### Issue

Task 05 correctly requires `derive(outer_context)` with exactly one positional argument, no `ctx=...` injection, and
positional-only selector tests. Task 06's partial-operation criterion only says derivations run “positionally once,” and
its test step only asks for “nested positional-once context derivation.” Neither requires exactly one positional
argument, the absence of keyword injection, or a positional-only selector on the partial path.


##### Impact

Partial nested translation can implement or test a different derivation API from full translation. An executor could
pass
an extra positional argument or omit the positional-only compatibility check while satisfying the partial task,
violating
the shared AC06 contract at the partial boundary.


##### Suggestion

Rewrite Task 06 AC06 and Step 1 to require `derive(outer_context)` with exactly one positional argument and no `ctx=...`
injection at each partial nesting boundary, once per boundary with the result reused for all elements. Add
both-direction
partial tests using a positional-only selector, omitted and explicit-`None` derivations, identity derivation, and
per-boundary call counts. Keep direct partial map, reduce, and nested callable tests explicit for final keyword-only
`ctx` injection.


##### Outcome

Accepted and applied: Task 06 now requires partial nested derivations to call `derive(outer_context)` exactly once with one positional argument, never `ctx=...`, and tests both directions and selector variants.

## Notes

Task 04 is now aligned with design AC05: its declaration-time, family-complete matrix covers map, reduce, project, and
nested inner callables in both directions, including both rejected positional forms. Task 05 is aligned with design
AC06's
exact derivation call and positional-only selector requirement. The remaining issue is limited to making the partial
path
state and test that same boundary contract explicitly.

The formatter reports the required level-five finding-field headings and the required level-five task technical-note
heading in the implementation plan. These are intentional exceptions required by the implementation-review and
implementation-plan artifact definitions.
