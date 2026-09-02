# Betwixt

![Betwixt logo](static/logo.png)

_Betwixt your data models lives a new, declarative mapping layer._



## Overview

Betwixt maps peer boundary models without coupling them to one another. Thus, the data models for each layer can remain
purely focused on their domain while Betwixt manages data mapping between them. Betwixt owns only the translation; each
model retains validation, serialization, persistence, and other concerns of its domain. You need only declare a derived
`Betwixt` class for every mapping that you need. Then, simply request a "leftward" or "rightward" mapping from a model
instance to obtain a fully mapped instance.


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
