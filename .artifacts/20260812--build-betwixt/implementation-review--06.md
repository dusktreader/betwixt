# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks both plan artifacts after the context callable contract changed, rechecks
implementation-review--05.md and all earlier implementation-plan findings, and verifies alignment with the approved
design.


**Iteration 06**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review found that the design states the new keyword-only `ctx` contract, but the implementation plan leaves three
execution and test details underspecified:

- **Critical**: 0
- **Significant**: 3
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--05.md` contained no new findings. Its three resolutions from `implementation-review--04.md`
  remain present: `nested_pairwise` has the independent-callable contract and tests, projection extraction rejects
  unknown or unreadable fields, and Task 01 owns the sole public `Betwixt` class.
- The 16 findings carried from `implementation-review--01.md` remain resolved: the plan retains the required task-note
  hierarchy and command inventory, exact construct and overlap contracts, staged public exports, the 12-variant command
  matrix, optional-test collection rules, demo smoke paths, adapter fixtures, alias matrix, documentation inventory,
  CI and release topology, lockfile and documentation updates, resolved unknowns, per-task quality checks, and the
  package metadata distinction.


## Findings

### Summary

| Finding ID | Title                                                  | Outcome |
| ---------- | ------------------------------------------------------ | ------- |
| S01        | Declaration-time callable validation is not executable |         |
| S02        | Nested derivation invocation is not preserved          |         |
| S03        | Partial operations omit the changed context contract   |         |


### Significant

#### S01: Declaration-time callable validation is not executable

##### Where

Design Plan — AC05, approximately lines 118-128; Implementation Plan — Task 04 AC01 and Steps 1, 3, approximately
lines 371-405.


##### Issue

The design requires a context-aware callable to end in a keyword-only `ctx` parameter and makes both positional-only
and positional-or-keyword `ctx` declarations invalid. The implementation criterion repeats that rule, but the steps
only ask for tests of "rejection of positional `ctx`" and place signature enforcement in the runtime engine. They do not
require the declaration itself to fail, test both positional forms, or assert that the valid final parameter is injected
as `ctx=...`.


##### Impact

An implementation can accept an invalid callable declaration and fail only when translation runs, or can inject a
positional context value, while still appearing to satisfy the listed tests. That violates the changed public contract
and makes declaration errors depend on the operation path.


##### Suggestion

Make Task 04 require a declaration-time signature matrix: a callable ending in `*, ctx` is accepted and receives the
value only as `ctx=...`; `ctx` declared positional-only and positional-or-keyword each cause a Betwixt-owned declaration
error while the mapping declaration is built. Exercise map, reduce, and project callables in both directions, and put
signature inspection before producer execution, whether the implementation stores the validator in the compiler or the
engine.


##### Outcome


#### S02: Nested derivation invocation is not preserved

##### Where

Design Plan — AC06, approximately lines 131-144; Implementation Plan — Task 05 AC02 and Steps 1-4, approximately lines
420-436.


##### Issue

The design deliberately makes `context_rightward` and `context_leftward` different from context-aware translation
callables: each derivation receives the outer context exactly once as its sole positional argument, and its result is
reused for every nested container element. Task 05 specifies the once-and-reuse behavior, but does not specify the
positional call form or say that direct-callable `ctx` validation does not apply to derivations. Its test list mentions
keyword-only propagation and positional `ctx` rejection without identifying this exception.


##### Impact

An implementation can pass a derivation as `ctx=...` or reject a positional-only derivation while implementing the
otherwise correct container reuse rule. Nested context derivation would then be incompatible with the approved design,
especially for derivations that intentionally declare a positional-only argument.


##### Suggestion

Extend Task 05 AC02 to require `derive(outer_context)` with exactly one positional argument, no `ctx=` injection, once
per outer nested field, with the result reused for all elements. Add both-direction tests using a positional-only
derivation, explicit identity, explicit `None`, omitted derivation, and a call counter. Keep positional `ctx` rejection
tests scoped to nested inner translation callables, not the derivation selectors.


##### Outcome


#### S03: Partial operations omit the changed context contract

##### Where

Design Plan — AC02 and AC06, approximately lines 34-38 and 131-144; Implementation Plan — Task 06 AC01-AC05 and Steps
1-4, approximately lines 447-469.


##### Issue

The design says callers provide one context object per operation and that direct context-aware callables receive it as
`ctx=...`. Partial operations are public operations and can execute maps, reductions, and nested inner operations, but
Task 06 never states that partial methods accept context or that partial producers use the new keyword-only injection.
Its tests cover sparse shapes and nested containers without any context-aware partial callable or derivation case.


##### Impact

The executor can implement the new contract for full translation while partial map, reduction, or nested paths omit
context, pass it positionally, or invoke derivations per element. Full and partial translations would then expose
different callable APIs despite sharing the public contract.


##### Suggestion

Add to Task 06 that partial operations accept `context`, pass it unchanged to direct context-aware producers only as
`ctx=...`, and apply the nested derivation positional-once rule at each partial nesting boundary. Add both-direction
partial tests for map, reduction, and nested callables, including a keyword-only `ctx`, `None` and identity derivations,
and a per-boundary counter. If partial operations are intentionally context-free, state that exception explicitly in
the design plan instead of leaving the scope implicit.


##### Outcome


## Notes

The design plan itself is internally consistent on the changed distinction: direct context-aware translation callables
use a final keyword-only `ctx`, while nested context derivations receive the outer context positionally. The latest
design review remains clean on the earlier architecture, adapter, documentation, and delivery decisions. The
implementation plan also retains the intentional level-five task technical-note heading required by the canonical
implementation-plan artifact, despite the formatter warning against H5 headings.
