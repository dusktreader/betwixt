"""Combined Pydantic and SQLAlchemy demo."""


def demo_combined() -> None:
    """
    Translate one bidirectional API model into an ORM row and back again.

    Install the `betwixt[pydantic,sqlalchemy]` extra to run this complete pipeline. Pydantic validates API aliases,
    Betwixt makes both boundary transformations explicit, and SQLAlchemy keeps database column names and integer cents
    behind canonical Python attributes. The request mapping expands one `display_name` value into two ORM fields, while
    the response mapping merges those fields back together; pairwise mappings are insufficient when the representations
    have different field counts.
    """
    from pydantic import BaseModel, ConfigDict, Field
    from sqlalchemy import Integer, String
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    from betwixt import Betwixt, expand_rightward, field_refs, map_leftward, map_pairwise

    class Base(DeclarativeBase):
        pass

    class AccountRow(Base):
        __tablename__ = "demo_accounts"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column("email_address", String(100))
        first_name: Mapped[str] = mapped_column("given_name", String(50))
        last_name: Mapped[str] = mapped_column("family_name", String(50))
        amount_cents: Mapped[int] = mapped_column("balance_cents", Integer)

    class AccountModel(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        id: int
        email: str = Field(validation_alias="emailAddress", serialization_alias="emailAddress")
        display_name: str = Field(validation_alias="displayName", serialization_alias="displayName")
        balance_dollars: float = Field(validation_alias="balanceDollars", serialization_alias="balanceDollars", ge=0)

    class AccountTwixt(Betwixt):
        left = AccountModel
        right = AccountRow
        (L, R) = field_refs(left, right)
        email = map_pairwise(
            left=L.email, right=R.email, rightward=lambda value: value.lower(), leftward=lambda value: value
        )
        name = expand_rightward(
            left=L.display_name,
            right=(R.first_name, R.last_name),
            rightward=lambda display_name: tuple(display_name.split(maxsplit=1)),
        )
        display_name = map_leftward(
            right=(R.first_name, R.last_name),
            left=L.display_name,
            leftward=lambda first_name, last_name: f"{first_name} {last_name}",
        )
        amount_cents = map_pairwise(
            left=L.balance_dollars,
            right=R.amount_cents,
            rightward=lambda dollars: round(dollars * 100),
            leftward=lambda cents: cents / 100,
        )

    request = AccountModel(
        id=7,
        emailAddress="ADA@EXAMPLE.COM",
        displayName="Ada Lovelace",
        balanceDollars=123.45,
    )
    twixt = AccountTwixt()
    row = twixt.rightward(request)
    response = twixt.leftward(row)

    print({column.key: getattr(row, column.key) for column in row.__mapper__.column_attrs})
    print(response.model_dump(by_alias=True))
