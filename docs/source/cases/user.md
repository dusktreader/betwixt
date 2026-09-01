# User case

The User case is the running boundary narrative: an ORM row and an API response are peers, not parent and child
classes. The optional fixture uses `email` as its canonical Python attribute while its database column uses a different
name. Betwixt maps that attribute to a Pydantic response, applies an explicit display-name transform, and
leaves validation to Pydantic. The shared dataclass fixture has no default declaration, so missing required fields are
reported rather than silently filled. No engine or session is needed.


## Example

The example also performs a partial patch with canonical keys. A source serialization alias never changes those keys.

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
