# Concepts

Think of a Betwixt mapping as a translator between two versions of the same information. One model might call a field
`emailAddress`, while another calls it `email_address`; the mapping knows those fields correspond and how to convert the
value. Neither model needs to know about the other, and the translation rules stay in one place.

Simple mappings can often connect fields automatically. If a value needs special handling, you add an explicit mapping
function. A mapping can also turn one field into several. For more involved cases, it can combine values, build a new
object, or reuse another mapping for nested data. It can also use extra context, such as a currency or tenant.

Adapters help Betwixt read fields and create values for each model. The sections below explain these building blocks and
the rules that keep mappings predictable.


## Why Betwixt

Most applications represent the same information in several ways. An API request, an application's main model, a
database row, and an API response may all describe a user, but each has its own fields and responsibilities.

When data moves between those models, it is tempting to put conversion rules wherever they fit: Pydantic aliases and
validators, SQLAlchemy properties and events, or helper methods in the application's own models. That scatters one
translation across several places and makes it harder to see what happens.

Betwixt gives those rules their own home. A mapping connects models without making them depend on each other, and it
makes direction explicit. A write-only secret can flow into a database record without creating a reverse path, while a
computed response field can be produced without being written back.


## Field references

A field reference is Betwixt's way of pointing to a particular field on one model. It tells Betwixt which model owns the
field and which canonical Python name to use. That matters because the same field can have a different name outside the
model: a Pydantic field may appear as `emailAddress` in JSON, a SQLAlchemy attribute may map to an `email_address`
column, and a `TypedDict` adapter still uses the dictionary's declared Python key.

Use `R.email` in the mapping, not an external alias such as `emailAddress` or `email_address`. Field references also let
Betwixt catch misspelled fields and fields from the wrong model when you declare the mapping. Define them inside the
mapping class, immediately after `left` and `right`:

```python
class AccountTwixt(Betwixt):
    left = AccountRequest
    right = AccountRow
    (L, R) = field_refs(left, right)
    email = map_pairwise(left=L.email, right=R.email, rightward=str.lower, leftward=str.lower)
```

The adapters handle JSON and database names at their own boundaries. Your mapping stays stable because it uses canonical
Python field names.


## Mapping directions

Every Betwixt mapping has a `left` model and a `right` model. These are labels you choose. Left does not mean input, and
right does not mean output. The "side" that a model occupies is arbitrary.

The direction names describe the movement of data. A `rightward` operation moves data from left to right, while a
`leftward` operation moves it from right to left. A `pairwise` operation describes both trips.

That means a mapping can be one-way when only one direction makes sense. For example, a secret might move from an API
request into a database record, while a computed display name might move from a database record into an API response.
An explicitly one-way operation does not invent reverse behavior.

Compatible same-name fields are different: Betwixt may create an implicit pairwise mapping for them. That mapping works
in both directions. Disable it when you need one-way behavior.


## Mapping building blocks

Betwixt provides six kinds of mapping building blocks. Across these families, the public API contains exactly several
factories, which are the functions you use to describe how data should move. Names ending in `_rightward` move data from
left to right, while names ending in `_leftward` move it in the opposite direction. `pairwise` functions handle both
directions in one declaration.

Functions that receive several fields get them in reference order, the order in which those fields appear in the
mapping's class body. In other words, class-body order is significant.

When several mapping operations write to the same destination field, the one declared later wins. The order of your
declarations therefore matters.

Here is the main job of each family:

| Family      | Functions                                                                              | What they do                                             |
| ----------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Maps        | `map_pairwise`, `map_rightward`, `map_leftward`                                        | Change one or more field values                          |
| Expansions  | `expand_rightward`, `expand_leftward`                                                  | Split one value into several fields                      |
| Reductions  | `reduce_rightward`, `reduce_leftward`                                                  | Use a complete source object to produce destination data |
| Projections | `project_rightward`, `project_leftward`                                                | Build a complete destination object                      |
| Nested      | `nested_pairwise`, `nested_rightward`, `nested_leftward`                               | Reuse another mapping for nested data                    |
| Controls    | `disable_implicit_pairwise`, `disable_implicit_rightward`, `disable_implicit_leftward` | Turn off automatic same-name mappings                    |

Reductions and projections only work in one direction. That is why there are no `reduce_pairwise` or `project_pairwise`
aliases.

An expansion starts with one source field and fills at least two destination fields. Its function returns one tuple item
per destination field, in order. Betwixt does not infer the reverse direction; define it explicitly when you need it.


## Functions and context

Mapping functions are ordinary Python functions. Betwixt checks their signatures when you create the mapping and passes
referenced field values in the order in which you list them in the mapping declaration.

You can pass extra information to a mapping when you run it:

```python
mapping.rightward(value, context=context)
mapping.leftward(value, context=context)
```

To use that context inside a mapping function, add a final keyword-only parameter named `ctx`. Betwixt passes it as
`ctx=...`. A positional `ctx` parameter is not valid. Context is useful for application-specific details such as a
currency policy, tenant, or feature flag.

Nested context selectors receive the outer context as one positional argument. Betwixt calls them once at each nested
boundary and reuses the result for every item there.

Giving your context a type documents what the function expects and helps type checkers and editors catch mistakes before
the mapping runs. The type is optional, but it is useful for any non-trivial context.

```python
from dataclasses import dataclass

@dataclass
class CurrencyContext:
    minor_units: int
    currency: str


def cents_to_dollars(cents: int, *, ctx: CurrencyContext) -> float:
    return cents / ctx.minor_units
```

The function's `ctx` annotation documents exactly what it expects. Betwixt passes the context object unchanged and does
not validate or coerce its contents.


## What's next

- Read the [feature guide](features.md) for detailed explanations and focused examples.
- Browse the [reference examples](examples.md) for complete standalone source files.
- Explore the [case studies](cases/index.md) to see the concepts applied to realistic boundaries.
- Check the [adapter guide](adapters.md) for TypedDict, Pydantic, SQLAlchemy, and custom adapters.
