# Case studies

These examples show how Betwixt helps when the same data appears in different parts of an application.


## Why these examples

The core examples introduce one feature at a time. These cases put those features into familiar situations, such as an
API talking to a database or an order containing several items. Each model has its own job, so the fields, names, and
directions can differ.

The examples show which conversions you need to describe and which straightforward fields Betwixt can handle for you.
They also show where an explicit choice is better than guessing.


## Cases

- [User](user.md): Keep a database record and an API response independent while each model validates its own data.
- [Payment](payment.md): Convert between cents and dollars while using the currency information available at runtime.
- [Order](order.md): Map nested values, optional fields, and lists while keeping partial updates sparse.
- [Checkout](checkout.md): Translate a validated API checkout into an in-memory SQLAlchemy row and back.

Read these cases after the [core examples](../examples.md) and before the [adapter guide](../adapters.md).
