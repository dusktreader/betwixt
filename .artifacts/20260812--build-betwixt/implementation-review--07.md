# Implementation Plan Review: Betwixt core mapping layer, integrations, documentation, and delivery

This re-review checks both plans after the direct-callable context contract changed to a final keyword-only `ctx`,
rechecks all earlier implementation findings, and verifies alignment with the approved design.

**Iteration 07**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/implementation-plan.md
```


## Overview

The review rechecked the 16 findings from `implementation-review--01.md`, the three findings from
`implementation-review--04.md`, and the three findings from `implementation-review--06.md`. The latest plans resolve
the partial-operation context gap, but two executable details remain underspecified:

- **Critical**: 0
- **Significant**: 2
- **Trivial**: 0


## Prior Review Resolution

- `implementation-review--06.md` **S01** ⚠: The plans now state final keyword-only `ctx`, `ctx=...` injection, and
  rejection of positional forms, but they do not explicitly require declaration-time validation, both positional forms,
  or a family-complete map/reduce/project/nested test matrix.
- `implementation-review--06.md` **S02** ⚠: The plans now say derivations run positionally once and reuse their result,
  but do not explicitly require the exact one-positional-argument call with no `ctx=` injection or test a
  positional-only
  derivation selector.
- `implementation-review--06.md` **S03** ✓: Task 06 now covers partial `context`, direct `ctx=...` injection, nested
  derivation reuse, omitted and explicit-`None` derivations, identity derivation, both directions, and call counts.
- `implementation-review--04.md` **S01-S03** ✓: The independent nested pairwise callable contract, projection failure
  ownership, and sole `Betwixt` class/module ownership remain explicit.
- `implementation-review--01.md` **C01-C02, S01-S12, T01-T02** ✓: The required heading hierarchy exception, command
  inventory, construct surface, overlap rules, staged exports, variant matrix, optional-test collection, demo smoke,
  adapter fixtures, alias matrix, documentation inventory, CI and release gates, lockfile scope, resolved unknowns,
  task-level checks, and package metadata distinction remain present.


## Findings

### Summary

| Finding ID | Title                                                        | Outcome |
| ---------- | ------------------------------------------------------------ | ------- |
| S01        | Declaration-time callable validation is still underspecified |         |
| S02        | Nested derivation call form remains ambiguous                |         |


### Significant

#### S01: Declaration-time callable validation is still underspecified

##### Where

Design Plan — AC05, approximately lines 118-129; Implementation Plan — Task 04 AC01 and Steps 1, 3-4, and Task 05
Step 1, approximately lines 365-436.


##### Issue

The design requires context-aware direct map, reduce, project, and nested inner callables to end in a keyword-only
`ctx`, receive it only as `ctx=...`, and reject positional-only or positional-or-keyword `ctx` while the declaration is
built. Task 04 repeats the contract, but its test step only says "rejection of positional `ctx`". It does not name both
positional forms, require the failure before any operation runs, verify that `ctx` is final, or require map, reduce, and
project coverage in both directions. Task 05 separately mentions nested inner-callable rejection without defining the
same declaration-time matrix. The plan therefore leaves signature validation timing and coverage ambiguous.


##### Impact

An executor can validate an invalid callable only when translation runs, reject one positional form but not the other,
inject context positionally, or omit a callable family while still satisfying the generic test wording. Full and partial
operations can then expose different callable contracts, and declaration errors depend on which operation a caller first
invokes.


##### Suggestion

Add an explicit declaration-build acceptance criterion and test step covering every direct `map_*`, `reduce_*`, and
`project_*` callable plus each nested inner callable in both directions. Accept a context-aware callable only when `ctx`
is its final keyword-only parameter and inject it as `ctx=...`. Reject both positional-only and positional-or-keyword
`ctx` declarations with a Betwixt-owned declaration error before the mapping declaration completes. Instantiate invalid
declarations in tests and assert they fail before any translation call; also assert valid map, reduce, project, and
nested calls receive the context by keyword.


##### Outcome


#### S02: Nested derivation call form remains ambiguous

##### Where

Design Plan — AC06, approximately lines 132-143; Implementation Plan — Task 05 AC02 and Steps 1-4 and Task 06 AC06,
approximately lines 415-475.


##### Issue

The design distinguishes derivation selectors from direct translation callables: each selector receives the outer
context as exactly one positional argument, never through `ctx=...`, and its result is reused for every nested element.
The implementation plan says derivations run "positionally once" and its tests mention "positional-once derivation
selectors", but it never states the exact `derive(outer_context)` call shape, excludes keyword injection, or requires a
positional-only derivation test. This wording can be read as a call-count requirement rather than an invocation
contract.


##### Impact

An executor can call a derivation as `derive(ctx=outer_context)`, pass extra arguments, or apply the direct-callable
`ctx` validator to the selector. Full and partial nested translation would then violate the approved derivation API,
especially for a selector intentionally declared with a positional-only parameter.


##### Suggestion

Rewrite Task 05 AC02 and Task 06 AC06 to require `derive(outer_context)` with exactly one positional argument and no
`ctx=` injection, once per outer nested-field invocation, with the result reused for every element. Add both-direction
tests using a positional-only selector such as `def derive(outer_context, /): ...`, explicit identity, explicit `None`,
omitted derivation, and a call counter. Keep positional-`ctx` rejection tests scoped to nested inner translation
callables, not derivation selectors.


##### Outcome


## Notes

The design plan remains aligned with the requested distinction. AC05 covers final keyword-only direct `ctx` handling for
map, reduce, project, and nested inner callables; AC06 covers positional-once context derivation and container reuse.
The latest design review remains clean, so the outstanding issues are implementation-plan executability gaps rather than
design contradictions.

The latest Task 06 change fully resolves the prior partial-operation finding. It now explicitly covers context and
derivation semantics in both directions, including `ctx=...`, omitted and explicit-`None` derivations, identity
derivation, and per-boundary call counts. S01 and S02 should be resolved together so full and partial paths share one
unambiguous signature and derivation test matrix.

The Markdown check passed for the design plan. It reports only the required level-five task technical-note heading at
line 288 of the implementation plan; the implementation-plan artifact definition requires level five for those
subsections, so this is an intentional exception.
