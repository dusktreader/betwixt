# Design Plan Review: Betwixt core mapping layer, documentation, and delivery

**Iteration 02**


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/design-plan.md
```


## Overview

The review surfaced findings:

- **Critical**: 1
- **Significant**: 7
- **Trivial**: 0


## Prior Review Resolution

- **C01** ✓: Full projections now return destination instances that are extracted into field values, partial projections
  are skipped, and partial reductions require complete source presence.
- **C02** ✓: AC10 defines literal, zero-argument factory, and required-default forms, the `defaults` call-site mapping,
  missing-default errors, and the absence of context for default factories.
- **S01** ⚠: Directional construct families, operation names, field references, and callable ordering are now stated,
  but declaration signatures and context-derivation call shapes remain undefined.
- **S02** ✓: AC17 and AC18 define annotation normalization, compatibility, supported nested shapes, and mismatch rules.
- **S03** ✓: AC21 names the optional extra and version range, defines missing-dependency behavior and native construction,
  and covers aliases; AC26 adds the corresponding matrix and failure tests.
- **S04** ✓: AC19 defines exact, MRO, built-in, duplicate, replacement, registry-lifetime, and declaration-snapshot
  behavior.
- **S05** ✓: AC12 makes partial operations mapping-only, requires caller-side normalization, and defines invalid keys,
  malformed nested values, and presence semantics.
- **S06** ✓: AC18 defines the supported nested grammar, tuple and dictionary rules, optionality, empty containers, and
  set hashability behavior.
- **S07** ✓: AC22 defines ownership and propagation for declaration, adapter, callable, context, traversal, and native
  construction failures; the phase exit criteria add corresponding coverage requirements.
- **S08** ✓: AC24 through AC26 establish phased delivery and phase-specific exit criteria.
- **T01** ✗: The plan removed the `Unknowns` section instead of replacing it with the required explicit no-unknowns
  statement in that section.
- **T02** ✓: The mechanics called out in the prior review are no longer prescribed in Technical Notes.


## Findings

### Summary

| Finding ID | Title                                                      | Outcome |
|------------|------------------------------------------------------------|---------|
| C01        | Required `Unknowns` section is missing                     |         |
| S01        | Public declaration signatures remain incomplete            |         |
| S02        | Context-aware callable and derivation contracts are vague  |         |
| S03        | Partial implicit-field behavior is unspecified             |         |
| S04        | Partial nested containers lack a shape contract             |         |
| S05        | Pydantic alias construction remains ambiguous               |         |
| S06        | CI coverage and artifact retention gates are unquantified   |         |
| S07        | Optional Pydantic examples conflict with the base run      |         |


### Critical

#### C01: Required `Unknowns` section is missing

##### Where

Design Plan structure — between Architecture, ending at line 379, and Technical Notes, beginning at line 381


##### Issue

The canonical design-plan structure requires an `Unknowns` section. The plan has no `## Unknowns` heading and instead
places the statement that no unresolved design questions remain in Technical Notes at line 392. The prior review asked
for an explicit no-unknowns statement in that section, not for the section to be removed.


##### Impact

The artifact still fails the required structure, and the review workflow has no canonical location for recording design
questions and their resolutions. Downstream planning cannot distinguish a deliberate absence of unknowns from an omitted
review section.


##### Suggestion

Add an `## Unknowns` section after Architecture containing a direct statement that no unresolved design questions remain,
or list each remaining question there. Keep unrelated technical context in Technical Notes.


##### Outcome

Accepted and applied: the revised plan restores the required `Unknowns` section and explicitly states that no unresolved design questions remain.

----

### Significant

#### S01: Public declaration signatures remain incomplete

##### Where

Acceptance Criteria — lines 37-81; Architecture — lines 287-296


##### Issue

AC03 now enumerates the construct names and broad input/output shapes, but it does not define how each construct is
declared. The plan leaves the placement of source references and destination fields, the callable slots for pairwise
constructs, the declaration form for defaults, and the attachment of nested context derivations to an implementation
choice. AC05's reference to a callable's "declared callable contract" does not identify that contract.


##### Impact

Two implementations can satisfy the stated taxonomy while exposing incompatible declaration APIs. Documentation and
tests cannot establish a stable public compatibility boundary, and the unresolved signature choices affect every
construct family rather than an isolated internal representation.


##### Suggestion

Add a public declaration matrix that states, for every construct family and direction, the source references, destination
field or object, callable position and arguments, optional context derivation, and full-versus-partial participation.
Also state the public operation exports. Keep storage and dispatch mechanics for the implementation plan.


##### Outcome

Accepted and applied: the revised plan adds a declaration matrix covering every construct's references, callable slots, context selectors, and partial behavior.


#### S02: Context-aware callable and derivation contracts are vague

##### Where

Acceptance Criteria — lines 67-81; Architecture — lines 321-327


##### Issue

The plan says a callable may opt into a final positional `ctx` value when its "declared callable contract" includes it,
and says nested constructs use a declared directional derivation. It never defines how context-aware behavior is declared,
what arguments a derivation receives, what it returns, or whether a derivation runs once per nested container or once per
element. The behavior when the operation context itself is `None` is also not distinguished from an omitted context.


##### Impact

Implementations can silently omit context, pass it to the wrong callable, or derive different contexts for list, tuple,
dictionary, and set traversal. The promised transitive context inventory is not testable, and user callables may observe
different values without violating the current wording.


##### Suggestion

Define the observable callable and derivation contracts: how a callable declares context awareness, the exact positional
arguments for each construct, the derivation input and result, the per-boundary invocation rule for containers, and the
meaning of an explicit `None` context. Add success and exception-propagation criteria for direct and nested calls.


##### Outcome

Accepted and applied: the revised plan defines final-positional context handling, nested derivation inputs and results, container invocation reuse, explicit `None`, and exception propagation.


#### S03: Partial implicit-field behavior is unspecified

##### Where

Acceptance Criteria — lines 86-91 and 129-162; Architecture — lines 316-319


##### Issue

AC07 defines compatible same-name fields for full translation, but AC12 through AC16 describe only explicit partial maps,
nested constructs, reductions, projections, and defaults. The plan does not say whether a present compatible same-name key
is copied implicitly in a partial operation, whether an incompatible same-name key is omitted, or how partial implicit
writes participate in overlap ordering. The Architecture phrase "only derived fields" does not resolve this.


##### Impact

A common patch can omit fields that the full contract would map or can include fields an implementation treats as
explicit-only. Callers cannot predict the patch for same-name updates, and implementations can disagree while passing the
listed partial acceptance criteria.


##### Suggestion

Add an explicit partial rule. For example: seed a patch from every present compatible same-name field, omit absent and
incompatible implicit fields, apply explicit declarations in class-body order, and never apply defaults. If partial
implicit mapping is intentionally unsupported, state that equally explicitly and add its omission as an acceptance case.


##### Outcome

Accepted and applied: the revised plan seeds partial patches from present compatible same-name fields, omits incompatible or absent fields, and applies explicit declarations afterward without defaults.


#### S04: Partial nested containers lack a shape contract

##### Where

Acceptance Criteria — lines 137-143 and 176-186; Architecture — lines 321-327


##### Issue

AC18 defines the declaration grammar and general runtime shapes, but the partial rules only describe a nested scalar value
as a mapping or `None`. They do not define how partial traversal handles lists, variadic or fixed tuples, dictionaries,
sets, nested optional containers, empty containers, dictionary keys, or a malformed element in a container. AC25 asks for a
matrix without making that matrix part of the observable contract.


##### Impact

An implementation may treat a container as one inner mapping, recurse over every element, reject partial containers, or
produce different patch shapes. Partial nested updates and their failure boundaries will therefore vary across adapters.


##### Suggestion

Add a partial container matrix that states the required input and output shape for every supported container, recursive
element presence rules, key pass-through, `None` and empty-container behavior, and the ownership of invalid-element and
set-hashability errors. Alternatively, explicitly limit partial nested traversal to scalar values.


##### Outcome

Accepted and applied: the revised plan defines recursive partial traversal for every supported nested container, including optional values, empty containers, keys, malformed elements, and set hashability.


#### S05: Pydantic alias construction remains ambiguous

##### Where

Acceptance Criteria — lines 209-217; Architecture — lines 298-306


##### Issue

AC21 requires Betwixt field names and patch keys to remain canonical while also requiring construction through Pydantic's
native validation boundary. It does not state how a destination model configured with an alias or validation alias that
does not accept the field name is constructed. Saying that aliases affect only Pydantic's own interfaces does not define
whether Betwixt requests name-based validation or rejects that model configuration.


##### Impact

A valid translation can fail at the destination boundary, or an implementation can bypass native validation to force
canonical names through. Alias behavior, defaults, coercion, and validation failures will differ between conforming
adapters, undermining the promised native Pydantic boundary.


##### Suggestion

Choose and state the alias bridge explicitly: either require the native validation path to accept canonical field names
regardless of alias configuration, or declare alias-only configurations unsupported. Cover validation aliases, source and
destination aliases, native defaults, coercion, and validation failures in the Pydantic acceptance criteria.


##### Outcome

Accepted and applied: the revised plan requires canonical-name Pydantic construction through native validation and rejects alias-only configurations instead of bypassing validation.


#### S06: CI coverage and artifact retention gates are unquantified

##### Where

Acceptance Criteria — lines 277-282; Architecture — lines 368-378


##### Issue

AC29 requires a coverage threshold and a defined retention period but specifies neither the threshold nor the period. The
Technical Notes define the Python versions, but they do not resolve these two release-gate values.


##### Impact

The quality gate has no deterministic pass/fail target. An implementation can select an arbitrarily low coverage bar and
an arbitrary artifact lifetime while still claiming conformance, and reviewers cannot verify release readiness from the
design plan.


##### Suggestion

State the numeric coverage threshold and artifact retention duration, or reference an existing repository policy that
defines both. Make the policy apply to test results, coverage, documentation, and distribution artifacts alike.


##### Outcome

Accepted and applied: the revised plan fixes the existing 85% coverage threshold and 14-day artifact retention period and assigns reports and release checks to the CI matrix.


#### S07: Optional Pydantic examples conflict with the base run

##### Where

Acceptance Criteria — lines 209-217 and 270-274; Architecture — lines 355-365


##### Issue

The examples architecture includes an optional Pydantic example, while AC28 says a clean supported-Python environment can
run every example and the CLI smoke test. The plan does not say whether that clean environment includes the optional extra.
The base environment is explicitly tested without Pydantic in AC21 and AC26.


##### Impact

The base CI job cannot satisfy the literal "every example" requirement without installing the optional dependency, while
the Pydantic job may skip the example without violating an alternative reading. The example and documentation release
gates therefore have no single executable target.


##### Suggestion

Split the criterion by dependency variant: require the dataclass examples and CLI to run in the base environment, and
require the Pydantic example and any Pydantic CLI path to run in the `pydantic` extra environment. State whether the CLI
must pass in both variants.


##### Outcome

Accepted and applied: the revised plan separates base dataclass example requirements from Pydantic-extra example requirements and requires the core CLI in both dependency variants.

----

## Notes

S01 and S02 are related but distinct: S01 needs the public declaration surface, while S02 needs the callable and context
semantics that surface must expose. S03 and S04 should be resolved together because implicit seeding and recursive
container traversal determine the complete partial-patch contract.

S05 is a residual edge of the prior Pydantic finding, not a request to replace native validation. S06 and S07 affect the
release gates independently of the core mapping semantics.
