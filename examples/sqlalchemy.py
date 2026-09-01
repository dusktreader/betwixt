"""Reference a dataclass-to-SQLAlchemy mapping without persistence."""

from dataclasses import dataclass

from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from betwixt import Betwixt, field_refs, map_rightward


class Base(DeclarativeBase):
    """Provide a local SQLAlchemy declarative registry."""


@dataclass
class UserInput:
    """Represent a non-SQLAlchemy source payload."""

    id: int
    email: str


class UserRow(Base):
    """Represent one ORM destination with a mapped storage-column name."""

    __tablename__ = "demo_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column("email_address", String(100))


class UserTwixt(Betwixt):
    """Map source attributes to the ORM model's Python attributes."""

    left = UserInput
    right = UserRow
    (L, R) = field_refs(left, right)
    email = map_rightward(left=L.email, right=R.email, rightward=str.lower)


user_row = UserTwixt().rightward(UserInput(7, "ADA@EXAMPLE.COM"))
mapped_columns = {column.key: getattr(user_row, column.key) for column in user_row.__mapper__.column_attrs}
