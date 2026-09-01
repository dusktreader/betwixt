"""Reference a bidirectional Pydantic-to-SQLAlchemy boundary mapping."""

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from betwixt import Betwixt, expand_rightward, field_refs, map_leftward, map_pairwise


class AccountModel(BaseModel):
    """Validate the API representation with explicit wire aliases."""

    model_config = ConfigDict(populate_by_name=True)
    email: str = Field(validation_alias="emailAddress", serialization_alias="emailAddress")
    display_name: str = Field(validation_alias="displayName", serialization_alias="displayName")
    balance_dollars: float = Field(validation_alias="balanceDollars", serialization_alias="balanceDollars", ge=0)


class Base(DeclarativeBase):
    """Provide a local SQLAlchemy declarative registry."""


class AccountRow(Base):
    """Persist canonical Python attributes under storage-specific column names."""

    __tablename__ = "demo_accounts"
    email: Mapped[str] = mapped_column("email_address", String(100), primary_key=True)
    first_name: Mapped[str] = mapped_column("given_name", String(50))
    last_name: Mapped[str] = mapped_column("family_name", String(50))
    amount_cents: Mapped[int] = mapped_column("balance_cents", Integer)


class AccountTwixt(Betwixt):
    """Translate aliases, split names, and convert dollars and cents both ways."""

    left = AccountModel
    right = AccountRow
    (L, R) = field_refs(left, right)
    email = map_pairwise(left=L.email, right=R.email, rightward=str.lower, leftward=str.lower)
    split_name = expand_rightward(
        left=L.display_name,
        right=(R.first_name, R.last_name),
        rightward=lambda display_name: tuple(display_name.split(maxsplit=1)),
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


account_twixt = AccountTwixt()
request = AccountModel(
    emailAddress="ADA@EXAMPLE.COM",
    displayName="Ada Lovelace",
    balanceDollars=123.45,
)
account_row = account_twixt.rightward(request)
response = account_twixt.leftward(account_row)
row_columns = {column.key: getattr(account_row, column.key) for column in account_row.__mapper__.column_attrs}
wire_response = response.model_dump(by_alias=True)
