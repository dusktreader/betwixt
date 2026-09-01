"""Contract tests for the core declaration and execution layer."""

from dataclasses import dataclass
from typing import Annotated, Any

import pytest
from betwixt.adapters.dataclass import DataclassAdapter
from betwixt.adapters.registry import registry
from betwixt.annotations import compatible, nested_compatible, normalize

from betwixt import (
    AdapterError,
    AdapterRegistry,
    Betwixt,
    DeclarationError,
    PartialInputError,
    UnmappedFieldError,
    disable_implicit_pairwise,
    field_refs,
    map_leftward,
    map_pairwise,
    map_rightward,
    nested_rightward,
    project_leftward,
    project_rightward,
    reduce_rightward,
)

pytestmark = pytest.mark.unit


@dataclass
class A:
    value: int
    label: str = "a"


@dataclass
class B:
    value: int
    label: str = "b"


def test_registry_precedence_duplicate_and_replace() -> None:
    """Resolve exact registrations before bases and reject accidental replacement."""
    registry = AdapterRegistry()
    base = object()
    exact = object()
    registry.register(object, base)
    assert registry.lookup(A) is base
    registry.register(A, exact)
    assert registry.lookup(A) is exact
    with pytest.raises(AdapterError):
        registry.register(A, object())
    replacement = object()
    registry.register(A, replacement, replace=True)
    assert registry.lookup(A) is replacement


def test_declared_mapping_keeps_adapters_after_registry_replacement(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep both directional adapter snapshots stable while new mappings use replacements."""

    @dataclass
    class RegistryLeft:
        value: int

    @dataclass
    class RegistryRight:
        value: int

    class RecordingAdapter:
        """Record construction while delegating native dataclass behavior."""

        def __init__(self, type_: type[Any], label: str) -> None:
            self.type = type_
            self.label = label
            self.delegate = DataclassAdapter(type_)
            self.constructed: list[str] = []

        def fields(self) -> dict[str, Any]:
            return self.delegate.fields()

        def read(self, value: Any, name: str) -> Any:
            return self.delegate.read(value, name)

        def construct(self, values: dict[str, Any]) -> Any:
            self.constructed.append(self.label)
            return self.delegate.construct(values)

        def required(self, name: str) -> bool:
            return self.delegate.required(name)

    monkeypatch.setattr(registry, "_registered", {})
    original_left = RecordingAdapter(RegistryLeft, "original-left")
    original_right = RecordingAdapter(RegistryRight, "original-right")
    replacement_left = RecordingAdapter(RegistryLeft, "replacement-left")
    replacement_right = RecordingAdapter(RegistryRight, "replacement-right")
    registry.register(RegistryLeft, original_left)
    registry.register(RegistryRight, original_right)

    class Original(Betwixt):
        left = RegistryLeft
        right = RegistryRight

    registry.register(RegistryLeft, replacement_left, replace=True)
    registry.register(RegistryRight, replacement_right, replace=True)

    class Replacement(Betwixt):
        left = RegistryLeft
        right = RegistryRight

    assert Original().rightward(RegistryLeft(1)) == RegistryRight(1)
    assert Original().leftward(RegistryRight(2)) == RegistryLeft(2)
    assert Replacement().rightward(RegistryLeft(3)) == RegistryRight(3)
    assert Replacement().leftward(RegistryRight(4)) == RegistryLeft(4)
    assert original_left.constructed == ["original-left"]
    assert original_right.constructed == ["original-right"]
    assert replacement_left.constructed == ["replacement-left"]
    assert replacement_right.constructed == ["replacement-right"]


def test_annotations_cover_forward_optional_generics_and_any() -> None:
    """Apply recursive compatibility without treating Any as a nested element type."""
    assert normalize(Annotated[int, "metadata"]) is int
    assert compatible(list[int], list[int])
    assert not compatible(tuple[int, ...], tuple[int, int])
    assert not compatible(tuple[int, int], tuple[int, ...])
    assert compatible(int, int | None)
    assert not compatible(int | None, int)
    assert compatible(Any, dict[str, int])
    assert not nested_compatible(list[Any], list[int], int, int)
    assert nested_compatible(list[int] | None, list[int] | None, int, int)


def test_pairwise_and_directional_calls_are_independent() -> None:
    """Use source-reference order and never synthesize an inverse callable."""
    L, R = field_refs(A, B)

    class Mapping(Betwixt):
        left = A
        right = B
        pair = map_pairwise(
            left=L.value, right=R.value, rightward=lambda value: value + 1, leftward=lambda value: value - 1
        )
        back = map_leftward(right=R.label, left=L.label, leftward=lambda label: label.upper())

    assert Mapping().rightward(A(2, "xyz")).value == 3
    assert Mapping().leftward(B(5, "ok")) == A(4, "OK")


def test_native_defaults_projection_reduction_and_unmapped_errors() -> None:
    """Run complete-object producers and preserve native model construction boundaries."""
    _, R = field_refs(A, B)

    class Mapping(Betwixt):
        left = A
        right = B
        total = reduce_rightward(right=R.value, rightward=lambda source: source.value * 2)
        projection = project_rightward(rightward=lambda source: B(source.value + 1, source.label))

    mapping = Mapping()
    assert mapping.rightward(A(2, "x")) == B(3, "x")
    assert mapping.rightward(A(2)) == B(3, "a")

    @dataclass
    class Required:
        missing: int

    class Broken(Betwixt):
        left = A
        right = Required

    with pytest.raises(UnmappedFieldError):
        Broken().rightward(A(1))


def test_projection_is_explicit_and_adapter_validated() -> None:
    """Represent projections in explanations and reject invalid projection objects."""

    class Mapping(Betwixt):
        left = A
        right = B
        projection = project_rightward(rightward=lambda source: B(source.value + 1, source.label))

    mapping = Mapping()
    assert mapping.rightward(A(2, "x")) == B(3, "x")
    assert [entry.status for entry in mapping.explain_rightward().entries] == ["explicit", "explicit"]

    class ReverseMapping(Betwixt):
        left = A
        right = B
        projection = project_leftward(leftward=lambda target: A(target.value - 1, target.label))

    reverse = ReverseMapping()
    assert reverse.leftward(B(3, "x")) == A(2, "x")
    assert [entry.status for entry in reverse.explain_leftward().entries] == ["explicit", "explicit"]

    class WrongType(Betwixt):
        left = A
        right = B
        projection = project_rightward(rightward=lambda source: {"value": source.value, "label": source.label})

    with pytest.raises(AdapterError, match="projection returned"):
        WrongType().rightward(A(2, "x"))

    class ExtraField(Betwixt):
        left = A
        right = B
        projection = project_rightward(rightward=lambda source: _projected_with_extra(source))

    with pytest.raises(AdapterError, match="unknown fields"):
        ExtraField().rightward(A(2, "x"))

    class UnreadableField(Betwixt):
        left = A
        right = B
        projection = project_rightward(rightward=lambda source: _projected_without_value(source))

    with pytest.raises(AdapterError, match="unreadable field"):
        UnreadableField().rightward(A(2, "x"))


def test_slotted_dataclass_projection_extracts_declared_fields() -> None:
    """Extract projection fields from a slotted dataclass without requiring an instance dictionary."""

    @dataclass(slots=True)
    class Slotted:
        value: int
        label: str = "slotted"

    adapter = DataclassAdapter(Slotted)
    projected = Slotted(3)

    assert adapter.project(projected) == {"value": 3, "label": "slotted"}


def test_normal_dataclass_projection_rejects_unknown_instance_fields() -> None:
    """Reject an undeclared public attribute on a dataclass with an instance dictionary."""
    adapter = DataclassAdapter(B)
    projected = B(3)
    projected.extra = True  # ty: ignore[unresolved-attribute]

    with pytest.raises(AdapterError, match="unknown fields.*extra"):
        adapter.project(projected)


def _projected_with_extra(source: A) -> B:
    """Create a valid destination carrying an undeclared projected attribute."""
    projected = B(source.value, source.label)
    projected.extra = True  # ty: ignore[unresolved-attribute]
    return projected


def _projected_without_value(source: A) -> B:
    """Create a destination whose declared value cannot be read."""
    projected = B(source.value, source.label)
    del projected.value
    return projected


def test_nested_containers_and_partial_paths() -> None:
    """Reuse derived context across containers and report malformed partial paths."""
    calls: list[Any] = []
    inner_left, inner_right = field_refs(A, B)

    class Inner(Betwixt):
        left = A
        right = B
        value_map = map_rightward(
            left=inner_left.value, right=inner_right.value, rightward=lambda value, *, ctx: value + ctx
        )

    @dataclass
    class OuterA:
        values: list[A]

    @dataclass
    class OuterB:
        values: list[B]

    outer_left, outer_right = field_refs(OuterA, OuterB)

    class Outer(Betwixt):
        left = OuterA
        right = OuterB
        values = nested_rightward(
            left=outer_left.values,
            right=outer_right.values,
            via=Inner,
            rightward=lambda value: value,
            context_rightward=lambda context: calls.append(context) or context,
        )

    assert Outer().rightward(OuterA([A(1), A(2)]), context=3).values == [B(4, "a"), B(5, "a")]
    assert calls == [3]
    with pytest.raises(PartialInputError, match="partial operations"):
        Inner().rightward_partial(A(1))  # ty: ignore[invalid-argument-type]


def test_declaration_validation_and_explanation_are_side_effect_free() -> None:
    """Reject invalid declarations before execution and report canonical statuses."""
    L, R = field_refs(A, B)
    with pytest.raises(DeclarationError, match="equal canonical"):

        class Invalid(Betwixt):
            left = A
            right = B
            bad = disable_implicit_pairwise(left=L.value, right=R.label)

    class Mapping(Betwixt):
        left = A
        right = B
        value = map_rightward(left=L.value, right=R.value, rightward=lambda value: value + 1)

    statuses = [entry.status for entry in Mapping().explain_rightward()]
    assert statuses == ["explicit", "implicit"]
