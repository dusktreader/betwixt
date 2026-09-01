# Features

Betwixt translates between two independent, adapter-backed types. This guide covers the declaration features that let a
mapping stay explicit where the two models differ and automatic where they agree.


## Declare a mapping

A `Betwixt` child declares its two sides with `left` and `right`. Field refs identify both the side and the canonical
field rather than passing an unvalidated string. They also let Betwixt validate the field against the declared adapter
when the child class is created.

Within that class body, `(L, R) = field_refs(left, right)` establishes the field references. References use canonical
Python field names, even when an adapter exposes a wire or database alias. This keeps declarations stable and prevents a
database or serialization name from leaking into mapping logic.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs


@dataclass
class User:
    name: str


@dataclass
class UserView:
    name: str


class UserTwixt(Betwixt):
    left = User
    right = UserView
    (L, R) = field_refs(left, right)
```

The declared mapping translates a model instance.

```python
user = UserTwixt().rightward(User("Ada"))
assert user == UserView("Ada")
```

The class declaration is compiled when the child class is created. Invalid references, missing adapters, incompatible
nested shapes, and invalid callable signatures fail at declaration time rather than on an unrelated translation.


## Implicit same-name mapping

### Why it exists

Peer types often share ordinary fields. Implicit mapping removes boilerplate for those fields while leaving declarations
available for the exceptional ones.


### Semantics

In each direction, a same-name source and destination field map implicitly when their annotations are compatible. The
source value is copied through the source adapter. An explicit producer for that destination takes precedence over the
implicit producer. Incompatible annotations are not coerced implicitly, and a present `None` is still a present value.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs


@dataclass
class Person:
    name: str
    age: int


@dataclass
class PersonView:
    name: str
    age: int


class PersonTwixt(Betwixt):
    left = Person
    right = PersonView
    (L, R) = field_refs(left, right)
```

The application shows compatible same-name fields being copied implicitly through the adapters.

```python
view = PersonTwixt().rightward(Person("Ada", 36))
assert view == PersonView("Ada", 36)
```

The mappings between `name` and `age` are not explicitly declared. Because the field names and annotations match between
the two data types, the mapping happens implicitly.


## Explicit directional field mapping

### Why it exists

Different names, different shapes, and one-way business rules need an explicit transformation. Directional declarations
also prevent Betwixt from inventing an inverse for a write-only or computed field.


### Semantics

`map_rightward` reads one or more left fields and writes one right field. `map_leftward` does the reverse. The callable
receives values in the order of its source references. `map_pairwise` declares both independent callables in one record;
it does not require the transformations to be mathematical inverses.

Each map runs only when every referenced source key is present. In a full operation, the adapter reads attributes or
keys.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_leftward, map_pairwise, map_rightward


@dataclass
class Account:
    first: str
    last: str
    email: str


@dataclass
class AccountView:
    display_name: str
    contact: str


class AccountTwixt(Betwixt):
    left = Account
    right = AccountView
    (L, R) = field_refs(left, right)
    name = map_rightward(
        left=(L.first, L.last), right=R.display_name,
        rightward=lambda first, last: f"{first} {last}",
    )
    contact = map_leftward(
        right=R.contact, left=L.email,
        leftward=lambda contact: contact.removeprefix("mailto:"),
    )
    pair = map_pairwise(
        left=L.email, right=R.contact,
        rightward=lambda email: f"mailto:{email}",
        leftward=lambda contact: contact.removeprefix("mailto:"),
    )
```

The application demonstrates directional callable behavior: each producer runs only in the direction it declares.

```python
account_view = AccountTwixt().rightward(Account("Ada", "Lovelace", "ada@example.com"))
assert account_view == AccountView("Ada Lovelace", "mailto:ada@example.com")
```

The example shows the factories' directional contracts. A declaration may use only the factory for the direction it
supports; there are no inferred reverse declarations.


## Expansion

### Why it exists

One source field sometimes contains several destination fields, such as a full name becoming first and last names.
Expansion expresses that fan-out without requiring a destination constructor or an inverse assumption.


### Semantics

`expand_rightward` has exactly one left source and at least two right destinations. `expand_leftward` has exactly one
right source and at least two left destinations. The callable receives the one source value and must return a tuple with
exactly as many values as destination references. Tuple positions, not names, determine assignment order.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, expand_rightward, field_refs


@dataclass
class Profile:
    display_name: str


@dataclass
class ProfileView:
    first_name: str
    last_name: str


class ProfileTwixt(Betwixt):
    left = Profile
    right = ProfileView
    (L, R) = field_refs(left, right)
    split_name = expand_rightward(
        left=L.display_name, right=(R.first_name, R.last_name),
        rightward=lambda name: tuple(name.split(" ", 1)),
    )
```

The result shows expansion tuple order controlling which returned value fills each destination field during a full
translation.

```python
view = ProfileTwixt().rightward(Profile("Ada Lovelace"))
assert view == ProfileView("Ada", "Lovelace")
```

Returning a list, the wrong tuple length, or another shape raises `ExpansionError`.


## Reductions

### Why it exists

Some destination values depend on the whole source object rather than a declared subset of fields. Reductions are suited
to totals, signatures, summaries, and other source-wide calculations.


### Semantics

`reduce_rightward` receives the complete left object and writes one right field. `reduce_leftward` receives the complete
right object and writes one left field.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, reduce_rightward


@dataclass
class Basket:
    prices: tuple[int, ...]


@dataclass
class BasketView:
    total: int


class BasketTwixt(Betwixt):
    left = Basket
    right = BasketView
    (L, R) = field_refs(left, right)
    total = reduce_rightward(
        right=R.total, rightward=lambda basket: sum(basket.prices),
    )
```

The application passes the complete source object to the reduction before writing its single result field.

```python
assert BasketTwixt().rightward(Basket((3, 4))) == BasketView(7)
```


## Projections

### Why it exists

When a conversion is already defined by a complete object-level function, field-by-field producers add noise. A
projection lets the callable own the entire destination shape.


### Semantics

`project_rightward` receives the complete left object and `project_leftward` receives the complete right object. The
callable must return an instance or mapping accepted by the destination adapter. The adapter validates the projection,
rejects unknown fields, and extracts canonical destination values.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, project_rightward


@dataclass
class Event:
    code: int
    label: str


@dataclass
class EventView:
    text: str


class EventTwixt(Betwixt):
    left = Event
    right = EventView
    (L, R) = field_refs(left, right)
    whole = project_rightward(
        rightward=lambda event: EventView(f"{event.code}: {event.label}"),
    )
```

The result demonstrates projection construction: one callable builds the complete destination object for the adapter.

```python
assert EventTwixt().rightward(Event(7, "ready")).text == "7: ready"
```


## Nested mappings and containers

### Why it exists

Nested models need the same boundary discipline as top-level models. Nested declarations reuse a child `Twixt` rather
than duplicating its rules, and container traversal lets that child mapping work at any supported depth.


### Semantics

`nested_rightward`, `nested_leftward`, and `nested_pairwise` delegate a field to another `Betwixt` via `via`. The outer
and inner annotations must have compatible shapes. Supported shapes include scalars, optional values, lists, variadic
tuple, fixed tuple, dictionaries, and sets. Dictionary keys pass through unchanged. Empty containers make no inner
calls.

The nested context selector, when supplied, is called once with the outer context. Its result is reused for every
element of that nested value. A nested declaration's callable then receives the translated inner value and may transform
it. Malformed values report their container path, such as `lines[0]`. A present `None` is distinct from an absent key
and is accepted only when the annotation is optional.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_rightward, nested_rightward


@dataclass
class Line:
    cents: int


@dataclass
class LineView:
    dollars: float


class LineTwixt(Betwixt):
    left = Line
    right = LineView
    (L, R) = field_refs(left, right)
    dollars = map_rightward(
        left=L.cents, right=R.dollars,
        rightward=lambda cents, *, ctx: cents / ctx["minor_units"],
    )


@dataclass
class Invoice:
    lines: list[Line]


@dataclass
class InvoiceView:
    lines: list[LineView]


class InvoiceTwixt(Betwixt):
    left = Invoice
    right = InvoiceView
    (L, R) = field_refs(left, right)
    lines = nested_rightward(
        left=L.lines, right=R.lines, via=LineTwixt,
        rightward=lambda value: value,
        context_rightward=lambda context: context,
    )
```

The application demonstrates nested traversal and context reuse across each item in the container.

```python
invoice_view = InvoiceTwixt().rightward(Invoice([Line(250)]), context={"minor_units": 100})
assert invoice_view == InvoiceView([LineView(2.5)])
```

In this example, the inner callable's `ctx` receives the derived value. The list is traversed and each `Line` is
translated with the same derived context. Malformed values report their container path, such as `lines[0]`. A present
`None` is distinct from an absent key; `None` is accepted only when the annotation is optional.


## Implicit-mapping controls

Same-name compatibility is useful until a boundary needs every producer to be deliberate. Implicit mapping can be
disabled globally, or a single same-name pair can be suppressed while other compatible fields remain automatic.

The class attribute `disable_implicit_mapping = True` suppresses all compatible same-name producers. Narrower controls
are available through `disable_implicit_rightward`, `disable_implicit_leftward`, or `disable_implicit_pairwise`; each
anchor must name the same canonical field on both sides.


The following example suppresses the implicit `label` producer so the source value does not cross this boundary. The
destination model supplies its own fallback.

```python
from dataclasses import dataclass

from betwixt import Betwixt, disable_implicit_rightward, field_refs


@dataclass
class Source:
    value: int
    label: str


@dataclass
class Destination:
    value: int
    label: str | None = None


class SourceTwixt(Betwixt):
    left = Source
    right = Destination
    (L, R) = field_refs(left, right)
    disable_label = disable_implicit_rightward(left=L.label, right=R.label)
```

The source `label` is omitted while the compatible `value` field still maps implicitly:

```python
assert SourceTwixt().rightward(Source(3, "ignored")) == Destination(3)
```


## Declaration order and overlap

### Why it exists

Several declarations may intentionally write the same destination, for example when a basic value is refined by a
business rule. A deterministic order makes that choice visible in the class body.


### Semantics

Implicit compatible fields seed the result first. Explicit declarations then run in class-body order. The last write
wins. This includes overlapping maps, expansions, nested producers, reductions, and project results. A producer that
cannot run because its source is incomplete does not write a value.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_rightward, reduce_rightward


@dataclass
class Source:
    amount: int
    expedited: bool


@dataclass
class Destination:
    charge: int


class SourceTwixt(Betwixt):
    left = Source
    right = Destination
    (L, R) = field_refs(left, right)
    base_charge = map_rightward(left=L.amount, right=R.charge, rightward=lambda amount: amount)
    expedited_charge = reduce_rightward(
        right=R.charge,
        rightward=lambda source: source.amount + 25 if source.expedited else source.amount,
    )
```

The reduction follows the map and refines the charge only when the complete source marks the shipment as expedited:

```python
assert SourceTwixt().rightward(Source(100, expedited=False)) == Destination(100)
assert SourceTwixt().rightward(Source(100, expedited=True)) == Destination(125)
```


## Partial translation

### Why it exists

Patch handlers often need to translate only fields supplied by a client. Partial translation avoids inventing missing
values or constructing a destination model prematurely.


### Semantics

`rightward_partial` accepts a mapping of canonical left keys and returns a sparse plain dictionary of canonical right
keys. `leftward_partial` does the reverse. Unknown source keys and non-mapping inputs raise `PartialInputError`. A map
or expansion runs when its required source keys are present; a reduction requires every source field before it runs.
Projections are skipped, and nested partial mappings preserve supported container shapes. Partial operations never apply
model construction or defaults.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_pairwise, map_rightward, reduce_rightward


@dataclass
class Product:
    cents: int
    label: str
    quantity: int


@dataclass
class ProductView:
    dollars: float
    label: str
    total: float


class ProductTwixt(Betwixt):
    left = Product
    right = ProductView
    (L, R) = field_refs(left, right)
    price = map_rightward(left=L.cents, right=R.dollars, rightward=lambda cents: cents / 100)
    labels = map_pairwise(left=L.label, right=R.label, rightward=str.upper, leftward=str.lower)
    total = reduce_rightward(right=R.total, rightward=lambda product: product.cents * product.quantity / 100)
```

When only the price is supplied, the map can run but the reduction cannot because `quantity` is absent:

```python
mapping = ProductTwixt()
assert mapping.rightward_partial({"cents": 2500}) == {"dollars": 25.0}
```

Supplying the reduction's complete source fields adds its result, while a pairwise mapping contributes independently
when its own source key is present:

```python
assert mapping.rightward_partial({"cents": 2500, "quantity": 2, "label": "widget"}) == {
    "dollars": 25.0,
    "label": "WIDGET",
    "total": 50.0,
}
assert mapping.leftward_partial({"dollars": 25.0, "label": "WIDGET"}) == {
    "cents": 2500,
    "label": "widget",
}
```


## Explanations and unmapped-field diagnostics

### Why they exist

Native construction should remain the source of truth for required fields, but a missing field needs an actionable
reason.
Declaration-only explanations expose the compiler's view without reading a value or constructing either type.


### Semantics

`explain_rightward()` and `explain_leftward()` return a `MappingExplanation` whose `entries` describe each destination
as `implicit`, `explicit`, `omitted`, or `unmapped`. Entries include the source field and annotations when known.
Full translation raises `UnmappedFieldError` when a required destination field has no produced value. The exception
includes direction, source and destination types, canonical fields, annotations, omission reason, the explanation
method,
and remedies. Native constructor, validation, callable, derivation, and set-insertion errors retain their original
types.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, UnmappedFieldError, field_refs


@dataclass
class Source:
    value: int


@dataclass
class Destination:
    value: int
    required: str


class IncompleteTwixt(Betwixt):
    left = Source
    right = Destination
    (L, R) = field_refs(left, right)
```

The application combines the failed translation with diagnostic inspection of the unmapped destination field.

```python
mapping = IncompleteTwixt()
try:
    mapping.rightward(Source(1))
except UnmappedFieldError as error:
    assert error.destination_field == "required"
    print(mapping.explain_rightward().entries)
```

The explanation identifies the implicit value and the required field with no producer:

```text
[MappingEntry(destination='value', status='implicit', source='value', reason=None, annotation=<class 'int'>, source_annotation=<class 'int'>), MappingEntry(destination='required', status='unmapped', source=None, reason=None, annotation=<class 'str'>, source_annotation=None)]
```

An `unmapped` or `omitted` entry is resolved by an explicit producer or the appropriate implicit-mapping control.


## Context and callable rules

### Why they exist

Translation sometimes depends on request metadata, currency, tenant, or another runtime value. Context keeps that
application concern outside the models while making its injection point unambiguous.


### Semantics

Operations have the signatures `rightward(value, *, context=None)` and `leftward(value, *, context=None)`. Map,
reduction, projection, and nested wrapper callables receive declared source values in reference order. A callable
receives context through a final keyword-only parameter named `ctx`; Betwixt calls it as `ctx=...`. Positional `ctx`, or
a `ctx` parameter that is not final, is invalid.

Nested context selectors are different: they receive the outer context as one positional argument, once per nested
boundary, and their return value is passed to each inner translation. Context is passed unchanged and is not validated
or coerced.


### Example

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_rightward


@dataclass
class Amount:
    cents: int


@dataclass
class AmountView:
    value: float


class AmountTwixt(Betwixt):
    left = Amount
    right = AmountView
    (L, R) = field_refs(left, right)
    value = map_rightward(
        left=L.cents, right=R.value,
        rightward=lambda cents, *, ctx: cents / ctx["minor_units"],
    )
```

The result demonstrates context injection into a keyword-only `ctx` parameter at application time.

```python
assert AmountTwixt().rightward(Amount(2500), context={"minor_units": 100}) == AmountView(25.0)
```


## Adapter boundaries

### Why they exist

Models should keep their native validation, construction, and persistence concerns. Adapters let Betwixt inspect fields,
read values, validate projections, and construct destinations without adding mapping methods to those models.


### Semantics

Dataclasses and `TypedDict` are supported directly. Pydantic and SQLAlchemy support is optional and selected by the
appropriate extra. Field references and partial keys always use canonical Python attribute names, not serialization
aliases or database column names. Pydantic performs its own coercion, defaults, and validation. SQLAlchemy relationships
must already be loaded; Betwixt never creates sessions, loads relationships, persists, flushes, commits, or refreshes.

An application can register an `Adapter` for another boundary type. The [adapter guide](adapters.md) describes
the Pydantic, SQLAlchemy, and `TypedDict` setup details.


### Example

```python
from dataclasses import dataclass
from typing import TypedDict

from betwixt import Betwixt, field_refs


@dataclass
class Record:
    name: str


class RecordView(TypedDict):
    name: str


class RecordTwixt(Betwixt):
    left = Record
    right = RecordView
    (L, R) = field_refs(left, right)
```

The application demonstrates the adapter/native boundary: Betwixt constructs the native `TypedDict` result without
changing the source model.

```python
assert RecordTwixt().rightward(Record("Ada")) == {"name": "Ada"}
```


## What's next

- Explore the [case studies](cases/index.md) to see these features applied to realistic boundaries.
- Read the [adapter guide](adapters.md) for `TypedDict`, Pydantic, SQLAlchemy, and custom adapters.
- Browse the [reference examples](examples.md) for complete standalone source files.
- Check the [API reference](api-reference.md) for the complete public surface.
