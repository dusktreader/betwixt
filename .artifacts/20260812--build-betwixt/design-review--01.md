# Design Plan Review: Betwixt core mapping layer

This review tests the proposed first release against the blog specification and the repository's current
dependency and documentation boundaries.

**Iteration 01**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/design-plan.md
```


## Overview

The review surfaced findings:

- **Critical**: 2
- **Significant**: 8
- **Trivial**: 2


## Findings

### Summary

| Finding | Title                                                     | Outcome |
|---------|-----------------------------------------------------------|---------|
| C01     | Partial, reduction, and projection semantics conflict    |         |
| C02     | Required defaults have no call-site contract              |         |
| S01     | Public construct names and signatures are underspecified  |         |
| S02     | Annotation compatibility is undefined                     |         |
| S03     | Pydantic construction and packaging are underspecified   |         |
| S04     | Adapter lookup and registration semantics are incomplete  |         |
| S05     | Partial input normalization has conflicting ownership    |         |
| S06     | Nested container failure boundaries are incomplete       |         |
| S07     | Failure ownership and test coverage are too weak         |         |
| S08     | The first-release scope has no phase boundary            |         |
| T01     | Unknowns contains settled decisions and a long flat list |         |
| T02     | Technical Notes prescribe implementation mechanics       |         |


### Critical

#### C01: Partial, reduction, and projection semantics conflict

##### Where

Acceptance Criteria — lines 54-59 and 133-145; Architecture — lines 203-228


##### Issue

`project_*` is defined as receiving a complete source object and producing a complete destination object, but the
translation engine models every declaration as a contribution to a destination value set. The plan never says how a
projected instance becomes field contributions or how it is merged with implicit fields and later declarations.

The partial rules introduce a second contradiction. A partial projection receives a sparse dictionary even though the
projection callable is otherwise defined against a complete typed object. A `reduce_*` construct receives a whole
source object and declares no source fields, yet AC17 says it runs when all declared source fields are present.


##### Impact

There is no single implementable or testable contract for two core construct families. Different implementations could
construct and validate a full object, merge a mapping, pass a sparse dictionary, or omit the declaration, all while
claiming conformance. Partial patches could also call user functions with the wrong type and silently produce the
wrong field set.


##### Suggestion

Define the exact input and output of each construct in both modes. For full projection, choose whether the callable
returns a destination instance or a field mapping, then define its merge order with implicit and field-level values.
For partial projection, either require a sparse-to-patch callable contract or explicitly reject/skip it. For partial
reductions, either declare their required source dependencies or require complete input and define the failure. Add
acceptance criteria for minimal sparse input, missing projection dependencies, and projection output conflicts.


##### Outcome


----

#### C02: Required defaults have no call-site contract

##### Where

Acceptance Criteria — lines 61-65; Architecture — lines 179-189; Technical Notes — lines 259-262


##### Issue

AC06 introduces a required-value marker and says the value must be supplied at translation time, but no operation
parameter or lookup namespace supplies it. The plan also does not say whether a late-bound default is zero-argument,
context-aware, or both. The blog specification itself shows both a zero-argument factory description and a
context-accepting default example. The plan does not resolve that inconsistency, and AC08 only describes context for
translation callables generally.


##### Impact

The required-default path cannot be implemented or documented consistently. Callers may pass the value through a
nonexistent keyword, context, or default override, and the promised "clear" failure has no defined trigger or error
boundary.


##### Suggestion

Specify the default contract completely: accepted value forms, the call-site channel for `...`, whether factories
receive context, and the error when the value is absent. If context-aware defaults are out of scope, state that
explicitly and route context-dependent computation through `reduce_*`. Add success and missing-value acceptance
criteria for both directions.


##### Outcome


----

### Significant

#### S01: Public construct names and signatures are underspecified

##### Where

Acceptance Criteria — lines 33-37 and 54-59; Architecture — lines 179-189


##### Issue

The architecture names the verbs `map`, `reduce`, `project`, `nested`, and `default`, but does not enumerate the
authoritative directional forms such as `map_pairwise`, `map_rightward`, `reduce_leftward`, or the nested context
variants. It also does not define the public field-reference and callable argument contract precisely enough to tell
single-input from multi-input calls, or how a class body distinguishes declarations from helper attributes.


##### Impact

An implementation plan can choose a different public API while satisfying the prose. Documentation and tests cannot
serve as a stable compatibility boundary, which defeats the design specification's goal of making direction visible.


##### Suggestion

List the public construct families and directional names from the specification, along with their observable inputs,
outputs, field-reference requirements, and context behavior. State the public translation and partial operation names
and the package-level symbols they expose. Leave internal collection machinery to the implementation plan.


##### Outcome


#### S02: Annotation compatibility is undefined

##### Where

Acceptance Criteria — lines 39-52 and 90-100; Architecture — lines 214-219; Technical Notes — lines 263-264


##### Issue

"Compatible annotations" and "container shape must agree" are not defined. The plan does not specify behavior for
`Any`, optional unions, `Annotated`, forward references, subclasses, aliases, or differing generic arguments. It also
does not say whether a same-name field with incompatible annotations is ignored so an explicit mapping can replace it,
or rejected as a declaration error.


##### Impact

Implicit mapping and declaration-time nested validation will vary by implementation. Users cannot predict when an
explicit mapping is required, and destination construction may become the accidental place where structural errors
surface.


##### Suggestion

Define the annotation compatibility predicate and normalization rules, including forward-reference resolution and
container recursion. State the behavior for every same-name mismatch and the supported annotation grammar for nested
containers. Add boundary acceptance criteria for optional, generic, and incompatible fields.


##### Outcome


#### S03: Pydantic construction and packaging are underspecified

##### Where

Goal — lines 15-19; Acceptance Criteria — lines 96-100; Architecture — lines 231-237


##### Issue

The plan commits to a Pydantic v2 optional extra without naming the extra, supported Pydantic range, compatibility
matrix, or behavior when the dependency is absent. "Native construction boundary" is also ambiguous: it does not say
whether the adapter invokes normal Pydantic validation, bypasses it, applies field names or aliases, or propagates
model defaults and validation errors.


##### Impact

Package metadata, lockfile updates, CI coverage, and the adapter's most important correctness boundary remain open.
Two conforming implementations could either coerce values through Pydantic or bypass validation, producing different
models and error behavior.


##### Suggestion

Name the optional extra and supported Pydantic version range, define import and missing-dependency behavior, and state
the destination construction contract. Specify how Betwixt field names interact with Pydantic aliases and require
native validation or explicitly require bypassing it. Add tests for the extra's presence and absence, aliases,
defaults, and validation failures.


##### Outcome


#### S04: Adapter lookup and registration semantics are incomplete

##### Where

Acceptance Criteria — lines 81-107; Architecture — lines 192-201


##### Issue

"Specific registration first" does not define whether lookup uses exact type identity, inheritance, MRO, or generic
origin. The plan also omits duplicate-registration behavior, conflict resolution, registry scope and lifetime, and
whether a twixt captures adapters at declaration time or looks them up on every call.


##### Impact

Import order or a later custom registration can change which adapter a twixt uses. Custom overrides are therefore not
predictable, and tests cannot isolate registry state or establish a stable failure mode for conflicting registrations.


##### Suggestion

Specify resolution order, exact-versus-inherited matching, duplicate and override policy, registry scope, and lookup
timing. Define whether a custom adapter replaces built-in support for the exact type and how registration failures are
reported.


##### Outcome


#### S05: Partial input normalization has conflicting ownership

##### Where

Acceptance Criteria — lines 133-145; Architecture — lines 222-228; Technical Notes — lines 265-266


##### Issue

AC16 says a partial operation may accept a sparse dictionary or an input model normalized to a dictionary. The
Technical Notes instead place normalization at the application boundary and specifically say Betwixt should not
interpret Pydantic unset sentinels. The plan also leaves unknown keys, wrong-side keys, non-mapping input, and nested
model-versus-dictionary values unspecified.


##### Impact

Callers cannot know whether model inputs are supported by Betwixt or must be normalized first. Nested partial
translations can receive a value shape the inner operation does not accept, and malformed patches may be silently
ignored or passed through to persistence.


##### Suggestion

Choose one boundary: accept mappings only and require callers to normalize models, or define a documented adapter
protocol for explicit-set model extraction. Define unknown-key and invalid-input behavior, including recursive nested
normalization, and add failure acceptance criteria.


##### Outcome


#### S06: Nested container failure boundaries are incomplete

##### Where

Acceptance Criteria — lines 109-129; Architecture — lines 214-219; Unknowns — lines 251-254


##### Issue

The plan promises scalar, list, variadic tuple, set, dictionary, and optional traversal but does not define the full
shape matrix. It leaves dictionary key annotation handling, fixed-length tuples, nested optional mismatches, `None`
versus non-optional destinations, and translated values that are not hashable for a set unresolved.


##### Impact

Declaration-time validation and runtime behavior will diverge across adapters. A mapping can pass structural checks and
then fail only after traversing a collection, or silently preserve keys whose types no longer match the destination.


##### Suggestion

Publish an explicit supported annotation grammar and matching rule for each container level. Define key policy,
optional compatibility, tuple limitations, set-construction failures, and the exception boundary for unsupported or
mismatched shapes. Add empty, `None`, and representative invalid-container acceptance criteria.


##### Outcome


#### S07: Failure ownership and test coverage are too weak

##### Where

Acceptance Criteria — lines 147-160; Unknowns — lines 249-254


##### Issue

AC19 names only a subset of failure modes. It does not require behavior for missing context or context derivation,
exceptions raised by user callables, destination constructor or Pydantic validation failures, malformed partial input,
registry conflicts, or nested traversal failures. AC18 says Betwixt does not validate, but does not distinguish errors
that should propagate from errors the framework must diagnose.


##### Impact

The most consequential boundaries can remain accidental while the test suite still satisfies AC19. Consumers will not
know which exception types and failure locations are stable, making debugging and compatibility across adapters poor.


##### Suggestion

Define error ownership for declaration checks, adapter lookup, user callables, context access, nested traversal, and
destination construction. State which exceptions propagate unchanged and which framework errors are actionable. Expand
AC19 to cover these boundaries and malformed partial inputs rather than relying on a generic "representative" set.


##### Outcome


#### S08: The first-release scope has no phase boundary

##### Where

Goal — lines 10-19; Acceptance Criteria — lines 22-167


##### Issue

The plan calls this the smallest useful release while combining five construct families, bidirectional dispatch,
declaration-time typing, a registry, custom adapters, nested traversal across several generic containers, runtime
context, partial patches, an optional Pydantic integration, documentation, and broad failure tests. The repository is
currently a skeleton, and several of these features still lack settled semantics.


##### Impact

The release becomes an all-or-nothing implementation with a large interaction surface. Basic dataclass mappings can be
blocked by unresolved partial or Pydantic decisions, while the broad acceptance list makes verification shallow.


##### Suggestion

Either justify why every listed capability is a v0.1 requirement and define sequencing and exit criteria, or split the
scope. A defensible first slice would establish dataclass adapters and field-level full translations, then add nested,
partial, and Pydantic integrations after their contracts and failure matrices are proven.


##### Outcome


----

### Trivial

#### T01: Unknowns contains settled decisions and a long flat list

##### Where

Unknowns — lines 240-254


##### Issue

The section says there are no unresolved unknowns, then lists six fixed decisions rather than answerable questions.
Both the content and the section's purpose are therefore unclear. The six-item flat list also exceeds the artifact
guidance for a flat Unknowns list.


##### Impact

Reviewers cannot distinguish constraints already decided from questions that still require resolution, and the
artifact does not conform to the canonical section formatting.


##### Suggestion

Replace the section with a single statement if no unknowns remain, and move the fixed decisions into Architecture or
Technical Notes. If any remain, express them as specific questions and use subsections for a list larger than five.


##### Outcome


#### T02: Technical Notes prescribe implementation mechanics

##### Where

Technical Notes — lines 259-270


##### Issue

Signature inspection timing, annotation-introspection mechanics, public typing preservation, and compiling metadata
once per twixt describe HOW rather than the design's required behavior. The design-plan guidance explicitly reserves
such implementation details for the implementation plan.


##### Impact

The plan unnecessarily constrains implementation choices and mixes architectural requirements with optimization and
mechanism details, making it harder to identify the actual public contract.


##### Suggestion

Keep the observable contracts: context is per-call, annotations drive structural checks, and repeated introspection
should not dominate ordinary translation if that is a requirement. Move signature inspection, cache timing, and other
mechanics to the implementation plan.


##### Outcome


## Notes

C01 blocks approval of the partial and projection portions of the release. S05 is the input-boundary part of the same
problem and should be resolved with it rather than independently.

C02 and S03 overlap around context-aware defaults and destination construction. S02 is a prerequisite for S06, since
container matching cannot be specified without a general annotation compatibility rule.

S08 is a scope recommendation, not a request to remove capabilities without human agreement. The orchestrator should
resolve the contract findings before asking whether the broad first-release scope is still justified.
