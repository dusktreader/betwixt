"""SQLAlchemy adapter contract tests."""

from dataclasses import dataclass

from betwixt.adapters.sqlalchemy import SQLAlchemyAdapter
from pytest import raises
from sqlalchemy import ForeignKey, String, create_engine, event, inspect, select
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, raiseload, relationship

from betwixt import (
    AdapterError,
    AdapterRegistry,
    Betwixt,
    UnloadedFieldError,
    UnmappedFieldError,
    field_refs,
    map_pairwise,
    map_rightward,
    nested_rightward,
)


class Base(DeclarativeBase):
    """Provide a declarative registry for adapter tests."""


class Child(Base):
    """Provide a mapped relationship target."""

    __tablename__ = "child"
    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
    name: Mapped[str] = mapped_column(String(20))
    parent: Mapped["Parent"] = relationship(back_populates="children")


class Parent(Base):
    """Provide mapped scalar and relationship attributes."""

    __tablename__ = "parent"
    id: Mapped[int] = mapped_column(primary_key=True)
    python_name: Mapped[str] = mapped_column("database_name")
    optional_name: Mapped[str | None] = mapped_column(nullable=False)
    server_name: Mapped[str] = mapped_column(server_default="server")
    children: Mapped[list[Child]] = relationship(back_populates="parent")


def test_fields_use_python_names_and_normalize_mapped_annotations() -> None:
    """Expose only mapper attributes under their canonical Python names."""
    adapter = SQLAlchemyAdapter(Parent)

    assert set(adapter.fields()) == {"id", "python_name", "optional_name", "server_name", "children"}
    assert adapter.fields()["python_name"] is str
    assert adapter.fields()["children"] == list[Child]
    assert adapter.required("id") is True
    assert adapter.required("optional_name") is False
    assert adapter.required("server_name") is True
    assert adapter.required("children") is False


def test_projection_reads_loaded_mapped_fields_and_rejects_wrong_types() -> None:
    """Validate projected SQLAlchemy objects through the mapped adapter."""
    adapter = SQLAlchemyAdapter(Parent)
    parent = Parent(id=1, python_name="value", optional_name="optional", server_name="server", children=[])
    assert adapter.project(parent) == {
        "id": 1,
        "python_name": "value",
        "optional_name": "optional",
        "server_name": "server",
        "children": [],
    }
    with raises(AdapterError, match="expected Parent"):
        adapter.project(object())
    with raises(AdapterError, match="unreadable field"):
        adapter.project(Parent(id=2, python_name="value", optional_name="optional", server_name="server"))


def test_projection_rejects_unknown_public_fields_but_allows_internal_state() -> None:
    """Reject dynamic public attributes without rejecting SQLAlchemy instrumentation state."""
    adapter = SQLAlchemyAdapter(Parent)
    parent = Parent(id=1, python_name="value", optional_name="optional", server_name="server", children=[])
    assert adapter.project(parent)["id"] == 1
    parent.extra = True  # ty: ignore[unresolved-attribute]

    with raises(AdapterError, match="unknown fields.*extra"):
        adapter.project(parent)


def test_unloaded_relationship_is_not_read() -> None:
    """Raise an owned error without invoking a lazy relationship loader."""
    parent = Parent(id=1, python_name="value", optional_name=None)
    assert "children" in inspect(parent).unloaded


def test_unloaded_relationship_full_and_partial_paths_are_loader_proof() -> None:
    """Reject unloaded relationships fully and omit them sparsely without invoking a loader."""
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    statements: list[str] = []

    @event.listens_for(engine, "before_cursor_execute")
    def record_statement(*args: object, **kwargs: object) -> None:
        statements.append(str(args[2]))

    with Session(engine) as session:
        session.add(Parent(id=1, python_name="value", optional_name="optional", children=[]))
        session.commit()
        loaded_parent = session.scalar(select(Parent).where(Parent.id == 1))
        assert loaded_parent is not None
        session.expire(loaded_parent, ["children"])
        assert "children" in inspect(loaded_parent).unloaded
        before = len(statements)
        adapter = SQLAlchemyAdapter(Parent)
        with raises(UnloadedFieldError):
            adapter.read(loaded_parent, "children")
        assert SQLAlchemyAdapter(Parent).read(loaded_parent, "python_name") == "value"
        assert len(statements) == before

        refs_left, refs_right = field_refs(Parent, Parent)

        class Mapping(Betwixt):
            left = Parent
            right = Parent
            children = map_rightward(
                left=refs_left.children,
                right=refs_right.children,
                rightward=lambda value: value,
            )

        with raises(UnloadedFieldError):
            Mapping().rightward(loaded_parent)
        assert Mapping().rightward_partial({"python_name": "new"}) == {"python_name": "new"}
        assert len(statements) == before

        detached = session.scalar(select(Parent).options(raiseload(Parent.children)))
        assert detached is not None
        with raises(InvalidRequestError):
            _ = detached.children
        session.expunge(detached)
        assert "children" in inspect(detached).unloaded
        with raises(UnloadedFieldError):
            Mapping().rightward(detached)
        assert Mapping().rightward_partial({"children": []}) == {"children": []}


def test_relationship_raise_on_lazy_remains_unloaded_during_full_translation() -> None:
    """Handle SQLAlchemy's raise-on-lazy state through the adapter-owned error."""
    parent = Parent(id=2, python_name="value", optional_name=None)
    state = inspect(parent)
    assert "children" in state.unloaded
    refs_left, refs_right = field_refs(Parent, Parent)

    class Mapping(Betwixt):
        left = Parent
        right = Parent
        children = map_rightward(
            left=refs_left.children,
            right=refs_right.children,
            rightward=lambda value: value,
        )

    with raises(UnloadedFieldError):
        Mapping().rightward(parent)
    assert "children" in inspect(parent).unloaded
    adapter = SQLAlchemyAdapter(Parent)

    with raises(UnloadedFieldError):
        adapter.read(parent, "children")
    assert "children" in inspect(parent).unloaded


def test_native_constructor_and_canonical_mapping() -> None:
    """Pass canonical names to SQLAlchemy's native constructor."""
    source = Parent(id=1, python_name="value", optional_name=None, server_name="server", children=[])
    refs_left, refs_right = field_refs(Parent, Parent)

    class Mapping(Betwixt):
        left = Parent
        right = Parent
        python_name = map_rightward(
            left=refs_left.python_name,
            right=refs_right.python_name,
            rightward=lambda value: value.upper(),
        )

    result = Mapping().rightward(source)
    assert result.python_name == "VALUE"
    assert result.id == 1


def test_leftward_full_and_partial_mapping_uses_context_and_native_construction() -> None:
    """Translate a mapped object leftward and preserve sparse canonical patches."""
    refs_left, refs_right = field_refs(Parent, Parent)

    class Mapping(Betwixt):
        left = Parent
        right = Parent
        python_name = map_pairwise(
            left=refs_left.python_name,
            right=refs_right.python_name,
            rightward=lambda value: value,
            leftward=lambda value, *, ctx="": value + ctx,
        )

    mapping = Mapping()
    source = Parent(id=1, python_name="value", optional_name="optional", server_name="server", children=[])
    assert mapping.leftward(source, context="-left").python_name == "value-left"
    assert mapping.leftward_partial({"python_name": "patched"}, context="-left") == {"python_name": "patched-left"}


def test_full_and_partial_nested_relationship_translation_uses_canonical_attributes() -> None:
    """Translate loaded SQLAlchemy relationships fully and sparsely through an inner mapping."""
    child_left, child_right = field_refs(Child, Child)

    class ChildMapping(Betwixt):
        left = Child
        right = Child
        disable_implicit_mapping = True
        id = map_rightward(left=child_left.id, right=child_right.id, rightward=lambda value: value)
        parent_id = map_rightward(left=child_left.parent_id, right=child_right.parent_id, rightward=lambda value: value)
        name = map_rightward(left=child_left.name, right=child_right.name, rightward=lambda value: value)

    parent_left, parent_right = field_refs(Parent, Parent)

    class ParentMapping(Betwixt):
        left = Parent
        right = Parent
        children = nested_rightward(
            left=parent_left.children,
            right=parent_right.children,
            via=ChildMapping,
            rightward=lambda value: value,
        )

    source = Parent(
        id=1,
        python_name="database value",
        optional_name="optional",
        server_name="server",
        children=[Child(id=2, parent_id=1, name="child")],
    )
    result = ParentMapping().rightward(source)

    assert [(child.id, child.name) for child in result.children] == [(2, "child")]
    assert ParentMapping().rightward_partial({"children": [{"name": "patched"}]}) == {"children": [{"name": "patched"}]}


def test_requiredness_rows_follow_native_sqlalchemy_constructibility() -> None:
    """Distinguish nullable, optional, Python-defaulted, relationship, and server-default fields."""

    class Requiredness(Base):
        __tablename__ = "requiredness"
        id: Mapped[int] = mapped_column(primary_key=True)
        nullable_name: Mapped[str | None] = mapped_column(nullable=True)
        optional_name: Mapped[str | None] = mapped_column(nullable=False)
        python_default: Mapped[str] = mapped_column(default="python")
        server_default: Mapped[str] = mapped_column(server_default="server")

    adapter = SQLAlchemyAdapter(Requiredness)
    assert adapter.required("nullable_name") is False
    assert adapter.required("optional_name") is False
    assert adapter.required("python_default") is False
    assert adapter.required("server_default") is True
    constructed = adapter.construct({"id": 1, "nullable_name": None, "optional_name": None})
    assert constructed.python_default is None
    assert Parent(id=3, python_name="value", optional_name="optional").children == []

    @dataclass
    class WithoutServerDefault:
        id: int
        nullable_name: str | None
        optional_name: str | None

    source_refs, destination_refs = field_refs(WithoutServerDefault, Requiredness)

    class MissingServerDefault(Betwixt):
        left = WithoutServerDefault
        right = Requiredness
        id = map_rightward(left=source_refs.id, right=destination_refs.id, rightward=lambda value: value)
        nullable_name = map_rightward(
            left=source_refs.nullable_name,
            right=destination_refs.nullable_name,
            rightward=lambda value: value,
        )
        optional_name = map_rightward(
            left=source_refs.optional_name,
            right=destination_refs.optional_name,
            rightward=lambda value: value,
        )

    with raises(UnmappedFieldError, match="server_default"):
        MissingServerDefault().rightward(WithoutServerDefault(1, None, None))


def test_exact_and_mro_adapters_override_sqlalchemy_builtin() -> None:
    """Prefer exact registrations, then nearest registered bases, over built-ins."""
    registry = AdapterRegistry()
    base_adapter = object()
    exact_adapter = object()

    class SpecializedParent(Parent):
        """Provide a mapped subclass for MRO lookup."""

    registry.register(Parent, base_adapter)
    assert registry.lookup(SpecializedParent) is base_adapter
    registry.register(SpecializedParent, exact_adapter)
    assert registry.lookup(SpecializedParent) is exact_adapter


def test_sqlalchemy_adapter_rejects_unmapped_types() -> None:
    """Report an adapter configuration error for an unmapped type."""
    from betwixt import AdapterError

    with raises(AdapterError, match="mapped"):
        SQLAlchemyAdapter(str)
