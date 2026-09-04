# Betwixt

![Betwixt logo](static/logo.png)

_Betwixt your data models lives a new, declarative mapping layer._


## Overview

If you've ever worked with advanced data types such as Pydantic models or SQLAlchemy ORM models, you know that
translating data between them can be a tricky operation. Two models can describe the same thing while using different
field names, nesting, or representations. Betwixt lets you describe those differences once, then move data between the
models in either direction.


## Basic Example


```python
from dataclasses import dataclass
from betwixt import Betwixt, field_refs, map_rightward

@dataclass
class Left:
    value: int

@dataclass
class Right:
    value: int

left_refs, right_refs = field_refs(Left, Right)

class Mapping(Betwixt):
    left = Left
    right = Right
    value = map_rightward(left=left_refs.value, right=right_refs.value, rightward=lambda value: value)

assert Mapping().rightward(Left(3)) == Right(3)
```


## What next

- Start with the [quickstart](quickstart.md), then follow the User, Payment, and Order cases.
- Learn the basic [Concepts](concepts.md) to better understand what `Betwixt` is all about.
- Read the [Comparison](comparison.md) to see how `Betwixt` cleanly replaces fragmented translation machinery.
