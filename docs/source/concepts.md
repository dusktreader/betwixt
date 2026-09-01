# Concepts

A declared Betwixt subclass describes how two data types relate without requiring either type to know
about the other or how fields should be mapped between the two. This allows the data types to remain focused on their
domain and purpose.

Adapters provide the common language for inspecting fields and constructing native values, while directional constructs
describe the transformations that cannot be inferred. The sections below introduce those pieces and the rules that make
a mapping predictable.


## Why Betwixt

Betwixt keeps peer models independent while making asymmetric translation explicit. An API request model, a domain
model, an ORM row, and a response model may describe the same concept with different ownership and validation rules.

For example, a Pydantic API schema often needs translation logic before it can become a SQLAlchemy model. Encoding that
logic through Pydantic aliases, validators, serializers, or SQLAlchemy properties and events fits poorly when the logic
belongs to the boundary between the two types. It dilutes the purpose of each model and fragments the translation story
across several framework-specific locations.

A declared `Betwixt` subclass makes that boundary visible in one place without adding framework-specific methods to
either type. Direction is explicit, so a write-only secret or a computed response field cannot accidentally acquire an
inverse.


## Field references

A field reference is a typed handle to one field on one side of a mapping. It tells a construct both which model owns
the field and which canonical Python name to use. That information matters because the same field may have a different
name outside the model: a Pydantic field can serialize as `emailAddress`, a SQLAlchemy attribute can use the
`email_address` column, and a `TypedDict` adapter still works with the dictionary's declared Python key.

The declaration should therefore use `R.email`, not an external alias such as `emailAddress` or `email_address`. Field
refs also let Betwixt reject misspelled or foreign fields when the child class is declared. They are defined inside the
child class that uses them, immediately after `left` and `right`:

```python
class AccountTwixt(Betwixt):
    left = AccountRequest
    right = AccountRow
    (L, R) = field_refs(left, right)
    email = map_pairwise(left=L.email, right=R.email, rightward=str.lower, leftward=str.lower)
```

The adapters handle serialization and persistence names at their own boundaries. Declarations and partial mappings
remain stable because they use canonical Python field names.


## Construct taxonomy

The public taxonomy contains exactly seventeen factories. Pairwise constructs require both directional callables;
directional constructs execute only in the named direction. The class-body order determines producer order, and a later
write replaces an earlier write for the same destination.

Maps receive referenced source values in declaration order. Expansions receive one source value and return a tuple whose
items fill multiple destination references in declaration order. Reductions receive a complete source object,
projections return a complete destination object, and nested declarations delegate scalar or supported container values
to another `Betwixt`.

| Family      | Constructs                                                                             | Directional behavior                                       |
| ----------- | -------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Maps        | `map_pairwise`, `map_rightward`, `map_leftward`                                        | Transform referenced field values in reference order       |
| Expansions  | `expand_rightward`, `expand_leftward`                                                  | Fan one value out to ordered destination fields            |
| Reductions  | `reduce_rightward`, `reduce_leftward`                                                  | Transform a complete source object                         |
| Projections | `project_rightward`, `project_leftward`                                                | Return a complete destination-shaped object                |
| Nested      | `nested_pairwise`, `nested_rightward`, `nested_leftward`                               | Delegate scalar or supported containers to another mapping |
| Controls    | `disable_implicit_pairwise`, `disable_implicit_rightward`, `disable_implicit_leftward` | Suppress compatible same-name implicit producers           |

There are no `reduce_pairwise` or `project_pairwise` aliases. Class-body order is the callable ordering rule, so later
writes replace earlier writes.

An expansion has one source reference and at least two destination references. Its callable must return a tuple with
exactly the destination arity. The matching directional partial operation requires only that one source key and returns
all expanded destination keys; the opposite direction is not inferred.


## Callable and context rules

The compiler validates callable signatures when the declaration is built. Direct map, reduction, projection, and nested
callables receive referenced values in declaration order. A final keyword-only parameter named `ctx` receives the
operation context as `ctx=...`; positional `ctx` parameters are invalid. Nested context selectors instead receive the
outer context as exactly one positional argument, once per nested boundary, and their result is reused for every
element.

The operation signatures are `rightward(value, *, context=None)` and `leftward(value, *, context=None)`. Context is
often where application-specific details belong, such as a currency policy, tenant, or feature flag. Giving that context
a type makes those dependencies visible to anyone reading the callable and gives type checkers and editors enough
information to catch a misspelled field or an incompatible value before the mapping runs. Such a type is not required,
but it is recommended for any non-trivial context.

```python
from dataclasses import dataclass

@dataclass
class CurrencyContext:
    minor_units: int
    currency: str


def cents_to_dollars(cents: int, *, ctx: CurrencyContext) -> float:
    return cents / ctx.minor_units
```

The callable's `ctx` annotation now documents exactly what it expects. Betwixt passes the context object unchanged and
does not validate or coerce its contents.


## What's next

- Read the [feature guide](features.md) for detailed explanations and focused examples.
- Browse the [reference examples](examples.md) for complete standalone source files.
- Explore the [case studies](cases/index.md) to see the concepts applied to realistic boundaries.
- Check the [adapter guide](adapters.md) for TypedDict, Pydantic, SQLAlchemy, and custom adapters.
