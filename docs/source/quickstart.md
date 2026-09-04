# Quickstart

This short example builds a mapping between two small Python models and shows the result in both directions.


## Requirements

Use Python 3.12 to 3.14.


## Installation

!!! note Using `uv`
    These examples use `uv`, but you can install `betwixt` with pip, Poetry, Hatch, or another Python package manager.

Install the latest version from PyPI:

```shell
uv add betwixt
```

Add an optional integration when your project uses Pydantic or SQLAlchemy:

```shell
uv add "betwixt[pydantic]"
uv add "betwixt[sqlalchemy]"
uv add "betwixt[pydantic,sqlalchemy]"
```


## Your first mapping

This example maps a dataclass to a `TypedDict`. The two models have the same fields, so Betwixt can connect them without
explicit field mappings.


```python
from dataclasses import dataclass
from typing import TypedDict

from betwixt import Betwixt, field_refs


@dataclass
class Person:
    """Represent the source person."""

    name: str
    age: int


class PersonView(TypedDict):
    """Represent the destination person view."""

    name: str
    age: int


class PersonTwixt(Betwixt):
    """Map compatible same-name fields without explicit declarations."""

    left = Person
    right = PersonView
    (L, R) = field_refs(left, right)


person_view = PersonTwixt().rightward(Person(name="Ada", age=36))
person = PersonTwixt().leftward(person_view)
partial_view = PersonTwixt().rightward_partial({"name": "Ada"})
partial_person = PersonTwixt().leftward_partial({"age": 36})

assert person_view == {"name": "Ada", "age": 36}
assert person == Person(name="Ada", age=36)
assert partial_view == {"name": "Ada"}
assert partial_person == {"age": 36}
```

The `rightward` call moves a `Person` to the right-hand model. `leftward` moves it back.
Because the field names and types match, Betwixt maps `name` and `age` automatically.

The two partial calls show how to translate only the fields you have. They accept plain dictionaries with the model's
canonical field names and return sparse dictionaries. They leave missing fields missing instead of applying defaults or
constructing a destination model.


## What's next

- Read the [concepts](concepts.md) guide for the ideas behind these mappings.
- Explore the [case studies](cases/index.md) for more realistic examples.
