# Quickstart

## Requirements

- Python 3.12 to 3.14

This example crosses a dataclass boundary on the left with a `TypedDict` boundary on the right.


## Installation

!!! note We use `uv`
    The documentation here assumes you will be using `uv`. However, you can install `betwixt` via pip, poetry, hatch,
    etc. in the same way.

Install the latest version from PyPI:

```shell
uv add betwixt
```

You may also install optional integrations if you need them:

```shell
uv add betwixt[pydantic]
uv add betwixt[sqlalchemy]
uv add betwixt[pydantic,sqlalchemy]
```


## Using

First, declare a derived `Betwixt` class that describes the mapping between your two models:


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
```

Full operations return a `PersonView` plain dict on the right and a `Person` instance in reverse. Partial operations
accept only canonical source mappings and return sparse plain dictionaries; they never apply defaults or construct a
destination.


## What next?

- Go deeper in the  [Concepts](concepts.md) to better understand what `Betwixt` is all about.
- Check out the [Case Studies](cases/index.md) to learn how the `Betwixt` patterns can be applied in real use-cases.
