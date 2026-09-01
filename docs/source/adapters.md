# Adapters

Betwixt includes adapters for dataclasses, `TypedDict`, Pydantic, and SQLAlchemy. A custom adapter extends the same
boundary contract to an application-owned type that does not fit one of those integrations.


## Why a custom adapter

Adapters keep model-specific inspection and construction out of the mapping declaration. This is useful for value
objects, legacy records, immutable structures, or types from another library whose fields are not exposed as ordinary
dataclass, Pydantic, TypedDict, or SQLAlchemy fields.


## Adapter contract

An adapter identifies the type and provides five operations. `fields()` returns canonical names and annotations.
`read()` gets one field from an existing value. `project()` extracts canonical fields from a complete projected value.
`construct()` creates a native destination value, and `required()` reports whether a destination field must be produced
before construction.

The adapter owns the type's native boundary behavior. Betwixt does not validate or coerce values on its behalf.


## Example

The following custom type stores its data in private attributes. Its adapter exposes a stable canonical field surface:

```python
from collections.abc import Mapping

from betwixt import Adapter, Betwixt, field_refs, map_pairwise, register_adapter


class LegacyUser:
    name: str
    email: str

    def __init__(self, name: str, email: str) -> None:
        self._name = name
        self._email = email


class LegacyUserAdapter:
    type = LegacyUser

    def fields(self) -> Mapping[str, object]:
        return {"name": str, "email": str}

    def read(self, value: LegacyUser, name: str) -> object:
        return getattr(value, f"_{name}")

    def project(self, value: LegacyUser) -> Mapping[str, object]:
        return {name: self.read(value, name) for name in self.fields()}

    def construct(self, values: Mapping[str, object]) -> LegacyUser:
        return LegacyUser(str(values["name"]), str(values["email"]))

    def required(self, name: str) -> bool:
        return True


adapter: Adapter = LegacyUserAdapter()
register_adapter(LegacyUser, adapter)
```

The registration must happen before the `Betwixt` child is declared, because adapters are resolved and snapshotted
during class declaration:

```python
from dataclasses import dataclass


@dataclass
class UserPayload:
    name: str
    email: str


class UserTwixt(Betwixt):
    left = UserPayload
    right = LegacyUser
    (L, R) = field_refs(left, right)
    name = map_pairwise(
        left=L.name,
        right=R.name,
        rightward=str.title,
        leftward=lambda name: name,
    )
    email = map_pairwise(
        left=L.email,
        right=R.email,
        rightward=str.lower,
        leftward=lambda email: email,
    )


twixt = UserTwixt()
legacy = twixt.rightward(UserPayload("ada", "ADA@EXAMPLE.COM"))
payload = twixt.leftward(legacy)
assert payload == UserPayload("Ada", "ada@example.com")
```

The custom adapter can now participate in the same full, partial, nested, and projected operations as a built-in
adapter.

The [feature guide](features.md) explains the adapter boundary in more detail, and the [reference examples](examples.md)
include a combined mapping for their different representations.


## Built-in adapters

Pydantic and SQLAlchemy adapters are available in `betwixt` as optional extras in the package. They can be installed
like:

```shell
uv add betwixt[pydantic,sqlalchemy]
```


## What's next

- Read the [feature guide](features.md) for mapping capabilities.
- Explore the [case studies](cases/index.md) for application-shaped examples.
- Browse the [API reference](api-reference.md) for the `Adapter` protocol.
