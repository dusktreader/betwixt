# Comparison

Most applications represent the same thing in several places. It might appear as a web request, an application model, a
database row, a message, or a response. Each version has its own job, so the names, validation, and shape can differ.
Without a clear home, conversion rules end up scattered across the models at each boundary. That makes them harder to
find, test, and keep in sync.

Pydantic and SQLAlchemy make this problem easy to see. Each library does its own job well. The friction appears when one
representation needs to become the other. Betwixt gives that conversion a name and a home. That keeps it out of model
settings and framework-specific hooks.


## The problem at the boundary

Consider an API account with a display name and a dollar balance. The database stores first and last names separately,
keeps money as integer cents, and uses storage-specific column names:

```python
class AccountRequest(BaseModel):
    id: int
    display_name: str = Field(alias="displayName")
    balance_dollars: float = Field(alias="balanceDollars", ge=0)


class AccountRow(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column("given_name")
    last_name: Mapped[str] = mapped_column("family_name")
    amount_cents: Mapped[int] = mapped_column("balance_cents")
```

One way to handle this is to make each framework help with the conversion. The request model can split the display name,
the database model can expose convenience properties, and the endpoint can convert dollars to cents:

```python
class AccountRequest(BaseModel):
    id: int
    display_name: str = Field(alias="displayName")
    balance_dollars: float = Field(alias="balanceDollars", ge=0)

    def to_row_values(self) -> dict[str, object]:
        first_name, last_name = self.display_name.split(" ", 1)
        return {
            "id": self.id,
            "first_name": first_name,
            "last_name": last_name,
            "amount_cents": round(self.balance_dollars * 100),
        }


class AccountRow(Base):
    @property
    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def balance_dollars(self) -> float:
        return self.amount_cents / 100


def response_from_row(row: AccountRow) -> AccountResponse:
    return AccountResponse(
        id=row.id,
        displayName=row.display_name,
        balanceDollars=row.balance_dollars,
    )
```

This can work, but the request and response rules are now spread across model methods, database properties, and endpoint
code. One direction can change without the other being updated, and you cannot see the whole conversion in one place.

As the project grows, conversion rules can get mixed in with unrelated business logic. Finding out how one model becomes
another turns into detective work.


## Put the relationship in one place

Betwixt keeps each model focused and puts the differences in one mapping. The field references use the model's canonical
Python attributes, not `displayName`, `given_name`, or `balance_cents`:

```python
from betwixt import Betwixt, expand_rightward, field_refs, map_leftward, map_pairwise


class AccountTwixt(Betwixt):
    left = AccountRequest
    right = AccountRow
    (L, R) = field_refs(left, right)
    split_name = expand_rightward(
        left=L.display_name,
        right=(R.first_name, R.last_name),
        rightward=lambda display_name: tuple(display_name.split(" ", 1)),
    )
    merge_name = map_leftward(
        right=(R.first_name, R.last_name),
        left=L.display_name,
        leftward=lambda first_name, last_name: f"{first_name} {last_name}",
    )
    balance = map_pairwise(
        left=L.balance_dollars,
        right=R.amount_cents,
        rightward=lambda dollars: round(dollars * 100),
        leftward=lambda cents: cents / 100,
    )
```

A single `AccountTwixt` can create the database row from a request and rebuild the API model for a response:

```python
account = AccountRequest(displayName="Ada Lovelace", balanceDollars=123.45)
row = AccountTwixt().rightward(account)
response = AccountTwixt().leftward(row)
```

The declaration names both directions and keeps the split, merge, and cents conversion together.

Pydantic still validates its model. SQLAlchemy still manages its database model. The mapping owns only the conversion
between them.

The shared `id` field already matches on both sides, so Betwixt maps it automatically. This makes the boundary easier to
understand, test, and change.

Betwixt is not a serializer, validator, ORM, or schema generator. It is the place where those different models are
explicitly translated into one another.


## What's next

- Read the [feature guide](features.md) for the individual mapping constructs.
- Browse the [case studies](cases/index.md) for longer boundary examples.
- See the [adapter guide](adapters.md) for adapter behavior and custom adapters.
