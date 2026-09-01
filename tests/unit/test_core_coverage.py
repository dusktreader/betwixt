"""Reachability tests for the dependency-free core and adapter boundaries."""

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Annotated, Any, ForwardRef

import pytest
from betwixt.adapters.base import optional_adapter, require_adapter
from betwixt.adapters.dataclass import DataclassAdapter
from betwixt.annotations import compatible, nested_compatible, normalize, resolved_fields
from betwixt.constructs import Construct, nested_leftward
from betwixt.errors import MissingAdapterError, PartialInputError
from betwixt.refs import FieldRef

from betwixt import AdapterError, AdapterRegistry, Betwixt, DeclarationError, field_refs, map_rightward

pytestmark = pytest.mark.unit


@dataclass
class Left:
    value: int
    label: str = "left"


@dataclass
class Right:
    value: int
    label: str = "right"


def test_adapter_boundaries_and_registry_builtins(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise dataclass adapters, optional lookup, and registry fallbacks."""
    adapter = DataclassAdapter(Left)
    assert adapter.fields() == {"value": int, "label": str}
    assert adapter.read(Left(2), "value") == 2
    assert adapter.construct({"value": 4}) == Left(4)
    assert adapter.required("value") is True
    assert adapter.required("label") is False
    with pytest.raises(AdapterError, match="not a dataclass"):
        DataclassAdapter(int)

    registry = AdapterRegistry()
    assert registry.lookup(Left).type is Left
    assert registry.lookup(int) is None
    custom = object()
    registry.register(Left, custom)
    assert registry.lookup(Left) is custom
    with pytest.raises(MissingAdapterError):
        require_adapter(int, registry)

    class FakePydantic:
        __module__ = "pydantic.fake"

    class FakeSQLAlchemy:
        __module__ = "sqlalchemy.fake"

        __mapper__ = object()

    import betwixt.adapters.pydantic as pydantic_adapter
    import betwixt.adapters.sqlalchemy as sqlalchemy_adapter

    sentinel = object()
    monkeypatch.setattr(pydantic_adapter, "PydanticAdapter", lambda type_: sentinel)
    monkeypatch.setattr(sqlalchemy_adapter, "SQLAlchemyAdapter", lambda type_: sentinel)
    assert optional_adapter(FakePydantic) is sentinel
    assert optional_adapter(FakeSQLAlchemy) is sentinel

    real_import = __import__

    def fail_optional(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in {"pydantic", "betwixt.adapters.pydantic", "betwixt.adapters.sqlalchemy"}:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fail_optional)
    assert optional_adapter(int) is None
    assert optional_adapter(FakePydantic) is None
    assert optional_adapter(FakeSQLAlchemy) is None

    assert require_adapter(Left, registry) is custom
    from betwixt import get_adapter, register_adapter

    class Registered:
        pass

    register_adapter(Registered, sentinel)
    assert get_adapter(Registered) is sentinel


def test_annotation_normalization_and_compatibility_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover unresolved references, generic shapes, unions, and nested validation."""
    assert normalize(Annotated[int, "metadata"]) is int
    assert isinstance(normalize("Missing", Left), ForwardRef)
    assert normalize("int", Left) is int
    assert isinstance(normalize(ForwardRef("Missing"), Left), ForwardRef)
    assert resolved_fields(Left) == {"value": int, "label": str}

    class BadHints:
        value: ForwardRef("MissingType")  # ty: ignore[invalid-type-form]

    assert isinstance(resolved_fields(BadHints)["value"], ForwardRef)
    assert not compatible(ForwardRef("X"), int)
    assert compatible(int, Any)
    assert compatible(int, int)
    assert compatible(bool, int)
    assert not compatible(int, str)
    assert not compatible(list[int], tuple[int, ...])
    assert compatible(tuple[int, ...], tuple[int, ...])
    assert not compatible(tuple[int, ...], tuple[int, str])
    assert not compatible(tuple[int, str], tuple[int, ...])
    assert not compatible(tuple[int], tuple[int, str])
    assert compatible(dict[str, int], Mapping[str, int]) is False
    assert not compatible(list[int], list[int, str])  # ty: ignore[invalid-type-arguments]
    assert not compatible(object(), object())
    assert not compatible(tuple[int, ...], tuple[bool, ...])
    assert not compatible(deque[int], deque[str])
    from betwixt import annotations

    original_get_origin = annotations.get_origin

    def different_origins(annotation: Any) -> Any:
        if annotation is Left:
            return list
        if annotation is Right:
            return set
        return original_get_origin(annotation)

    monkeypatch.setattr(annotations, "get_origin", different_origins)
    original_issubclass = __builtins__["issubclass"] if isinstance(__builtins__, dict) else __builtins__.issubclass
    monkeypatch.setattr("builtins.issubclass", lambda *args: (_ for _ in ()).throw(TypeError()))
    assert not compatible(Left, Right)
    monkeypatch.setattr("builtins.issubclass", original_issubclass)
    monkeypatch.setattr(annotations, "get_origin", original_get_origin)

    class RaisingMeta(type):
        def __subclasscheck__(cls, subclass: Any) -> bool:
            raise TypeError

    class RaisingDestination(metaclass=RaisingMeta):
        pass

    assert not compatible(Left, RaisingDestination)
    assert nested_compatible(int, int, int, int)
    assert not nested_compatible(list[int], list[str], int, int)
    assert not nested_compatible(list[int], tuple[int, ...], int, int)
    assert not nested_compatible(int | None, int, int, int)
    assert nested_compatible(int, int | None, int, int)
    assert not nested_compatible(int | str, int | str, int, int)
    assert not nested_compatible(int | None, int | str, int, int)
    assert not nested_compatible(ForwardRef("X"), int, int, int)
    assert not nested_compatible(tuple[int, ...], tuple[int, int], int, int)
    assert not nested_compatible(tuple[int, int], tuple[int, ...], int, int)
    assert not nested_compatible(tuple[int, ...], tuple[bool, ...], int, int)
    assert not nested_compatible(tuple[int, str], tuple[bool, str], int, int)
    assert not nested_compatible(tuple[int], tuple[int, str], int, int)
    assert nested_compatible(dict[str, int], dict[str, int], int, int)
    assert not nested_compatible(dict[int, int], dict[str, int], int, int)
    assert not nested_compatible(dict[str, int], dict[str, Any], int, int)
    assert not nested_compatible(deque[int], deque[int], int, int)


def test_low_level_declaration_validation_and_base_abstractness() -> None:
    """Exercise malformed records and reject direct or argument-based base initialization."""
    with pytest.raises(TypeError, match="abstract"):
        Betwixt()

    class Concrete(Betwixt):
        left = Left
        right = Right

    with pytest.raises(TypeError):
        Concrete(Left, Right)  # ty: ignore[too-many-positional-arguments]
    with pytest.raises(TypeError):
        Concrete(left=Left, right=Right)  # ty: ignore[unknown-argument]
    with pytest.raises(DeclarationError, match="cannot subclass a concrete"):
        type("Derived", (Concrete,), {})
    with pytest.raises(DeclarationError, match="left and right types"):
        type("Bad", (Betwixt,), {"left": 1, "right": Right})

    refs = field_refs(Left, Right)
    with pytest.raises(DeclarationError, match="invalid side"):
        type(
            "Bad",
            (Betwixt,),
            {"left": Left, "right": Right, "x": Construct("x", FieldRef("middle", Left, "value"), refs[1].value)},  # ty: ignore[invalid-argument-type]
        )
    foreign = field_refs(Right, Left)
    with pytest.raises(DeclarationError, match="different declared"):
        type(
            "Bad",
            (Betwixt,),
            {
                "left": Left,
                "right": Right,
                "x": map_rightward(left=foreign[0].value, right=refs[1].value, rightward=lambda x: x),
            },
        )
    with pytest.raises(DeclarationError, match="absent"):
        type(
            "Bad",
            (Betwixt,),
            {
                "left": Left,
                "right": Right,
                "x": Construct(
                    "map_rightward", FieldRef("left", Left, "missing"), refs[1].value, rightward=lambda x: x
                ),
            },
        )

    with pytest.raises(DeclarationError, match="boolean"):
        type("InvalidDisable", (Betwixt,), {"left": Left, "right": Right, "disable_implicit_mapping": "yes"})

    with pytest.raises(DeclarationError, match="at least one"):
        type(
            "Bad",
            (Betwixt,),
            {"left": Left, "right": Right, "x": Construct("map_rightward", right=refs[1].value, rightward=lambda x: x)},
        )
    with pytest.raises(DeclarationError, match="requires its directional"):
        type(
            "Bad",
            (Betwixt,),
            {"left": Left, "right": Right, "x": Construct("map_rightward", left=refs[0].value, right=refs[1].value)},
        )
    with pytest.raises(DeclarationError, match="FieldRef"):
        type(
            "Bad",
            (Betwixt,),
            {
                "left": Left,
                "right": Right,
                "x": Construct("map_rightward", left="value", right=refs[1].value, rightward=lambda x: x),  # ty: ignore[invalid-argument-type]
            },
        )

    with pytest.raises(MissingAdapterError, match="available"):
        type("Missing", (Betwixt,), {"left": type("Unknown", (), {}), "right": Right})
    with pytest.raises(DeclarationError, match="one field"):
        type(
            "Bad",
            (Betwixt,),
            {
                "left": Left,
                "right": Right,
                "x": Construct("disable_implicit_pairwise", left=(refs[0].value, refs[0].value), right=refs[1].value),
            },
        )
    with pytest.raises(DeclarationError, match="require one"):
        type(
            "Bad",
            (Betwixt,),
            {"left": Left, "right": Right, "x": Construct("disable_implicit_pairwise", left=refs[0].value, right=None)},
        )

    class Mapping(Betwixt):
        left = Left
        right = Right

    assert Mapping().rightward(Left(1)) == Right(1, "left")
    with pytest.raises(MissingAdapterError, match="No adapter"):
        type("Missing", (Betwixt,), {"left": type("Unknown", (), {}), "right": Right})
    with pytest.raises(DeclarationError, match="no field"):
        _ = field_refs(Left, Right)[0].missing
    assert map_rightward(left=refs[0].value, right=refs[1].value, rightward=lambda value: value).kind == "map_rightward"
    assert Mapping().rightward_partial({}) == {}


def test_callable_compiler_validation_and_context(monkeypatch: pytest.MonkeyPatch) -> None:
    """Cover inspectable signatures, derivations, and context injection."""
    from betwixt.compiler import call, validate_callable, validate_derivation

    with pytest.raises(DeclarationError, match="callable"):
        validate_callable(3)
    original_signature = __import__("betwixt.compiler", fromlist=["signature"]).signature
    monkeypatch.setattr("betwixt.compiler.signature", lambda function: (_ for _ in ()).throw(ValueError()))
    with pytest.raises(DeclarationError, match="inspectable"):
        validate_callable(lambda: None)
    monkeypatch.setattr("betwixt.compiler.signature", original_signature)
    with pytest.raises(DeclarationError, match="final"):
        validate_callable(lambda *, ctx, other: None)
    validate_callable(lambda value, *, ctx: value)
    with pytest.raises(DeclarationError, match="callable"):
        validate_derivation(3)
    with pytest.raises(DeclarationError, match="one positional"):
        validate_derivation(lambda: None)
    validate_derivation(lambda value: value)
    assert call(lambda value: value + 1, (2,), object()) == 3
    assert call(lambda value, *, ctx: value + ctx, (2,), 3) == 5


def test_leftward_explanations_and_nested_partial_edges() -> None:
    """Cover reverse operations, explanation statuses, and nested partial error paths."""
    left_ref, right_ref = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        value = map_rightward(left=left_ref.value, right=right_ref.value, rightward=lambda value: value + 1)

    mapping = Mapping()
    assert mapping.leftward_partial({"value": 4}) == {"value": 4}
    assert mapping.leftward_partial({}) == {}
    assert mapping.explain_leftward().entries

    class PartialMap(Betwixt):
        left = Left
        right = Right
        value = map_rightward(left=left_ref.value, right=right_ref.value, rightward=lambda value: value)

    assert PartialMap().rightward_partial({}) == {}

    @dataclass
    class OuterLeft:
        child: Left | None

    @dataclass
    class OuterRight:
        child: Right | None

    outer_left, outer_right = field_refs(OuterLeft, OuterRight)

    class Outer(Betwixt):
        left = OuterLeft
        right = OuterRight
        child = __import__("betwixt").nested_rightward(
            left=outer_left.child, right=outer_right.child, via=mapping, rightward=lambda value: value
        )

    assert Outer().rightward(OuterLeft(None)) == OuterRight(None)
    with pytest.raises(PartialInputError, match="child"):
        Outer().rightward_partial({"child": 1})
    with pytest.raises(PartialInputError, match=r"child: child: unknown source"):
        Outer().rightward_partial({"child": {"missing": 1}})

    from betwixt.betwixt import _nested

    class FailingInner:
        def rightward(self, value: Any, *, context: Any = None) -> Any:
            raise PartialInputError("inner failure")

    with pytest.raises(PartialInputError, match=r"value: inner failure"):
        _nested(FailingInner(), Left(1), "rightward", None, False)  # ty: ignore[invalid-argument-type]
    with pytest.raises(PartialInputError, match="null is not allowed"):
        _nested(FailingInner(), None, "rightward", None, True, shape=int | str)  # ty: ignore[invalid-argument-type]
    with pytest.raises(PartialInputError, match="null is not allowed"):
        _nested(FailingInner(), None, "rightward", None, True, shape=int)  # ty: ignore[invalid-argument-type]


def test_optional_adapters_cover_native_boundaries() -> None:
    """Exercise the installed optional adapters without making core imports depend on them."""
    pytest.importorskip("pydantic")
    pytest.importorskip("sqlalchemy")
    from betwixt.adapters.pydantic import PydanticAdapter
    from betwixt.adapters.sqlalchemy import SQLAlchemyAdapter
    from betwixt.errors import UnloadedFieldError
    from pydantic import BaseModel, ConfigDict, Field
    from sqlalchemy import ForeignKey, String
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

    class Model(BaseModel):
        value: int

    pydantic = PydanticAdapter(Model)
    assert pydantic.fields() == {"value": int}
    assert pydantic.read(Model(value=1), "value") == 1
    assert pydantic.construct({"value": "2"}).value == 2
    assert pydantic.required("value") is True

    class Aliased(BaseModel):
        model_config = ConfigDict(populate_by_name=False)
        value: int = Field(validation_alias="v")

    with pytest.raises(AdapterError, match="rejects"):
        PydanticAdapter(Aliased).construct({"value": 1})

    class Base(DeclarativeBase):
        pass

    class Child(Base):
        __tablename__ = "child"
        id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))

    class Parent(Base):
        __tablename__ = "parent"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String, nullable=False)
        children: Mapped[list[Child]] = relationship()

    sqlalchemy = SQLAlchemyAdapter(Parent)
    assert sqlalchemy.fields() == {"id": int, "name": str, "children": list[Child]}
    parent = Parent(id=1, name="parent", children=[])
    assert sqlalchemy.read(parent, "name") == "parent"
    assert sqlalchemy.construct({"id": 2, "name": "new"}).name == "new"
    assert sqlalchemy.required("id") is True
    assert sqlalchemy.required("name") is True
    assert sqlalchemy.required("children") is False
    assert sqlalchemy.read(parent, "children") == []

    unloaded = Parent(id=3, name="unloaded")
    with pytest.raises(UnloadedFieldError):
        sqlalchemy.read(unloaded, "children")


def test_optional_adapter_missing_dependency_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the direct optional adapter constructors actionable when imports fail."""
    real_import = __import__

    def fail(name: str, *args: Any, **kwargs: Any) -> Any:
        if name in {"pydantic", "sqlalchemy"}:
            raise ImportError(name)
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fail)
    from betwixt.adapters.pydantic import PydanticAdapter
    from betwixt.adapters.sqlalchemy import SQLAlchemyAdapter

    with pytest.raises(ImportError, match=r"betwixt\[pydantic\]") as pydantic_error:
        PydanticAdapter(Left)
    assert isinstance(pydantic_error.value.__cause__, ImportError)
    with pytest.raises(ImportError, match=r"betwixt\[sqlalchemy\]") as sqlalchemy_error:
        SQLAlchemyAdapter(Left)
    assert isinstance(sqlalchemy_error.value.__cause__, ImportError)


def test_nested_declaration_validation_and_explanation_omissions() -> None:
    """Reject malformed nested records and report incompatible, disabled, and unmapped destinations."""
    inner_left, inner_right = field_refs(Left, Right)

    class Inner(Betwixt):
        left = Left
        right = Right
        value = map_rightward(left=inner_left.value, right=inner_right.value, rightward=lambda value: value)

    assert (
        nested_leftward(left=inner_left.value, right=inner_right.value, via=Inner, leftward=lambda value: value).kind
        == "nested_leftward"
    )

    @dataclass
    class WideLeft:
        value: int
        incompatible: int
        label: str = "wide-left"

    @dataclass
    class WideRight:
        value: int
        incompatible: str
        missing: float
        label: str = "wide"

    wide_left, wide_right = field_refs(WideLeft, WideRight)
    with pytest.raises(DeclarationError, match="require via"):
        type(
            "NoVia",
            (Betwixt,),
            {
                "left": WideLeft,
                "right": WideRight,
                "x": Construct("nested_rightward", wide_left.value, wide_right.value, rightward=lambda value: value),
            },
        )
    with pytest.raises(DeclarationError, match="must be a Betwixt"):
        type(
            "BadVia",
            (Betwixt,),
            {
                "left": WideLeft,
                "right": WideRight,
                "x": Construct(
                    "nested_rightward", wide_left.value, wide_right.value, via=object(), rightward=lambda value: value
                ),
            },
        )

    @dataclass
    class BoxLeft:
        child: Left

    @dataclass
    class BoxRight:
        child: str

    box_left, box_right = field_refs(BoxLeft, BoxRight)
    with pytest.raises(DeclarationError, match="nested field"):
        type(
            "BadShape",
            (Betwixt,),
            {
                "left": BoxLeft,
                "right": BoxRight,
                "x": Construct(
                    "nested_rightward", box_left.child, box_right.child, via=Inner, rightward=lambda value: value
                ),
            },
        )

    class Reported(Betwixt):
        left = WideLeft
        right = WideRight
        disable = Construct("disable_implicit_rightward", left=wide_left.label, right=wide_right.label)

    report = Reported().explain_rightward()
    assert {entry.status for entry in report} == {"implicit", "omitted", "unmapped"}
    assert any(entry.reason == "implicit mapping disabled" for entry in report)
    assert any(entry.reason == "incompatible annotations" for entry in report)
    assert any(entry.status == "unmapped" for entry in report)

    missing_left, _ = field_refs(Left, Right)

    class MissingReference(Betwixt):
        left = Left
        right = Right
        broken = Construct("map_rightward", left=missing_left.value, right=None, rightward=lambda value: value)

    with pytest.raises(DeclarationError, match="missing a field"):
        MissingReference().rightward(Left(1))

    @dataclass
    class PairLeft:
        child: Left

    @dataclass
    class PairRight:
        child: Right

    pair_left, pair_right = field_refs(PairLeft, PairRight)
    pair = type(
        "Pair",
        (Betwixt,),
        {
            "left": PairLeft,
            "right": PairRight,
            "child": __import__("betwixt").nested_pairwise(
                left=pair_left.child,
                right=pair_right.child,
                via=Inner,
                rightward=lambda value: value,
                leftward=lambda value: value,
            ),
        },
    )()
    assert pair.leftward(PairRight(Right(2))) == PairLeft(Left(2, "right"))
