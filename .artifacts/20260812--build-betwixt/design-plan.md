# Design Plan: Betwixt core mapping layer, documentation, and delivery

Betwixt is a peer-to-peer, declarative translation layer for two structured Python types. This plan fixes the
runtime contract for the skeleton release and includes native optional adapters for Pydantic v2 and SQLAlchemy ORM,
the browsable documentation, runnable examples, and gated delivery pipeline needed to make that contract usable and
verifiable.


## Goal

Build a small, explicit mapping layer that relates two peer types without modifying either type. A twixt exposes
direction-named full and partial operations, supports dataclasses in the base distribution, Pydantic v2 through an
optional extra, and SQLAlchemy 2.x mapped declarative classes through a separate optional extra. Each adapter
delegates validation and construction to the destination type system.

The release also turns the existing documentation skeleton into a Zensical site configured by `zensical.toml` and
distilled from the authoritative blog
specification. The site teaches the design through the User, Payment, and Order scenarios, not just through generated
API pages. CI verifies supported Python and dependency variants, examples, documentation, and package quality. Package
publishing occurs automatically after a validated pushed version tag, while documentation publishing occurs
automatically
after a qualifying merged pull request to `main`.


## Acceptance Criteria

### Public contract

#### AC01: A twixt identifies two peer types

A declaration relates a `left` type and a `right` type without requiring Betwixt-specific members on either type.
`rightward(value, *, context=None, defaults=None)` returns a new right instance from a left instance, and
`leftward(value, *, context=None, defaults=None)` returns a new left instance from a right instance. `context` and
`defaults` are keyword-only operation arguments; passing either positionally is invalid.


#### AC02: Directional operations are explicit

The public operations are `rightward`, `leftward`, `rightward_partial`, and `leftward_partial`. No operation infers an
inverse. Full operations return destination instances; partial operations return sparse `dict[str, Any]` patches.


#### AC03: The public construct taxonomy is stable

The package exposes exactly these directional construct names:

| Construct                    | Direction     | Source input                 | Destination output                     |
| ---------------------------- | ------------- | ---------------------------- | -------------------------------------- |
| `map_pairwise`               | both          | one or more named fields     | one named field                        |
| `map_rightward`              | left to right | one or more left fields      | one right field                        |
| `map_leftward`               | right to left | one or more right fields     | one left field                         |
| `reduce_rightward`           | left to right | complete left object         | one right field                        |
| `reduce_leftward`            | right to left | complete right object        | one left field                         |
| `project_rightward`          | left to right | complete left object         | complete right object                  |
| `project_leftward`           | right to left | complete right object        | complete left object                   |
| `nested_pairwise`            | both          | one referenced field         | one referenced field                   |
| `nested_rightward`           | left to right | one left field               | one right field                        |
| `nested_leftward`            | right to left | one right field              | one left field                         |
| `default_rightward`          | left to right | no source field              | one right field                        |
| `default_leftward`           | right to left | no source field              | one left field                         |
| `disable_implicit_pairwise`  | both          | one left and one right field | suppresses the matching implicit pair  |
| `disable_implicit_rightward` | left to right | one left and one right field | suppresses the rightward implicit pair |
| `disable_implicit_leftward`  | right to left | one left and one right field | suppresses the leftward implicit pair  |

`reduce_pairwise`, `project_pairwise`, and `default_pairwise` do not exist. `map_pairwise` and `nested_pairwise` each
require independently supplied directional behavior; they never synthesize an inverse. The three
`disable_implicit_*` declarations do not transform values. They suppress only the matching automatic same-name mapping,
while an explicit mapping may still write the fields.

The class-level `disable_implicit_mapping` setting is assumed to be `False` when it is absent. When explicitly defined
as `True`, it disables all automatic same-name mappings in both directions for full and partial operations. The
per-field `disable_implicit_*` declarations provide narrower opt-outs while the class-level setting remains `False`.

The public field-reference helper is `field_refs(left, right)`. It returns the two typed accessor proxies in the same
order as its arguments, conventionally assigned as `L, R = field_refs(left, right)`. This single helper makes the two
sides explicit at the declaration site without requiring separate `f(left)` and `f(right)` calls.

Every `disable_implicit_*` declaration must reference equal canonical field names on both sides. A differing pair is a
Betwixt-owned declaration error, not a silent no-op. `disable_implicit_mapping` is a boolean class setting; any other
value is a Betwixt-owned declaration error. Explanation reports distinguish global suppression from per-field,
direction-specific suppression.

Each twixt also exposes `explain_rightward()` and `explain_leftward()`, which return a structured declaration-time
`MappingExplanation`. These methods do not read a source value, call user code, derive context, or construct a
destination; they exist to show why each destination field is or is not produced.

The public declaration matrix is:

| Construct                    | Declaration signature and example                                                                                                                   | Source and destination refs                                                   | Callable keyword and arguments                                        | `via=` and context derivation                                            | Partial behavior                                                     |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| `map_pairwise`               | `map_pairwise(left=L.first, right=R.first, rightward=to_right, leftward=to_left)`                                                                   | Each direction reads its own side refs and writes the opposite-side field ref | `rightward(*left_values[, ctx])`; `leftward(*right_values[, ctx])`    | No `via=`; no derivation                                                 | Runs per direction when all referenced keys are present              |
| `map_rightward`              | `map_rightward(left=L.first, right=R.first, rightward=to_right)`                                                                                    | Left refs to one right destination ref                                        | `rightward(*left_values[, ctx])`                                      | No `via=`; no derivation                                                 | Runs when all referenced keys are present                            |
| `map_leftward`               | `map_leftward(right=R.first, left=L.first, leftward=to_left)`                                                                                       | Right refs to one left destination ref                                        | `leftward(*right_values[, ctx])`                                      | No `via=`; no derivation                                                 | Runs when all referenced keys are present                            |
| `reduce_rightward`           | `reduce_rightward(right=R.total, rightward=from_left)`                                                                                              | Complete left object to one right destination ref                             | `rightward(left_object[, ctx])`                                       | No `via=`; no derivation                                                 | Runs only when every left source key is present                      |
| `reduce_leftward`            | `reduce_leftward(left=L.total, leftward=from_right)`                                                                                                | Complete right object to one left destination ref                             | `leftward(right_object[, ctx])`                                       | No `via=`; no derivation                                                 | Runs only when every right source key is present                     |
| `project_rightward`          | `project_rightward(rightward=build_right)`                                                                                                          | Complete left object to the right object                                      | `rightward(left_object[, ctx])`                                       | No `via=`; no derivation                                                 | Skipped                                                              |
| `project_leftward`           | `project_leftward(leftward=build_left)`                                                                                                             | Complete right object to the left object                                      | `leftward(right_object[, ctx])`                                       | No `via=`; no derivation                                                 | Skipped                                                              |
| `nested_pairwise`            | `nested_pairwise(left=L.child, right=R.child, via=child_twixt, rightward=..., leftward=..., context_rightward=derive_r, context_leftward=derive_l)` | One nested field ref on each side                                             | Nested operations receive the nested value and optional derived `ctx` | `via=` names the inner twixt; derivations are directional and optional   | Runs when the source field is present; recurses into the value shape |
| `nested_rightward`           | `nested_rightward(left=L.child, right=R.child, via=child_twixt, rightward=..., context_rightward=derive)`                                           | One left nested field ref to one right nested field ref                       | Nested operations receive the nested value and optional derived `ctx` | `via=` names the inner twixt; `context_rightward=` derives inner context | Runs when the source field is present; recurses into the value shape |
| `nested_leftward`            | `nested_leftward(right=R.child, left=L.child, via=child_twixt, leftward=..., context_leftward=derive)`                                              | One right nested field ref to one left nested field ref                       | Nested operations receive the nested value and optional derived `ctx` | `via=` names the inner twixt; `context_leftward=` derives inner context  | Runs when the source field is present; recurses into the value shape |
| `default_rightward`          | `default_rightward(right=R.status, value="new")`                                                                                                    | No source ref to one right destination ref                                    | A literal, zero-argument factory, or `...`; no callable context       | No `via=` or derivation                                                  | Full only; skipped in partial operations                             |
| `default_leftward`           | `default_leftward(left=L.status, value="new")`                                                                                                      | No source ref to one left destination ref                                     | A literal, zero-argument factory, or `...`; no callable context       | No `via=` or derivation                                                  | Full only; skipped in partial operations                             |
| `disable_implicit_pairwise`  | `disable_implicit_pairwise(left=L.a, right=R.a)`                                                                                                    | One same-name field ref on each side                                          | No callable; suppresses both implicit directions                      | No `via=` or derivation                                                  | Suppresses both partial implicit directions for this pair            |
| `disable_implicit_rightward` | `disable_implicit_rightward(left=L.a, right=R.a)`                                                                                                   | One same-name field ref on each side                                          | No callable; suppresses rightward implicit mapping                    | No `via=` or derivation                                                  | Suppresses rightward partial implicit mapping for this pair          |
| `disable_implicit_leftward`  | `disable_implicit_leftward(left=L.a, right=R.a)`                                                                                                    | One same-name field ref on each side                                          | No callable; suppresses leftward implicit mapping                     | No `via=` or derivation                                                  | Suppresses leftward partial implicit mapping for this pair           |

`map_pairwise`, `nested_pairwise`, every directional construct, and the three `disable_implicit_*` declarations are
public declarations. The package exports all construct names in this matrix, the four translation operations in AC02,
the `field_refs` helper, the two diagnostic methods and their public report type, and the public declaration and error
types documented by the API reference. This matrix specifies only the declaration surface and observable calls;
internal storage and dispatch remain implementation choices.


#### AC04: Field references are typed and checked early

The public field-reference syntax is `L, R = field_refs(left, right)` followed by `L.field_name` or `R.field_name`.
Attribute access yields a typed field reference, not a string. Missing fields, wrong-side references, and incompatible
nested `via` types fail while the twixt declaration is built.


#### AC05: Callable inputs have deterministic ordering

`map_*` callables receive source field values in the order of the tuple or sequence in the source-side reference. A
single reference produces one positional value. `reduce_*` and `project_*` callables receive the complete source
instance as their first positional value. Nested inner calls receive the nested scalar or container element as their
normal inner-operation input. A callable is context-aware only when signature inspection finds a final keyword-only
parameter named `ctx`; otherwise it is called without context. Thus context-aware map, reduce, project, and nested inner
callables receive exactly the arguments shown in the matrix and receive `ctx` only as a keyword argument. A callable
that
declares `ctx` as positional-only or positional-or-keyword is an invalid declaration. Defaults always use a
zero-argument
factory and never receive `ctx`.


#### AC06: Context is per-call and explicitly propagated

Callers provide one `context` object per operation. The full and partial operation signatures require `context` and
`defaults` to be passed by keyword. Betwixt passes the same object unchanged to direct context-aware
callables as the keyword `ctx=...`. At each outer nested-field invocation, a declared directional derivation receives
the outer context exactly once as its sole positional argument and returns the inner context, either unchanged or
transformed; that one result is
reused for every element in a nested list, tuple, dictionary, or set. An omitted derivation selector means inner context
`None`. An explicit selector that returns `None` is a distinct declaration and runtime event, although both cases yield
`None` to the inner call. An explicit identity derivation is required to pass the outer context through. Derivation is
not rerun per container element. TypedDict, dataclass, attrs, and Pydantic context objects are supported by convention;
Betwixt does not inspect or validate their shape. User callable and derivation exceptions, including missing context
keys, propagate unchanged.


### Full translation semantics

#### AC07: Implicit fields have a defined compatibility rule

Same-name fields are implicit only when their normalized annotations are compatible and implicit mapping has not been
disabled globally or for that field and direction. Explicit declarations take precedence over implicit values. An
incompatible same-name field is omitted from implicit mapping, so an explicit construct may replace it.

`explain_rightward()` and `explain_leftward()` return one diagnostic entry for each destination field, including its
producer or lack of producer. Entries identify the canonical source and destination names where applicable, preserve
explicit declaration order, and distinguish an active implicit producer from an omitted same-name candidate. Omitted
candidates state whether normalized annotations are incompatible or implicit mapping is disabled globally or for that
field and direction. A field with no same-name candidate or explicit/default producer is reported as unmapped. The
`MappingExplanation` contains the direction, source and destination types, and ordered entries. Each entry contains a
canonical destination name, a status of `implicit`, `explicit`, `default`, `omitted`, or `unmapped`, and optional
canonical source name, normalized annotation descriptions, and omission reason. The report is stable enough for tests
and tooling; it does not execute translation.

During full translation, if a required destination field still has no value after implicit and explicit declarations and
defaults run, Betwixt raises a Betwixt-owned `UnmappedFieldError` before native destination construction. The error
names the direction, source and destination types, destination field, and, when relevant, the same-name source field,
both normalized annotations, and the omission reason. It points callers toward the corresponding explanation method
and the applicable remedies: add an explicit mapping, supply a default, or remove the implicit-mapping suppression.
Destination fields satisfied by a native destination default do not error. Native constructor or validation errors for
values that Betwixt supplied remain native errors.


#### AC08: Full maps and reductions are complete and ordered

`map_*` runs only when every referenced source field is available and writes one named destination field.
`reduce_*` receives a complete source instance and writes one named destination field. In a full operation, reductions
always run after their source instance exists. Callable results are not coerced by Betwixt.


#### AC09: Full projections return destination instances

A full `project_*` callable returns a fully constructed destination instance, not a mapping. The instance's declared
fields become the projection's complete baseline. Implicit values are seeded before explicit declarations; explicit
constructs execute in declaration order, and each later write, including a later projection, replaces an earlier value.
The destination adapter extracts fields from the projected instance before the final destination construction. Unknown
or unreadable projected fields are declaration or adapter errors, not silently discarded.


#### AC10: Defaults have a complete call-site contract

`default_*` accepts a literal, a zero-argument factory, or the required marker `...`. Defaults run only in full
operations after ordinary declarations and only for fields with no prior value. A zero-argument factory is called
without context. Context-dependent computation uses `reduce_*` instead.

Required defaults are supplied through the operation's `defaults` mapping, keyed by the destination field's canonical
Betwixt name, for example `defaults={"password_hash": value}`. A missing required entry raises a Betwixt-owned missing-
default error naming the field and direction. `defaults` is ignored by partial operations.


#### AC11: Overlap is deterministic

Declarations execute in class-body order. A later declaration writing the same destination field wins, including a
field-level declaration after a projection. The framework does not inspect callable bodies or warn about overlap.


### Partial translation semantics

#### AC12: Partial operations accept mappings only

`leftward_partial` and `rightward_partial` accept a mapping whose keys are canonical field names on the source side and
return a patch keyed by canonical destination field names. Callers must normalize model instances and Pydantic
explicit-set state before calling. Non-mapping input, keys not present on the source side, and malformed nested values
raise actionable Betwixt-owned input errors. `None` is present; an absent key is not.


#### AC13: Partial maps and nested constructs are sparse

A partial `map_*` runs only when all referenced keys are present. A partial `nested_*` runs when its source field is
present. A non-optional nested value must be a mapping for the inner partial operation; an optional value may be `None`
and yields `None`. A present nested model instance is not normalized implicitly. Inner patches are returned as the
nested field's patch value, and the inner operation uses the same partial rules recursively.

Partial implicit mapping first seeds the patch with each present, compatible same-name source field unless implicit
mapping has been disabled globally or for that field and direction. It omits absent same-name fields and present
incompatible same-name fields, then applies explicit declarations in class-body order. Explicit declarations therefore
overwrite a seeded implicit field when they target the same destination field. Defaults are never applied. An explicit
declaration can supply a destination field whose same-name source is absent or incompatible.

The partial nested container contract is:

| Source value shape     | Partial input                   | Returned patch shape                                    | Rule and error ownership                                                                       |
| ---------------------- | ------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Scalar nested value    | Mapping                         | Mapping patch                                           | Recurse once; malformed or non-mapping non-optional input is a Betwixt-owned input error       |
| Optional scalar        | Mapping or `None`               | Mapping patch or `None`                                 | `None` is preserved; non-optional inner errors remain Betwixt-owned                            |
| `list[T]`              | List                            | List of recursively returned element patches            | Traverse every element in order; malformed elements are Betwixt-owned input errors             |
| Variadic tuple         | Tuple                           | Tuple of recursively returned element patches           | Traverse every element in order and preserve tuple shape; malformed elements are Betwixt-owned |
| Fixed tuple            | Tuple of declared arity         | Tuple of recursively returned element patches           | Traverse by position and preserve arity; malformed elements are Betwixt-owned                  |
| `dict[K, T]`           | Dict                            | Dict with original keys and recursively returned values | Keys pass through unchanged; malformed values are Betwixt-owned input errors                   |
| `set[T]`               | Set                             | Set of recursively returned element patches             | Traverse every element; an unhashable returned patch raises the native set hashability error   |
| Empty container        | Empty list, tuple, dict, or set | Same empty container shape                              | No inner call occurs and no element error is raised                                            |
| Any optional container | Container or `None`             | Recursively shaped patch or `None`                      | `None` is preserved; the contained shape follows its row above                                 |

Traversal is recursive for nested containers. The outer nested field contributes one destination patch value with the
same container shape, and each scalar element contributes its inner partial patch. Inner Betwixt input errors remain
Betwixt-owned and identify the nested path; user callable, derivation, adapter, and set-insertion exceptions retain
their respective ownership from AC23. A present model instance is not normalized implicitly.


#### AC14: Partial reductions require complete source presence

A partial `reduce_*` runs only when every field of the source type is present in the input mapping. It then constructs a
source instance through the source adapter and calls the reduction with that instance. Otherwise it contributes nothing.
It never receives a sparse mapping.


#### AC15: Partial projections are explicitly unsupported

`project_*` is skipped by partial operations and contributes no patch values. A partial operation never calls a
projection with a sparse mapping and never pretends that a partial mapping is a complete source instance. Applications
needing a sparse projection use an ordinary `map_*` or an application-owned callable before invoking Betwixt.


#### AC16: Partial defaults are always skipped

Partial operations never apply literal defaults, factories, or required defaults. They include only values derived from
present input. This prevents an update patch from writing fields the caller did not mention.


### Types and adapters

#### AC17: Annotation compatibility is defined

Annotation normalization removes `Annotated` metadata and resolves forward references against the declaring type. `Any`
is compatible with every annotation for implicit mapping but cannot establish a nested element type by itself. A source
annotation is compatible with a destination annotation when it is the same normalized type, or a source class is a
subclass accepted by the destination class. Generic origins must match and their arguments must recursively match under
the same rule. Betwixt does not perform runtime coercion based on annotations.


#### AC18: Nested annotation grammar is explicit

The declarative nested grammar supports scalar twixt types, `T | None` or `Optional[T]`, `list[T]`, variadic
`tuple[T, ...]`, fixed tuples with equal arity and pairwise-compatible elements, `dict[K, T]`, and `set[T]`. Container
origins and element shapes must match across sides. Dictionary keys pass through unchanged and therefore require exactly
compatible key annotations. Fixed and variadic tuples do not match each other. Optional source to non-optional
destination and `None` to a non-optional nested value are declaration/input errors; non-optional to optional is allowed.

`Any`, unresolved forward references, custom containers, generic aliases whose origin is not in this list, root
wrappers, and discriminated unions require explicit `map_*` or `project_*` callables. A set traversal raises the
underlying hashability error if a translated element cannot be inserted. Empty containers preserve their declared shape.


#### AC19: Adapter lookup and registration are predictable

The process-local registry contains built-in adapters and user registrations. Lookup uses an exact registered type
first, then the nearest registered base in the type's MRO, then built-in type-family support. Generic origin matching is
not implicit. A registration for an exact type overrides built-in support; duplicate registrations raise unless the
caller explicitly requests replacement. Registrations are process-local and remain until replaced or process exit.

A twixt captures the resolved adapters when its declaration is built. Later registry changes do not mutate an existing
twixt; a new twixt sees the new registry state. Unsupported types raise an actionable missing-adapter error identifying
the type and registration contract. Adapter lookup, duplicate registration, and adapter failures are owned by Betwixt;
exceptions from adapter field access and construction propagate with their original cause attached.


#### AC20: Dataclass support has a native boundary

The base distribution supports standard-library dataclasses, including required fields, defaults, optional values, and
the supported container grammar. Destination instances are created through normal dataclass construction. Dataclass
constructor errors and user-defined post-init errors remain native errors at the destination boundary.


#### AC21: Pydantic support is optional and native

The optional extra is named `pydantic` and supports `pydantic>=2.7,<3`. Pydantic is installed as a regular development
dependency for the test environment but remains package-optional and is included only through the `pydantic` extra for
consumers. Canonical Betwixt names are passed to normal Pydantic validation. A destination Pydantic model must accept
canonical names through field names or validation
configuration; an alias-only or validation-alias-only configuration that rejects canonical names is an actionable
unsupported adapter configuration, not a reason to bypass validation. Source aliases, validation aliases, and
serialization aliases affect their respective Pydantic interfaces, not Betwixt field references or patch keys, which
always use canonical names. Pydantic defaults and coercion occur at the native destination boundary, and Pydantic
validation failures propagate as native validation errors. The source adapter reads canonical fields regardless of
source serialization aliases.

Without the extra, importing core Betwixt succeeds, but declaring a Pydantic side raises an actionable missing-optional-
dependency error. Pydantic and SQLAlchemy are regular development dependencies, so the development test environment can
collect and run all adapter tests without optional-import markers. They remain optional package dependencies exposed
only
through their respective extras. A separate isolated no-extras job verifies the missing-extra boundary. CI tests the
base, `pydantic`, `sqlalchemy`, and combined `pydantic+sqlalchemy` package variants separately, using the regular
development dependency set for each normal test job.


### Error ownership and non-goals

#### AC22: SQLAlchemy ORM support is optional and native

The optional extra is named `sqlalchemy` and supports `SQLAlchemy>=2.0,<3`. SQLAlchemy is installed as a regular
development dependency for the test environment but remains package-optional and is included only through the
`sqlalchemy` extra for consumers. It provides a native adapter for mapped
SQLAlchemy 2.x declarative classes, including mapped scalar attributes and mapped relationships whose annotations fit
the existing nested twixt grammar. The adapter discovers only ORM-mapped attributes exposed by the class mapper and
uses the mapped Python attribute name as Betwixt's canonical field name. A database column name, explicit column key,
or relationship join name is never substituted for that canonical name. Field references, partial patch keys, mapping
explanations, and constructor values therefore use names such as `email_address`, not a database name such as
`email_address_db`.

The adapter reads SQLAlchemy's mapped annotations and resolves the supported `Mapped[T]` scalar and relationship
shapes to the normalized annotations used by the existing adapter contract. It ignores class annotations that are not
mapped attributes. Supported relationship values participate in scalar and container nested twixts when both sides
match the existing grammar. Before reading a relationship, the adapter checks that it is loaded and raises a
Betwixt-owned unloaded-field error rather than triggering a loader. Full translation fails on an unloaded relationship;
partial translation omits that field. This applies equally to lazy, detached, and raise-on-lazy configurations.
Unsupported annotations, unreadable attributes, unmapped attributes, hybrid properties, association proxies, and other
SQLAlchemy descriptors are outside the native adapter boundary. A custom adapter is the supported escape hatch;
`reduce_*` and `project_*` callables may access such attributes only when the application accepts responsibility for
doing
so explicitly.

Full translation constructs the destination ORM object through normal mapped-model construction with canonical
keyword values. SQLAlchemy owns constructor behavior, Python-side defaults, instrumentation, and any model-level
validation; Betwixt does not coerce values, flush, commit, refresh, attach, or otherwise persist the object. A mapped
field is constructible without a Betwixt value when it is annotated optional, nullable, has a Python-side constructor
default or default factory, or is a relationship with a Python-side default. Server-side defaults do not satisfy the
pre-construction requirement because no flush occurs. Missing required values produce the existing Betwixt
unmapped-field
or missing-default errors before construction. Native ORM constructor and validation errors propagate unchanged, as do
loaded-attribute access errors.

Without the extra, importing core Betwixt succeeds, but declaring a SQLAlchemy side raises an actionable missing-
optional-dependency error. A user registration for an exact mapped class takes precedence over the built-in adapter;
otherwise lookup follows the existing exact-type, nearest-MRO, then built-in-family order. A custom adapter or explicit
custom adapter may support SQLAlchemy features outside this native boundary. No SQLAlchemy engine, session, query,
lazy-loading, flush, commit, refresh, identity-map, or persistence integration is part of the adapter or Betwixt's
public
contract.


#### AC23: Failures have stable ownership

Betwixt-owned declaration errors cover missing fields, invalid directions, incompatible nested shapes, unsupported
annotations, duplicate registrations, and missing adapters. Betwixt-owned operation errors cover malformed partial
input, missing required defaults, and required destination fields omitted from implicit mapping. `UnmappedFieldError`
includes the corresponding direction, field names, omission reason, and a pointer to the relevant explanation method.
Exceptions from user callables, context derivation, field access, set insertion, and native destination construction or
validation propagate unchanged, with the translation boundary preserved in the traceback.


#### AC24: Betwixt remains a translation layer

Betwixt does not parse wire data, validate source data, serialize, generate schemas, persist data, or integrate with a
web framework. Each side retains its own validation, serialization, persistence, and wire-format responsibilities.


### Release phases and exit criteria

#### AC25: Phase 1 establishes the executable skeleton

Phase 1 delivers the public declaration model, field references, dataclass adapters, implicit mapping, explanation
reports, `map_*`, full translation, context, deterministic overlap, and actionable declaration and unmapped-field
errors. Exit requires both directions of a dataclass example, tests that cover compatible, incompatible, disabled, and
unmapped same-name fields plus the diagnostic report and error remedies, passing lint and type checks, and a working
local Make-based test command.


#### AC26: Phase 2 adds complete structural behavior

Phase 2 delivers reductions, full projections, defaults, nested scalar and container traversal, partial operations, and
the complete annotation grammar. Exit requires the sparse and complete-input matrices in this plan, including projection
skip, reduction availability, required-default call sites, optional values, fixed and variadic tuples, dictionary keys,
set hashability, and nested partial patches.


#### AC27: Phase 3 adds native optional adapters

Phase 3 delivers the `pydantic` extra and the `sqlalchemy` extra, native Pydantic validation and alias behavior, the
native SQLAlchemy mapped-class boundary, adapter registration and override rules, and base-versus-extra compatibility
tests. Exit requires the Pydantic and SQLAlchemy version matrices, an isolated no-extras boundary test, adapter snapshot
and exact/MRO precedence tests, representative translations in both directions, nested SQLAlchemy relationship
coverage, and a SQLAlchemy-to-Pydantic User example matching the blog scenario. Pydantic and SQLAlchemy are installed as
regular development dependencies for normal test environments, but remain package-optional and are included only
through their respective extras for consumers.


#### AC28: The documentation site teaches the design

The Zensical site is configured by `zensical.toml` and is browsable locally and from the published site. Zensical is the
sole documentation build, serve, CI, and publish toolchain; the former MkDocs configuration and dependencies are removed
or explicitly deprecated and are not authoritative. It contains the
sections listed in the Documentation
Architecture below, includes runnable examples for full and partial translation, and explains the User, Payment, and
Order case studies as a coherent narrative distilled from the blog post. Generated API reference is present but is not
the site's sole content. The site teaches installation of the optional `sqlalchemy` extra, the native mapped-class
boundary, canonical mapped attribute names versus database column names, supported scalar and relationship mappings,
unsupported SQLAlchemy descriptors and session concerns, and the SQLAlchemy-to-Pydantic User example from the blog
scenario. It provides a runnable dependency-variant command for the SQLAlchemy example and explains that Betwixt
constructs ORM instances but never manages persistence.


#### AC29: Examples and demos are executable

The repository contains runnable examples for the User, Payment, and Order cases, with deterministic sample inputs and
outputs. The interactive `betwixt-demo` follows the established typerdrive-style demo pattern: a Typer entry point
selects one named feature or all features by default, feature modules expose discoverable `demo_*` functions, and shared
helpers present each demo's explanation, source, captured output, and continuation prompt through Rich. Demo functions
remain independently callable for documentation and smoke tests; the interactive shell is a presentation layer rather
than the implementation of the examples.

The base package variant runs all dataclass examples and the core CLI path. The `pydantic` package variant runs the
Pydantic example and any Pydantic CLI path. The `sqlalchemy` package variant runs the SQLAlchemy-only smoke example. The
combined package variant runs the complete SQLAlchemy-to-Pydantic User example path. All normal variant environments use
the regular development dependency set, so their complete adapter test suites can be collected without optional-import
markers. The core CLI path runs and passes in all four variants. An isolated no-extras job verifies the package boundary
without either optional adapter installed. An optional combined CLI path exercises the blog's SQLAlchemy-to-Pydantic
boundary. The main CLI demo exercises all three cases, including runtime context, nested values, and a patch
translation.
Each clean supported-Python environment runs its required examples without network services, database sessions, or
secrets.


#### AC30: CI verifies quality and release gates

Continuous integration tests every supported Python version across exactly four package variants: base, `pydantic`,
`sqlalchemy`, and combined `pydantic+sqlalchemy`, for twelve normal test jobs. Each normal job uses the regular
development dependency set and runs the complete adapter suite. A separate no-extras job installs the package without
optional extras and verifies both missing-adapter errors. Every test job uploads JUnit and coverage reports; the docs
job
uploads the built site, and the package-build job uploads source and wheel distributions. All artifacts are retained for
14 days, including failed-job reports. The matrix requires 100% coverage on measured code with no reduction. Any code
that is structural, trivial, or intentionally untestable must be excluded only with a local `# pragma: no cover` and a
nearby justification comment. Pull requests and branch pushes gate on all normal test jobs, the no-extras boundary,
lint,
typo, type, docs, SQLAlchemy integration, and core CLI checks; release gates also require both optional-adapter example
paths and successful distribution and site builds.


## Architecture

### Declarative twixt layer

The central abstraction is a peer relationship between `left` and `right`. The class body is an ordered, readable
specification. `field_refs(left, right)` is the public field-reference entry point and returns the two accessor proxies
used as `L` and `R`. Helper aliases are ordinary declaration conveniences and are not translated fields.

The construct taxonomy separates field maps, whole-object reductions, whole-object projections, nested delegation, and
side-only defaults. Direction is encoded in both construct names and callable keyword names (`rightward` or `leftward`).
Pairwise constructs bundle two declarations around field anchors but require both callables.


### Adapter boundary and registry

Adapters provide the conceptual operations needed to describe fields and annotations, read canonical fields, and create
a native destination instance. The registry is process-local, supports exact and MRO-based custom registration, and is
snapshotted by a concrete Betwixt mapping at declaration time. This keeps a declared relationship stable while allowing
applications to
register adapters before declaring their relationships.

Built-in dataclass support is always available. Pydantic support is isolated behind the `pydantic` extra, and mapped
SQLAlchemy support is isolated behind the `sqlalchemy` extra. The SQLAlchemy adapter recognizes mapped declarative
classes, exposes mapped Python attribute names as canonical fields, resolves supported `Mapped[T]` scalar and
relationship annotations, reads loaded attributes, and constructs destination objects through ordinary ORM model
construction. It does not inspect database column labels as Betwixt names, load relationships, or participate in any
session or persistence lifecycle. Hybrid properties, association proxies, unmapped attributes, and other descriptors
remain outside the native boundary unless an explicit mapping or custom adapter handles them.


### Translation engine

Full translation gathers implicit compatible fields, then applies explicit declarations in source order. A projection
contributes the fields extracted from the destination instance it returns. Reductions receive complete source objects.
Defaults fill remaining gaps at the end. The adapter constructs the final destination instance and remains responsible
for native validation and defaults.

Partial translation consumes only canonical mapping keys and emits only derived fields. Maps require all referenced
inputs, nested constructs recurse into mapping values, reductions require all source fields, projections and defaults
are skipped, and presence is determined by key membership. No partial path constructs a destination instance.


### Nested traversal

Nested declarations validate the inner Betwixt mapping's side types against the supported annotation grammar at
declaration time.
At runtime they preserve scalar, optional, list, tuple, dictionary, and set shapes while recursively invoking the
appropriate inner direction. Dictionary keys pass through; translated set values must remain hashable. Context
derivation is a declared relationship at each nesting boundary, so the outer call site can inventory its transitive
dependencies.


### Documentation architecture

The documentation is a browsable Zensical site configured by `zensical.toml`, using the repository's existing Material
theme variant, local Zensical serve/build targets, and a Zensical-compatible Python API reference integration. Its
navigation is organized as follows:

1. **Home and quickstart**: base installation, optional `pydantic`, `sqlalchemy`, and combined installations, first
   dataclass mapping, operation names, and the boundary between validation and translation.
2. **Why Betwixt**: design principles, peer-to-peer two sides, the scenario, and when a mapping layer earns its cost.
3. **Core concepts**: adapters; the complete construct taxonomy and table; directional naming; field references,
   aliases, callable ordering, runtime context, and typed context.
4. **Translation behavior**: implicit fields, declaration order and overlap, nested twixts and containers, full
   translation, partial and patch translation, defaults, implicit-mapping troubleshooting, and failure ownership.
5. **Worked cases**: User as the running taxonomy, including a runnable SQLAlchemy-to-Pydantic example matching the
   blog scenario, Payment for context and asymmetric multi-field transforms, and Order for scalar, optional, list
   nesting, and context propagation.
6. **Optional integrations**: native Pydantic and SQLAlchemy adapter behavior, canonical mapped names versus database
   names, supported relationships, unsupported descriptors, dependency-variant commands, and the absence of session or
   persistence integration.
7. **Design comparison**: Pydantic alone versus Pydantic plus Betwixt, including clean side types, visible asymmetry,
   required pairing, and honest costs.
8. **Limits and outlook**: when not to use Betwixt, risks and future validation such as denormalized joins and
   discriminated unions.
9. **API reference**: generated public symbols, construct signatures, adapter protocol, errors, and supported extras.
10. **Delivery**: CI/CD checks, dependency-variant example commands, retained artifacts, automatic tag releases, and
     automatic documentation deployment after qualifying merges.

Every conceptual page includes at least one short runnable code example. Longer examples share the same User, Payment,
and Order fixtures used by the CLI. Documentation states the exact partial contract, Pydantic behavior, unsupported
annotation shapes, SQLAlchemy's mapped-attribute and relationship boundary, and the `explain_*` and `UnmappedFieldError`
troubleshooting path rather than implying that the API reference is the specification. The site explicitly presents the
requested blog-distilled peer-mapping narrative, its User, Payment, and Order examples and demos, and the CI/CD and
release behavior that verifies and publishes them.


### Examples and CLI demo

The example suite uses dependency-light dataclasses for the core path, an optional Pydantic example for the native
adapter boundary, and an optional SQLAlchemy ORM example. The User example demonstrates the blog's ORM-row to
Pydantic-response mapping, implicit fields, canonical ORM attribute names, a database-column rename, a split or
combined name, a required default, context, and a partial patch. Its runnable command installs or selects the
`sqlalchemy` and `pydantic` variants and uses no engine or session. Documentation provides the concrete command
`uv run --extra pydantic --extra sqlalchemy python examples/sqlalchemy_user.py` to run this combined dependency
variant. The Payment example demonstrates multi-field amount conversion, asymmetric directions, and an FX-rate
context. The Order example demonstrates customer, line-item list,
optional shipping address, nested context slices, and order-level derived values. SQLAlchemy relationship examples use
already available mapped values and nested twixts, never lazy-loading or persistence operations.

The CLI demo presents three selectable scenarios or a run-all mode, prints the source and translated values, performs a
partial update, and exits nonzero for an unexpected result. It uses fixed FX rates, timestamps, and service stubs so the
output is stable in CI. Examples are documentation sources, not separate undocumented toy implementations.


### CI/CD architecture

CI has a quality matrix across Python 3.12, 3.13, and 3.14 and across four package variants: base, `pydantic`,
`sqlalchemy`, and combined `pydantic+sqlalchemy`, for twelve normal test jobs. Each normal job uses the regular
development dependency set and runs the complete adapter suite. A separate no-extras job installs the package without
optional extras and verifies both missing-adapter errors. Every test job uploads JUnit and coverage reports; the docs
job
uploads the built site, and the package-build job uploads source and wheel distributions. All artifacts are retained for
14 days, including failed-job reports. The matrix requires 100% coverage on measured code with no reduction. Structural,
trivial, and intentionally untestable code may use only local `# pragma: no cover` exclusions with nearby justification
comments. Pull
requests and branch pushes gate on all normal test jobs, the no-extras boundary, lint, typo, type, docs, SQLAlchemy
integration, and core CLI checks; release gates also require both optional-adapter example paths and successful
distribution and site builds.

Documentation build validation runs on pull requests and pushes by invoking Zensical through `zensical.toml`, without
publishing. A documentation deployment job listens to closed pull requests whose paths include `docs/source/**` or
`zensical.toml` and runs only when the pull request was merged into `main`. It uses the same Zensical build output,
verifies that a representative generated API page exists, and requires the repository's deployment environment. This
supports merge-commit, squash, and rebase merges while excluding direct main pushes, feature-branch pushes, tag pushes,
and unrelated merges. Package publication builds once, verifies the same quality gates, and publishes automatically only
from a validated pushed version tag. No manual package publication path exists.


## Unknowns

No unresolved design questions remain. Implementation planning may choose internal representations and caching without
changing the observable contracts above.


## Technical Notes

- The supported Python range is 3.12 through 3.14, matching the repository's current CI intent; metadata and CI must
  agree.
- The canonical developer interface remains the existing Make-based QA, documentation, and demo commands.
- Full destination construction is intentionally native to the selected adapter. Betwixt supplies translated canonical
  values but does not add a coercion or validation layer.
- The authoritative blog is the source for the site's narrative and examples, while this plan's explicit contracts
  govern implementation where the blog leaves edge behavior open.
- attrs, msgspec, custom containers, discriminated unions, and root wrappers remain extension or explicit callable
  scenarios rather than hidden features. SQLAlchemy mapped declarative support is a delivered Phase 3 feature under
  the native boundary defined in AC22; SQLAlchemy session and persistence integration remains explicitly out of scope.
