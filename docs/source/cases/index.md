# Case studies

These case studies show where an explicit boundary mapping earns its keep.


## Why case studies

The core examples introduce individual constructs in isolation. These cases put those constructs into recognizable
application boundaries, where models have different owners, representations, validation rules, and directions of flow.
They show the decisions a mapping makes without pretending that every boundary can be inferred automatically.


## Cases

- [User](user.md): Keep an ORM row and an API response independent while preserving canonical field names and native
  validation.
- [Payment](payment.md): Convert cents and dollars in opposite directions while deriving currency from operation
  context.
- [Order](order.md): Compose nested scalar, optional, and list mappings while preserving sparse partial updates.

Read the cases after the [core examples](../examples.md) and before the [adapter guide](../adapters.md).
