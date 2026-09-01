# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks the implementation plan against implementation-review--08.md, the approved design plan, and the
full earlier finding history, with focused attention to the full and partial context contracts.

**Iteration 09**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review rechecked the remaining finding from implementation-review--08.md and all earlier findings carried into that
review. Task 06 now states the required partial derivation call contract, and no unresolved or new findings remain:

- **Critical**: 0
- **Significant**: 0
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--08.md` **S01** ✓: Task 06 AC06 now explicitly requires
  `derive(outer_context)` with exactly one positional argument and no `ctx=...` injection. Task 06 AC06 and Step 1
  require positional-only selector tests, omitted and explicit-`None` derivations, identity derivation, both directions,
  and per-boundary call counts with the result reused for all elements.
- `implementation-review--07.md` **S01** ✓: Task 04 still requires declaration-time validation for map, reduce, project,
  and nested inner callables in both directions, accepts only a final keyword-only `ctx`, injects it as `ctx=...`, and
  rejects both positional forms.
- `implementation-review--07.md` **S02** ✓: Tasks 05 and 06 now state the exact positional derivation call and test
  positional-only selectors, omitted and explicit-`None` derivations, identity derivation, both directions, and call
  counts.
- `implementation-review--06.md` **S03** ✓: Partial operations accept context, use `ctx=...` only for direct
  context-aware producers, and cover nested derivation reuse and boundary counts.
- `implementation-review--04.md` **S01-S03** ✓: The independent nested pairwise contract, projection failure ownership,
  and sole `Betwixt` class/module ownership remain explicit.
- `implementation-review--01.md` **C01-C02, S01-S12, T01-T02** ✓: The required heading hierarchy, command inventory,
  construct and overlap rules, staged exports, variant matrix, optional-test collection, demo smoke, adapter fixtures,
  alias matrix, documentation inventory, CI and release gates, lockfile scope, resolved unknowns, task-level checks, and
  package metadata distinction remain present.


## Findings

### Summary

No new findings were identified.

| Finding ID | Title | Outcome |
| ---------- | ----- | ------- |


## Notes

The context contract is consistent across the plan and the approved design: direct context-aware map, reduce, project,
and nested inner callables accept a final keyword-only `ctx` and receive it only as `ctx=...`; nested context
derivations
are the distinct exception and receive exactly one positional `outer_context` with no keyword injection. Full and
partial
paths both require omitted, explicit-`None`, identity, positional-only, both-direction, reuse, and per-boundary-count
coverage. The implementation-plan Markdown check still reports the required level-five task technical-note heading;
that is an intentional artifact-structure exception, not a new finding.
