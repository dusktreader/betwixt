# Features

Betwixt helps two models exchange data, even when they have different shapes. Matching fields map automatically, while
explicit declarations handle the differences.


## Declare a mapping

A `Betwixt` child connects two models through `left` and `right`. Field references tie each field to its model and name.
Betwixt checks each reference against the adapter when it creates the mapping class.

Inside the class body, `(L, R) = field_refs(left, right)` creates those references.
They use canonical Python field names, meaning the names on the model itself.
An adapter can expose a different JSON or database name, but the mapping stays independent of those details.


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

With the declaration in place, the mapping can translate a model instance.

```python
user = UserTwixt().rightward(User("Ada"))
assert user == UserView("Ada")
```

Betwixt compiles the declaration when the child class is created. It checks references, adapters, nested shapes, and
supported parts of function signatures near the declaration. Problems that depend on runtime arguments can still appear
when a translation runs.


## Implicit same-name mapping

### Matching fields map automatically

Two models often share ordinary fields. Implicit mapping means you do not have to repeat declarations for those fields,
while explicit declarations remain available for exceptions.


### How it works

In either direction, matching field names map implicitly when their annotations are compatible. Betwixt reads the source
through its adapter and copies the value to the destination. An explicit mapping wins when it runs; during a partial
translation, an incomplete explicit mapping can leave the implicit value in place. Betwixt does not implicitly coerce
incompatible annotations. A key whose value is `None` is still present, so it is not treated like an absent key.


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

Here, the compatible same-name fields are copied through the adapters without declarations for either field.

```python
view = PersonTwixt().rightward(Person("Ada", 36))
assert view == PersonView("Ada", 36)
```

There are no explicit mappings for `name` or `age`. Their names and annotations match, so Betwixt maps them implicitly.


## Explicit directional field mapping

### One-way field transformations

An explicit transformation helps when names or shapes differ, or when a business rule works in only one direction.
Direction also matters. Betwixt will not invent an inverse for a write-only or computed field.


### How it works

`map_rightward` reads one or more left fields and writes one right field. `map_leftward` does the reverse. Each function
receives its referenced source values in reference order. `map_pairwise` records independent functions for both
directions, so the two functions do not need to be mathematical inverses.

Each map runs only when every referenced source key is present. During a full operation, the adapter reads the model's
attributes or mapping keys for you.


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

This example shows the one-way rule: each one-way mapping function runs only in the direction it declares.

```python
account_view = AccountTwixt().rightward(Account("Ada", "Lovelace", "ada@example.com"))
assert account_view == AccountView("Ada Lovelace", "mailto:ada@example.com")
```

One-way mapping functions support only their named direction. Pairwise functions support both directions.
Betwixt does not infer a reverse declaration for a one-way function.


## Expansion

### One field split into several fields

Sometimes one source field needs to fill several destination fields. For example, a full name can become first and last
names. Expansion handles that split without requiring a destination constructor or guessing a reverse mapping.


### How it works

`expand_rightward` takes one left source and at least two right destinations.
`expand_leftward` takes one right source and at least two left destinations.
Each function receives one source value and returns one tuple item per destination.
Betwixt assigns the items by position, not by field name.


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

The tuple order determines which returned value fills each destination field during a full translation.

```python
view = ProfileTwixt().rightward(Profile("Ada Lovelace"))
assert view == ProfileView("Ada", "Lovelace")
```

Returning a list, the wrong tuple length, or any other shape raises `ExpansionError`.


## Reductions

### A value from the whole model

Some values depend on the complete source model instead of just a few fields.
Reductions work well for totals, signatures, summaries, and other calculations that need the whole object.


### How it works

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

The reduction receives the complete source object and writes its one result field.

```python
assert BasketTwixt().rightward(Basket((3, 4))) == BasketView(7)
```


## Projections

### The whole destination at once

When one object-level function already defines the conversion, field-by-field mappings add noise. A projection lets one
function build the entire destination shape.


### How it works

`project_rightward` receives the complete left object and `project_leftward` receives the complete right object. The
function must return an instance or mapping accepted by the destination adapter. The adapter validates the projection,
rejects unknown fields, and extracts the destination's canonical field values.


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

One function builds the complete destination object for the adapter.

```python
assert EventTwixt().rightward(Event(7, "ready")).text == "7: ready"
```


## Nested mappings and containers

### Reuse mappings inside nested values

Nested models need the same clear boundary as top-level models. A nested declaration reuses a child `Twixt` instead of
duplicating its rules. Betwixt can also walk supported containers and apply the child mapping to each nested element.


### How it works

`nested_rightward`, `nested_leftward`, and `nested_pairwise` reuse another `Betwixt` through `via`. The outer and inner
annotations must describe compatible shapes. Supported shapes include scalars, optional values, lists, variadic tuples,
fixed tuples, dictionaries, and sets. Dictionary keys pass through unchanged. Empty containers make no inner calls.

If supplied, the nested context selector receives the outer context once, positionally. Betwixt reuses its result for
every element in that nested value. The nested function then receives the translated inner value and may transform it.
Malformed values include their container path, such as `lines[0]`.
A present `None` is different from an absent key. It is accepted only when the annotation is optional.


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

This example walks the list and reuses the derived context for each item.

```python
invoice_view = InvoiceTwixt().rightward(Invoice([Line(250)]), context={"minor_units": 100})
assert invoice_view == InvoiceView([LineView(2.5)])
```

The inner function's `ctx` receives the derived value. Each `Line` uses that same context. Malformed values include a
container path such as `lines[0]`. A present `None` is distinct from an absent key. Optional annotations accept it.


## Implicit-mapping controls

Same-name mapping is convenient until a boundary requires every field to be deliberate. You can disable implicit mapping
globally, or suppress one same-name pair while leaving other compatible fields automatic.

You can set `disable_implicit_mapping = True` on the class to suppress all compatible same-name mappings.
For narrower control, use `disable_implicit_rightward`, `disable_implicit_leftward`, or `disable_implicit_pairwise`.
Each control must point to the same canonical field on both sides.


This example suppresses the automatic `label` mapping, so the source value does not cross the boundary. The destination
model supplies its own fallback.

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

The source `label` is omitted, while compatible `value` still maps implicitly:

```python
assert SourceTwixt().rightward(Source(3, "ignored")) == Destination(3)
```


## Declaration order and overlap

### Predictable overlapping declarations

Several declarations can write the same destination. A business rule may refine a basic value. The class body makes the
precedence visible and predictable.


### How it works

Betwixt starts with compatible same-name fields. It then runs explicit declarations in class-body order. The last write
wins for overlapping maps, expansions, nested mappings, reductions, and projections. A mapping with incomplete source
fields cannot run. It does not write a value.


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

### Only the fields you received

Patch handlers often receive only some fields from a client. Partial translation keeps missing values missing. It avoids
inventing them or constructing a destination model too early.


### How it works

`rightward_partial` accepts canonical left keys and returns a sparse plain dictionary of canonical right keys.
`leftward_partial` does the reverse. Unknown source keys and non-mapping inputs raise `PartialInputError`. A map or
expansion runs when its required source keys are present. A reduction waits for every source field. Projections are
skipped, and nested partial mappings preserve supported container shapes. Partial operations do not construct the
destination model or apply its defaults. A reduction may construct a temporary source model, but only when every source
field is present.


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

With only `cents`, the price map can run, but the reduction cannot because `quantity` is absent:

```python
mapping = ProductTwixt()
assert mapping.rightward_partial({"cents": 2500}) == {"dollars": 25.0}
```

Once the reduction's complete source fields are present, it contributes its result. The pairwise mapping contributes
independently whenever its own source key is present:

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

### Why a field did not map

The destination model still decides which fields are required. When a field is missing, you need to know why.
Declaration-only explanations show Betwixt's view without reading a value or constructing either model.


### How it works

`explain_rightward()` and `explain_leftward()` return a `MappingExplanation`. Its `entries` classify each destination as
`implicit`, `explicit`, `omitted`, or `unmapped`. They include the source field and annotations when known.

Full translation raises `UnmappedFieldError` when a required destination field has no produced value. The exception
includes the direction, source and destination types, canonical fields, annotations, omission reason, the explanation
method, and remedies. Errors from model construction, validation, functions, derived values, and set insertion retain
their original types.


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

This example catches the failed translation and then inspects the unmapped destination field.

```python
mapping = IncompleteTwixt()
try:
    mapping.rightward(Source(1))
except UnmappedFieldError as error:
    assert error.destination_field == "required"
    print(mapping.explain_rightward().entries)
```

The explanation identifies the implicit value and the required field that has no mapping:

```text
[MappingEntry(destination='value', status='implicit', source='value', reason=None, annotation=<class 'int'>, source_annotation=<class 'int'>), MappingEntry(destination='required', status='unmapped', source=None, reason=None, annotation=<class 'str'>, source_annotation=None)]
```

For a required field, an `unmapped` entry needs an explicit mapping. An optional or defaulted field can remain unmapped.
An `omitted` required field may need its suppressing control removed.
An explicit mapping may be needed if the field needs a different transformation.
Incompatible annotations also need an explicit mapping, not an implicit-mapping control.


## Runtime context for functions

### Runtime values outside models

A translation may depend on request metadata, currency, tenant, or another runtime value. Context keeps that application
data out of the models and makes the injection point explicit.


### How it works

Operations have the signatures `rightward(value, *, context=None)` and `leftward(value, *, context=None)`. Map functions
receive referenced source values in reference order. Reductions and projections receive the complete source object. A
function around a nested mapping receives the translated inner value.

These mapping functions can receive context through a final keyword-only parameter named `ctx`. That includes maps,
expansions, reductions, projections, and nested mappings. Betwixt calls it as `ctx=...`. A positional `ctx`, or a `ctx`
parameter that is not final, is invalid.

Nested context selectors work differently: they receive the outer context as one positional argument at each nested
boundary. Their return value goes to each inner translation. Betwixt passes context unchanged; it does not validate or
coerce it.


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

At application time, Betwixt injects context into the function's keyword-only `ctx` parameter.

```python
assert AmountTwixt().rightward(Amount(2500), context={"minor_units": 100}) == AmountView(25.0)
```


## Adapter boundaries

### Model concerns at the model boundary

Models should keep their own validation, construction, and persistence behavior. Adapters let Betwixt inspect fields and
read values. They validate projections and construct destinations without adding mapping methods to the models.


### How it works

Dataclasses and `TypedDict` work directly. Pydantic and SQLAlchemy support is optional and selected by the appropriate
extra. Field references and partial keys always use canonical Python attribute names. Serialization aliases and database
column names do not apply. Pydantic performs its own coercion, defaults, and validation. SQLAlchemy relationships must
already be loaded. Betwixt never creates sessions, loads relationships, persists, flushes, commits, or refreshes.

You can register an `Adapter` for another kind of boundary value. The [adapter guide](adapters.md) covers the Pydantic,
SQLAlchemy, and `TypedDict` setup details.


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

Betwixt constructs the `TypedDict` result without changing the source model. That is the adapter boundary in action.

```python
assert RecordTwixt().rightward(Record("Ada")) == {"name": "Ada"}
```


## What's next

- The [case studies](cases/index.md) show these features applied to realistic boundaries.
- The [adapter guide](adapters.md) covers `TypedDict`, Pydantic, SQLAlchemy, and custom adapters.
- The [reference examples](examples.md) include complete standalone source files.
- The [API reference](api-reference.md) documents the complete public surface.
