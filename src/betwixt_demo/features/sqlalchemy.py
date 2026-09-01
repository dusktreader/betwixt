"""Optional SQLAlchemy demo."""


def demo_sqlalchemy() -> None:
    """
    Install `betwixt[sqlalchemy]` to map a dataclass into a native ORM object.

    The dataclass supplies the source object. Betwixt uses Python attribute names at the boundary, so SQLAlchemy's
    `email_address` column name remains an internal storage detail while native ORM construction handles the destination.
    """
    from dataclasses import dataclass

    from sqlalchemy import String
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

    from betwixt import Betwixt, field_refs, map_rightward

    class Base(DeclarativeBase):
        pass

    @dataclass
    class UserPayload:
        id: int
        email: str

    class UserRow(Base):
        __tablename__ = "demo_users"
        id: Mapped[int] = mapped_column(primary_key=True)
        email: Mapped[str] = mapped_column("email_address", String(100))

    class RowTwixt(Betwixt):
        left = UserPayload
        right = UserRow
        (L, R) = field_refs(left, right)
        email = map_rightward(left=L.email, right=R.email, rightward=str.lower)

    result = RowTwixt().rightward(UserPayload(id=7, email="ADA@EXAMPLE.COM"))
    print({column.key: getattr(result, column.key) for column in result.__mapper__.column_attrs})
