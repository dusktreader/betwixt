# Adapters

Betwixt already knows how to work with dataclasses, `TypedDict`, Pydantic models, and SQLAlchemy models. If your data
lives in a different kind of object, a custom adapter teaches Betwixt how to inspect it and build it. The adapter keeps
that type-specific code separate from your mapping declarations.


## Why write a custom adapter

Use a custom adapter when your type stores or creates data in its own way. Common examples include value objects and
immutable structures, legacy records, and types from another library. Instead of teaching every mapping about those
details, you teach the adapter once.


## What an adapter does

An adapter describes a type and answers five questions:

- `fields()` says which fields the type has and what their types are.
- `read()` gets one field from an existing value.
- `project()` extracts the fields from a complete value.
- `construct()` builds a new value from mapped fields.
- `required()` says whether a destination field must be present before construction.

Use the model's canonical Python field names here. The adapter can handle names used outside the object. Betwixt leaves
validation and type conversion to the type itself.


## Example

This custom type stores its data in private attributes. Its adapter gives Betwixt a clean, stable view of those fields:

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

Register the adapter before declaring the `Betwixt` child.
Betwixt remembers the adapter when it creates the mapping class:

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

The custom adapter can now use the same mapping features as a built-in adapter, including complete, partial, nested, and
projected mappings.

The [feature guide](features.md) explains the adapter boundary in more detail.
The [reference examples](examples.md) show combined mappings for models with different representations.


## Built-in adapters

Pydantic and SQLAlchemy support is available as optional package extras. Install both with:

```shell
uv add "betwixt[pydantic,sqlalchemy]"
```


## What's next

- Read the [feature guide](features.md) for mapping capabilities.
- Explore the [case studies](cases/index.md) for application-shaped examples.
- Browse the [API reference](api-reference.md) for the `Adapter` protocol.
