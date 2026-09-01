# Comparison

Applications regularly carry the same concept through several boundaries: a web request, a domain object, a persistence
record, a message, or a response. Each representation has its own ownership, validation rules, naming, and shape, so
translation logic appears wherever those representations meet. When that logic is spread across the models on either
side,
it becomes difficult to discover, test, and keep symmetric where symmetry is intended.

Pydantic and SQLAlchemy provide a concrete example of this broader problem. Each library does its own job well. The
friction appears at the boundary, where one representation has to become the other. Betwixt makes that translation a
named, inspectable relationship instead of scattering it across model configuration and framework hooks.


## The boundary problem

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

One common alternative is to make each framework participate in the conversion. The request model may normalize or split
the display name, the ORM model may expose convenience properties, and the endpoint may still need to convert dollars to
cents:

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

This can work, but the request and response rules are now distributed across model methods, ORM properties, and endpoint
code. It is easy for one direction to change without updating the other, and the boundary behavior is no longer visible
from one declaration.

You can imagine that as a project grows and complexity increases, the mappings grow more scattered and obsfucated by
other business logic. Understanding how one data type is translated to the other can become a chore.


## The explicit relationship

Betwixt keeps the models focused and puts the representation differences in one declaration. The field refs use
canonical Python attributes, not `displayName`, `given_name`, or `balance_cents`:

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

The same `AccountTwixt` produces the ORM row for a request and reconstructs the API model for a response:

```python
account = AccountRequest(displayName="Ada Lovelace", balanceDollars=123.45)
row = AccountTwixt().rightward(account)
response = AccountTwixt().leftward(row)
```

The declaration names both directions and puts the split, merge, and cents conversion next to one another. Pydantic
still validates its native model, SQLAlchemy still owns its ORM model, and the mapping layer owns only the translation
between them. The shared `id` field is not declared because its name and type already match; Betwixt maps it implicitly.
That separation makes the boundary easier to understand, test, and change.

Betwixt is not a serializer, validator, ORM, or schema generator. It is the explicit peer-to-peer translation layer
between those concerns.


## What's next

- Read the [feature guide](features.md) for the individual mapping constructs.
- Browse the [case studies](cases/index.md) for longer boundary examples.
- See the [adapter guide](adapters.md) for adapter behavior and custom adapters.
