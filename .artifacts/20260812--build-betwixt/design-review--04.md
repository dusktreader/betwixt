# Design Plan Review: Betwixt core mapping layer, documentation, and delivery

**Iteration 04**

This re-review checks the approved prior review and focuses on the new SQLAlchemy adapter contract, dependency
matrix, runnable cross-adapter example, Zensical migration, and implicit-mapping controls.


## Source Artifact

```text
/home/dusktreader/src/dusktreader/betwixt/.worktrees/feat/NO-TICKET--build-betwixt/.artifacts/20260812--build-betwixt/design-plan.md
```


## Overview

The review surfaced findings:

- **Critical**: 0
- **Significant**: 6
- **Trivial**: 0


## Prior Review Resolution

`design-review--03.md` reported zero findings at every severity level. There are no prior findings to carry forward.


## Findings

### Summary

| Finding | Title                                                               | Outcome |
| ------- | ------------------------------------------------------------------- | ------- |
| S01     | SQLAlchemy requiredness and defaults are undefined                  |         |
| S02     | SQLAlchemy unloaded relationships lack a contract                   |         |
| S03     | The SQLAlchemy escape hatch is not a public contract                |         |
| S04     | The dependency matrix assigns the cross-adapter example incorrectly |         |
| S05     | The Zensical migration does not make MkDocs replacement testable    |         |
| S06     | Implicit-mapping controls lack invalid-anchor semantics             |         |


### Significant

#### S01: SQLAlchemy requiredness and defaults are undefined

##### Where

Acceptance Criteria AC07 and AC22, approximately lines 156-162 and 323-350; Architecture, approximately lines 458-464


##### Issue

AC07 requires Betwixt to reject missing required destination fields, while allowing native destination defaults. AC22
also says that SQLAlchemy owns Python-side defaults and that construction uses normal mapped-model construction. The
plan never defines how the SQLAlchemy adapter determines whether a mapped attribute is required or has a usable native
default. An annotation's optionality, column nullability, Python-side default, server-side default, and relationship
default can produce different answers, especially when no session or flush is available.


##### Impact

Different implementations can either raise `UnmappedFieldError`, omit a value and let SQLAlchemy construct a partially
initialized object, or claim that a server-side default satisfies a pre-construction requirement. The native adapter
boundary and its tests will therefore disagree about missing fields.


##### Suggestion

Define a SQLAlchemy requiredness table covering annotated optionality, nullability, Python-side defaults, server-side
defaults, and relationship defaults. State which defaults Betwixt may rely on before construction and require explicit
tests for missing values in full and partial operations.


##### Outcome

Accepted and applied: the plan now defines SQLAlchemy constructibility for optional, nullable, Python-defaulted, and relationship-defaulted fields, while excluding server-side defaults from pre-construction satisfaction.

#### S02: SQLAlchemy unloaded relationships lack a contract

##### Where

Acceptance Criterion AC22, approximately lines 333-344; Architecture, approximately lines 458-464


##### Issue

The plan says the adapter reads mapped relationship attributes but does not trigger relationship loading. Ordinary
attribute access on an unloaded SQLAlchemy relationship can trigger a lazy load or raise when the instance is detached
or
configured with raise-on-lazy behavior. The plan does not say how the adapter detects unloaded state, or whether full
translation raises, partial translation omits, or both modes propagate an error.


##### Impact

An implementation can perform hidden database I/O despite the explicit no-session boundary, or fail with a native
exception whose meaning varies by loader strategy. Callers cannot know whether a translation is safe for detached or
partially loaded ORM instances.


##### Suggestion

Specify that the adapter checks load state before reading a relationship and never invokes a loader. Define the full and
partial outcomes for an unloaded source field, preferably an actionable Betwixt-owned unloaded-field error for full
translation and an explicit omission rule for partial translation, with tests for lazy, detached, and raise-on-lazy
cases.


##### Outcome

Accepted and applied: the SQLAlchemy adapter now checks relationship load state, raises an owned error for unloaded fields during full translation, and omits them during partial translation without triggering loaders.

#### S03: The SQLAlchemy escape hatch is not a public contract

##### Where

Acceptance Criterion AC22, approximately lines 335-339


##### Issue

AC22 says unsupported annotations, unmapped attributes, hybrid properties, and association proxies can use an explicit
map callable, an explicit field map, or a user adapter. The public taxonomy defines no "explicit field map", and the
adapter is explicitly limited to mapper-exposed attributes. The plan also does not say whether whole-object reductions
or projections may intentionally read unsupported descriptors.


##### Impact

The plan promises a route around the native SQLAlchemy boundary that an implementation planner cannot identify or test.
Users may expect `field_refs` to expose ignored descriptors even though the adapter is required not to expose them, or
may receive an undocumented second mapping API.


##### Suggestion

Either remove "explicit field map" from AC22 or define it as a public construct with its field-discovery and error
rules. State explicitly whether `reduce_*` and `project_*` whole-object callables may access arbitrary ORM attributes;
otherwise require a custom adapter for every descriptor outside the native boundary.


##### Outcome

Accepted and applied: the plan removes the undefined explicit-field-map escape hatch and makes custom adapters the public route for unsupported SQLAlchemy descriptors, while documenting responsibility for whole-object callables.

#### S04: The dependency matrix assigns the cross-adapter example incorrectly

##### Where

Acceptance Criterion AC29, approximately lines 410-419; Examples and CLI architecture, approximately lines 524-533;
CI/CD architecture, approximately lines 542-548


##### Issue

The `sqlalchemy`-only environment is required to run an "ORM-to-Pydantic User path", but that environment does not
contain the `pydantic` extra. The combined environment is the only variant with both adapters, and the documented
command at line 529 explicitly installs both extras. AC29 also requires the core CLI to pass in all four variants while
describing one CLI demo whose User case includes the SQLAlchemy-to-Pydantic boundary, which cannot run in the base or
single-extra environments.


##### Impact

The twelve-job matrix cannot satisfy its own example requirements. Implementers must either add undeclared dependencies,
silently skip the required path, or make the base CLI import optional integrations, undermining the absent-extra
contract.


##### Suggestion

Add an explicit variant table: run the core, dependency-free CLI in all four variants; run the Pydantic-only example in
`pydantic`; run SQLAlchemy-only smoke coverage in `sqlalchemy`; and run the SQLAlchemy-to-Pydantic User example only in
`pydantic+sqlalchemy`. Require the combined command and its deterministic output in that final variant.


##### Outcome

Accepted and applied: the dependency-variant requirements now reserve SQLAlchemy-only smoke coverage for `sqlalchemy` and the SQLAlchemy-to-Pydantic example for the combined `pydantic+sqlalchemy` environment.

#### S05: The Zensical migration does not make MkDocs replacement testable

##### Where

Acceptance Criteria AC28 and AC30, approximately lines 397-435; Documentation architecture, approximately lines 488-519


##### Issue

The plan requires a `zensical.toml` site but does not state that Zensical is the sole local build, serve, CI, and
publish
toolchain. The repository currently has MkDocs commands, `docs/mkdocs.yaml`, and MkDocs/Material/mkdocstrings
dependencies. "Existing Material theme" and "Python API reference integration" do not identify their Zensical
configuration or compatible dependency boundary, and do not require the stale MkDocs path to stop being authoritative.


##### Impact

The implementation can leave two competing documentation systems, build the old site in CI, or lose the generated API
reference while still satisfying the literal requirement that a Zensical config file exists. The current main-branch
deployment path can also remain an unreviewed bypass of the stated release gate.


##### Suggestion

Require Zensical to be the only documented build and serve path, require local targets and every CI publish/build job to
invoke it, and remove or explicitly deprecate the MkDocs config and dependencies. Specify the Zensical theme variant,
API-reference extension and versions, and add a build assertion that a representative generated API page is present.
Require branch builds without publication and tag/manual publication as separate verified paths.


##### Outcome

Accepted and applied: the plan makes Zensical configured by `zensical.toml` the sole documentation toolchain, deprecates or removes MkDocs paths, and requires generated API-page verification for build and publish.

#### S06: Implicit-mapping controls lack invalid-anchor semantics

##### Where

Acceptance Criteria AC03 and AC07, approximately lines 58-69 and 140-160; public declaration matrix, approximately lines
95-97


##### Issue

The three `disable_implicit_*` declarations are defined to suppress a matching same-name mapping, but the plan does not
define what happens when their left and right references have different canonical names. `field_refs` makes such
cross-name references valid, so the declaration could silently become a no-op or suppress an unintended candidate. The
class-level `disable_implicit_mapping` setting has truth semantics, but no invalid-value or declaration-time validation
contract.


##### Impact

A typo in a disable declaration can leave a destination unmapped without an early error, while explanations and remedies
remain ambiguous about whether the declaration applied. Implementers may also disagree about whether a non-boolean class
setting is ignored or rejected.


##### Suggestion

Require every `disable_implicit_*` declaration to reference equal canonical field names and raise a Betwixt-owned
declaration error otherwise. Define the class setting as a boolean with declaration-time validation, and require
`explain_*` to report the global and per-field suppression reason separately from annotation incompatibility.


##### Outcome

Accepted and applied: the plan now requires equal canonical anchors for per-field implicit controls, validates the boolean global setting, and distinguishes suppression reasons in explanation reports.

## Notes

The `field_refs(left, right)` decision is internally consistent across the public contract and architecture. The plan
mentions `f(left)` only to explain why the new single helper avoids two calls; the documentation and runnable examples
should use `field_refs` rather than copying the blog's older `f(...)` spelling.

The global and per-field implicit-mapping decisions are otherwise coherent: the absent class setting defaults to false,
true disables both directions for full and partial operations, and explicit declarations remain able to write suppressed
fields. S06 addresses the missing invalid-input boundary rather than changing those semantics.

The canonical design-review schema requires `#####` field headings. The Markdown formatter reports those required H5
headings as warnings, so they are retained as an intentional artifact-format exception.
