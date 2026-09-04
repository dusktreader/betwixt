# Checkout case

A checkout arrives through a Pydantic API model, then needs to live in SQLAlchemy models with columns and relationships
that reflect the database. The API model owns aliases and validation. The SQLAlchemy models own storage-specific column
names and the line relationship. Betwixt owns the translation between those two representations.


## The story

The checkout service receives a wire payload such as `orderId`, `customerEmail`, and `recipientName`. It validates that
payload, splits the recipient name for storage, converts dollar prices to cents, and keeps each line in a related row.
When the row comes back, the mapping joins the name again and converts cents to dollars before the response is
serialized with the API aliases.

There is no database engine or session in this example. The relationship collection is populated in memory, which keeps
the translation mechanics visible. In a real query, eager-load `lines` before translating: the SQLAlchemy adapter never
silently loads an unloaded relationship.


## Complete example

The following is also available as
[`examples/checkout.py`](https://github.com/dusktreader/betwixt/blob/main/examples/checkout.py).
It uses the Pydantic and SQLAlchemy extras and can be copied as one executable script.

```python
"""Reference a complete Pydantic-to-SQLAlchemy checkout mapping."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from betwixt import (
    Betwixt,
    expand_rightward,
    field_refs,
    map_leftward,
    map_pairwise,
    map_rightward,
    nested_pairwise,
    reduce_rightward,
)


@dataclass(frozen=True)
class CurrencyContext:
    """Carry the currency policy needed by dollar and cent conversions."""

    minor_units: int
    currency: str


class CheckoutLine(BaseModel):
    """Validate one line in the checkout API payload."""

    model_config = ConfigDict(populate_by_name=True)
    line_id: int
    product_code: str = Field(validation_alias="sku", serialization_alias="sku")
    quantity: int = Field(ge=1)
    unit_price_dollars: float = Field(validation_alias="unitPrice", serialization_alias="unitPrice", ge=0)


class CheckoutRequest(BaseModel):
    """Validate the API representation and define its wire aliases."""

    model_config = ConfigDict(populate_by_name=True)
    order_id: int = Field(validation_alias="orderId", serialization_alias="orderId")
    customer_email: str = Field(validation_alias="customerEmail", serialization_alias="customerEmail")
    status: str = Field(pattern="^(pending|paid|shipped)$")
    recipient_display_name: str = Field(
        validation_alias="recipientName",
        serialization_alias="recipientName",
        pattern=r"^\s*\S+(?:\s+\S+)+\s*$",
    )
    postal_code: str | None = Field(default=None, validation_alias="postalCode", serialization_alias="postalCode")
    lines: list[CheckoutLine]
    total_dollars: float = Field(validation_alias="total", serialization_alias="total", ge=0)


class Base(DeclarativeBase):
    """Provide the SQLAlchemy declarative registry."""


class CheckoutLineRow(Base):
    """Store one checkout line under database-specific column names."""

    __tablename__ = "checkout_lines"
    line_id: Mapped[int] = mapped_column("line_id", primary_key=True)
    order_id: Mapped[int | None] = mapped_column(ForeignKey("checkouts.checkout_id"), nullable=True)
    product_code: Mapped[str] = mapped_column("sku_code", String(40))
    quantity: Mapped[int] = mapped_column(Integer)
    unit_price_cents: Mapped[int] = mapped_column("unit_price_minor", Integer)


class CheckoutRow(Base):
    """Represent the persisted checkout and its eagerly populated lines."""

    __tablename__ = "checkouts"
    order_id: Mapped[int] = mapped_column("checkout_id", primary_key=True)
    customer_email: Mapped[str] = mapped_column("customer_email_address", String(255))
    status: Mapped[str] = mapped_column(String(20))
    first_name: Mapped[str] = mapped_column("recipient_given_name", String(80))
    last_name: Mapped[str] = mapped_column("recipient_family_name", String(80))
    postal_code: Mapped[str | None] = mapped_column("postal_code", String(20), nullable=True)
    total_cents: Mapped[int] = mapped_column("total_minor", Integer)
    lines: Mapped[list[CheckoutLineRow]] = relationship()


class CheckoutLineMapping(Betwixt):
    """Translate one API line to one stored line, including money conversion."""

    left = CheckoutLine
    right = CheckoutLineRow
    (L, R) = field_refs(left, right)
    product = map_rightward(left=L.product_code, right=R.product_code, rightward=lambda value: value)
    price = map_pairwise(
        left=L.unit_price_dollars,
        right=R.unit_price_cents,
        rightward=lambda dollars, *, ctx: round(dollars * ctx.minor_units),
        leftward=lambda cents, *, ctx: cents / ctx.minor_units,
    )


def calculate_expected_total_cents(order: CheckoutRequest, *, ctx: CurrencyContext) -> int:
    """Recalculate the order total and verify the declared API total."""
    calculated_cents = sum(line.quantity * round(line.unit_price_dollars * ctx.minor_units) for line in order.lines)
    declared_cents = round(order.total_dollars * ctx.minor_units)
    if declared_cents != calculated_cents:
        raise ValueError(
            f"declared checkout total is {declared_cents} cents, but the line total is {calculated_cents} cents"
        )
    return calculated_cents


class CheckoutMapping(Betwixt):
    """Translate the validated API checkout and the in-memory database row."""

    left = CheckoutRequest
    right = CheckoutRow
    (L, R) = field_refs(left, right)
    recipient = expand_rightward(
        left=L.recipient_display_name,
        right=(R.first_name, R.last_name),
        rightward=lambda name: tuple(name.split(maxsplit=1)),
    )
    recipient_display_name = map_leftward(
        right=(R.first_name, R.last_name),
        left=L.recipient_display_name,
        leftward=lambda first_name, last_name: f"{first_name} {last_name}",
    )
    line_items = nested_pairwise(
        left=L.lines,
        right=R.lines,
        via=CheckoutLineMapping,
        rightward=lambda value: value,
        leftward=lambda value: value,
        context_rightward=lambda context: context,
        context_leftward=lambda context: context,
    )
    total = reduce_rightward(
        right=R.total_cents,
        rightward=calculate_expected_total_cents,
    )
    total_dollars = map_leftward(
        right=R.total_cents,
        left=L.total_dollars,
        leftward=lambda cents, *, ctx: cents / ctx.minor_units,
    )


context = CurrencyContext(minor_units=100, currency="USD")
request = CheckoutRequest(
    orderId=42,
    customerEmail="ada@example.com",
    status="paid",
    recipientName="Ada Lovelace",
    postalCode="90210",
    lines=[CheckoutLine(line_id=1, sku="BOOK-42", quantity=2, unitPrice=12.50)],
    total=25.00,
)
mapping = CheckoutMapping()
row = mapping.rightward(request, context=context)
response = mapping.leftward(row, context=context)
wire_response = response.model_dump(by_alias=True)
patch = mapping.rightward_partial({"order_id": 43, "status": "shipped"}, context=context)
explanation = mapping.explain_rightward()
status_by_field = {entry.destination: entry.status for entry in explanation.entries}

assert row.total_cents == 2500
assert row.lines[0].unit_price_cents == 1250
assert response.recipient_display_name == "Ada Lovelace"
assert wire_response["orderId"] == 42
assert patch == {"order_id": 43, "status": "shipped"}
assert "total_cents" not in patch
assert status_by_field["order_id"] == "implicit"
assert status_by_field["total_cents"] == "explicit"
```


## What this example demonstrates

- Pydantic accepts wire aliases while Betwixt references canonical Python names. `model_dump(by_alias=True)` puts the
  aliases back on the response.
- SQLAlchemy keeps database column names separate from Python attributes and exposes an already populated `lines`
  relationship for the nested mapping.
- `nested_pairwise` maps a list of API lines to a list of stored lines. `map_pairwise` receives the typed `ctx` context
  for dollar and cent conversion in both directions.
- `expand_rightward` splits the recipient name, while `map_leftward` joins the stored first and last names again.
- `reduce_rightward` recalculates and checks the persisted `total_cents` from every line in the complete API order
  against
  the declared total. Its reverse is an explicit `map_leftward`, not an assumed inverse.
- `rightward_partial` uses canonical keys and returns a sparse dictionary. The reduction waits because a partial input
  is not a complete order, and no destination model is constructed.
- `explain_rightward()` makes the mapping readable: same-name compatible fields such as `order_id`, `customer_email`,
  `status`, and `postal_code` are implicit, while the line, name, money, and total conversions are explicit.

For the underlying callable shapes, see the [mapping constructs](../concepts.md) and [adapter guide](../adapters.md).
