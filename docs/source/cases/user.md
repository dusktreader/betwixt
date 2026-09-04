# User case

An API response and a database row can describe the same user without being built the same way.
In this example, `email` is the canonical Python attribute, even though the database column has a different name.
Betwixt maps that attribute to a Pydantic response, applies an explicit display-name transform, and leaves validation to
Pydantic.

The dataclass in this example has no default declaration, so Betwixt reports missing required fields instead of quietly
filling them. No database engine or session is needed.


## Example

The example also performs a partial patch with canonical keys. A serialization alias never changes those keys.

```python
from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_pairwise

@dataclass
class User:
    name: str
    email: str

@dataclass
class UserView:
    name: str
    email: str

left, right = field_refs(User, UserView)

class UserMapping(Betwixt):
    left = User
    right = UserView
    fields = map_pairwise(left=(left.name, left.email), right=right.name,
                          rightward=lambda name, email: f"{name} <{email}>",
                          leftward=lambda value: value.split(" ", 1)[0])

mapping = UserMapping()
patch = mapping.rightward_partial({"email": "ada@example.test"})
assert patch["email"] == "ada@example.test"
```
