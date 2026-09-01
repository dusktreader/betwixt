"""Exhaustive core contract examples for Tasks 01 through 06."""

from dataclasses import dataclass
from typing import Annotated, Any

import pytest
from betwixt.annotations import compatible, nested_compatible, normalize
from betwixt.errors import PartialInputError, UnmappedFieldError

from betwixt import (
    AdapterError,
    AdapterRegistry,
    Betwixt,
    DeclarationError,
    disable_implicit_leftward,
    field_refs,
    map_leftward,
    map_pairwise,
    map_rightward,
    nested_leftward,
    nested_pairwise,
    nested_rightward,
    project_leftward,
    project_rightward,
    reduce_leftward,
    reduce_rightward,
)

pytestmark = pytest.mark.unit


@dataclass(frozen=True)
class Source:
    number: int
    text: str = "source"


@dataclass(frozen=True)
class Target:
    number: int
    text: str = "target"


def test_annotation_grammar_and_normalization() -> None:
    """Normalize metadata and exercise scalar, optional, tuple, mapping, and set compatibility."""
    assert normalize(Annotated[int, "ignored"]) is int
    assert compatible(int, int | None)
    assert not compatible(int | None, int)
    assert compatible(list[int], list[int])
    assert not compatible(tuple[int, ...], tuple[int, int])
    assert not compatible(tuple[int, int], tuple[int, ...])
    assert compatible(dict[str, int], dict[str, int])
    assert compatible(set[int], set[int])
    assert not compatible(list[int], set[int])
    assert not compatible(list[int], list[str])
    assert nested_compatible(list[int] | None, list[int] | None, int, int)
    assert not nested_compatible(list[Any], list[int], int, int)


def test_all_directional_construct_families() -> None:
    """Execute maps, reductions, projections, nested mappings, and suppressions in both directions."""
    L, R = field_refs(Source, Target)

    class Mapping(Betwixt):
        left = Source
        right = Target
        pair = map_pairwise(
            left=(L.number, L.text),
            right=R.number,
            rightward=lambda number, text: number + len(text),
            leftward=lambda number: number - 1,
        )
        right_text = map_rightward(left=L.text, right=R.text, rightward=str.upper)
        left_text = map_leftward(right=R.text, left=L.text, leftward=str.lower)
        right_reduce = reduce_rightward(right=R.number, rightward=lambda source: source.number * 2)
        left_reduce = reduce_leftward(left=L.number, leftward=lambda target: target.number // 2)
        right_project = project_rightward(rightward=lambda source: Target(source.number + 3, source.text))
        left_project = project_leftward(leftward=lambda target: Source(target.number - 3, target.text))

    mapping = Mapping()
    assert mapping.rightward(Source(2, "ab")) == Target(5, "ab")
    assert mapping.leftward(Target(8, "AB")) == Source(5, "AB")


def test_leftward_nested_mapping_and_suppression_are_behavioral() -> None:
    """Exercise reverse nested traversal and a valid reverse implicit suppression."""
    inner_left, inner_right = field_refs(Source, Target)

    class Inner(Betwixt):
        left = Source
        right = Target
        number = map_pairwise(
            left=inner_left.number,
            right=inner_right.number,
            rightward=lambda value: value,
            leftward=lambda value, *, ctx=0: value + ctx,
        )

    @dataclass(frozen=True)
    class LeftBox:
        child: Source

    @dataclass(frozen=True)
    class RightBox:
        child: Target

    left_box, right_box = field_refs(LeftBox, RightBox)

    class NestedMapping(Betwixt):
        left = LeftBox
        right = RightBox
        child = nested_leftward(
            left=left_box.child,
            right=right_box.child,
            via=Inner,
            leftward=lambda value: value,
            context_leftward=lambda context: context + 1,
        )

    nested = NestedMapping()
    assert nested.leftward(RightBox(Target(4)), context=2) == LeftBox(Source(7, "target"))
    assert nested.leftward_partial({"child": {"number": 4}}, context=2) == {"child": {"number": 7}}

def test_nested_shapes_and_context_are_reused_per_boundary() -> None:
    """Translate optional and supported containers while deriving context once per nested field."""
    inner_left, inner_right = field_refs(Source, Target)
    seen: list[int] = []

    class Inner(Betwixt):
        left = Source
        right = Target
        number = map_rightward(
            left=inner_left.number, right=inner_right.number, rightward=lambda number, *, ctx=0: number + ctx
        )

    @dataclass
    class BoxSource:
        optional: Source | None
        values: list[Source]
        pair: tuple[Source, Source]
        mapping: dict[str, Source]
        items: set[Source]

    @dataclass
    class BoxTarget:
        optional: Target | None
        values: list[Target]
        pair: tuple[Target, Target]
        mapping: dict[str, Target]
        items: set[Target]

    source, target = field_refs(BoxSource, BoxTarget)

    class BoxMapping(Betwixt):
        left = BoxSource
        right = BoxTarget
        optional = nested_pairwise(
            left=source.optional,
            right=target.optional,
            via=Inner,
            rightward=lambda value: value,
            leftward=lambda value: value,
            context_rightward=lambda context: seen.append(context) or context,
            context_leftward=lambda context: seen.append(context) or context,
        )
        values = nested_rightward(
            left=source.values,
            right=target.values,
            via=Inner,
            rightward=lambda value: value,
            context_rightward=lambda context: context,
        )
        pair = nested_rightward(
            left=source.pair,
            right=target.pair,
            via=Inner,
            rightward=lambda value: value,
            context_rightward=lambda context: context,
        )
        mapping = nested_rightward(
            left=source.mapping,
            right=target.mapping,
            via=Inner,
            rightward=lambda value: value,
            context_rightward=lambda context: context,
        )
        items = nested_rightward(
            left=source.items,
            right=target.items,
            via=Inner,
            rightward=lambda value: value,
            context_rightward=lambda context: context,
        )

    value = Source(1)
    result = BoxMapping().rightward(BoxSource(value, [value], (value, value), {"x": value}, {value}), context=2)
    assert result.optional == Target(3, "source")
    assert result.values == [Target(3, "source")]
    assert result.pair == (Target(3, "source"), Target(3, "source"))
    assert result.mapping == {"x": Target(3, "source")}
    assert result.items == {Target(3, "source")}
    assert seen == [2]


def test_partial_operations_are_sparse_and_path_aware() -> None:
    """Preserve presence, reject malformed nested patches, and omit incomplete reductions."""
    _, R = field_refs(Source, Target)

    class Mapping(Betwixt):
        left = Source
        right = Target
        reduction = reduce_rightward(right=R.number, rightward=lambda source: source.number)

    mapping = Mapping()
    assert mapping.rightward_partial({"number": 4}) == {"number": 4}
    assert mapping.rightward_partial({"number": None}) == {"number": None}
    with pytest.raises(PartialInputError, match="unknown source"):
        mapping.rightward_partial({"missing": 1})

    @dataclass
    class PatchSource:
        child: Source

    @dataclass
    class PatchTarget:
        child: Target

    source, target = field_refs(PatchSource, PatchTarget)

    class PatchMapping(Betwixt):
        left = PatchSource
        right = PatchTarget
        child = nested_rightward(left=source.child, right=target.child, via=mapping, rightward=lambda value: value)

    with pytest.raises(PartialInputError, match="child"):
        PatchMapping().rightward_partial({"child": {"unknown": 1}})
    with pytest.raises(TypeError):
        mapping.rightward_partial({"number": 1}, object())  # ty: ignore[too-many-positional-arguments]


def test_declaration_validation_registry_snapshot_and_explanations() -> None:
    """Validate anchors and signatures, resolve registry precedence, and expose diagnostic entries."""
    L, R = field_refs(Source, Target)
    registry = AdapterRegistry()
    base, exact = object(), object()
    registry.register(Source, base)
    assert registry.lookup(Source) is base
    registry.register(Source, exact, replace=True)
    assert registry.lookup(Source) is exact
    with pytest.raises(AdapterError):
        registry.register(Source, object())

    with pytest.raises(DeclarationError, match="equal canonical"):

        class Invalid(Betwixt):
            left = Source
            right = Target
            bad = disable_implicit_leftward(left=L.number, right=R.text)

    with pytest.raises(DeclarationError, match="final keyword-only"):

        class InvalidContext(Betwixt):
            left = Source
            right = Target
            bad = map_rightward(left=L.number, right=R.number, rightward=lambda value, ctx: value + ctx)

    class Mapping(Betwixt):
        left = Source
        right = Target
        number = map_rightward(left=L.number, right=R.number, rightward=lambda value: value)

    report = Mapping().explain_rightward()
    assert [entry.status for entry in report] == ["explicit", "implicit"]
    assert report.entries[0].annotation is int


def test_nested_mapping_wraps_inner_partial_errors() -> None:
    """Preserve the outer path when an inner nested partial operation rejects its input."""
    leaf_left, leaf_right = field_refs(Source, Target)

    class Leaf(Betwixt):
        left = Source
        right = Target
        number = map_rightward(left=leaf_left.number, right=leaf_right.number, rightward=lambda value: value)

    @dataclass
    class InnerSource:
        child: Source

    @dataclass
    class InnerTarget:
        child: Target

    inner_left, inner_right = field_refs(InnerSource, InnerTarget)

    class Inner(Betwixt):
        left = InnerSource
        right = InnerTarget
        child = nested_rightward(
            left=inner_left.child, right=inner_right.child, via=Leaf, rightward=lambda value: value
        )

    @dataclass
    class OuterSource:
        child: InnerSource

    @dataclass
    class OuterTarget:
        child: InnerTarget

    outer_left, outer_right = field_refs(OuterSource, OuterTarget)

    class Outer(Betwixt):
        left = OuterSource
        right = OuterTarget
        child = nested_rightward(
            left=outer_left.child, right=outer_right.child, via=Inner, rightward=lambda value: value
        )

    with pytest.raises(PartialInputError, match="child"):
        Outer().rightward_partial({"child": {"child": {"unknown": 1}}})


def test_subclass_compatibility_and_nested_callable_contract() -> None:
    """Accept source subclasses and execute both directional nested wrappers."""

    @dataclass(frozen=True)
    class Child(Source):
        pass

    @dataclass(frozen=True)
    class ChildTarget(Target):
        pass

    class Mapping(Betwixt):
        left = Child
        right = ChildTarget

    assert Mapping().rightward(Child(1)) == ChildTarget(1, "source")

    calls: list[str] = []

    class Inner(Betwixt):
        left = Source
        right = Target

    @dataclass
    class OuterSource:
        child: Source

    @dataclass
    class OuterTarget:
        child: Target

    source, target = field_refs(OuterSource, OuterTarget)

    class Outer(Betwixt):
        left = OuterSource
        right = OuterTarget
        child = nested_pairwise(
            left=source.child,
            right=target.child,
            via=Inner,
            rightward=lambda value, *, ctx: calls.append(f"r:{ctx}") or Target(value.number + 10, value.text),
            leftward=lambda value, *, ctx: calls.append(f"l:{ctx}") or Source(value.number - 10, value.text),
            context_rightward=lambda context: context,
            context_leftward=lambda context: context,
        )

    mapping = Outer()
    assert mapping.rightward(OuterSource(Source(2)), context="context").child == Target(12, "source")
    assert mapping.leftward(OuterTarget(Target(13)), context="context").child == Source(3, "target")
    assert calls == ["r:context", "l:context"]


def test_plain_and_nested_subclass_compatibility_works_in_both_directions() -> None:
    """Accept subclass source annotations when mapping to superclass destinations in either direction."""

    @dataclass(frozen=True)
    class LeftChild(Source):
        pass

    @dataclass(frozen=True)
    class RightChild(Target):
        pass

    class Plain(Betwixt):
        left = LeftChild
        right = Target

    class Reverse(Betwixt):
        left = Source
        right = RightChild

    assert Plain().rightward(LeftChild(1)) == Target(1, "source")
    assert Reverse().leftward(RightChild(2)) == Source(2, "target")

    @dataclass
    class NestedLeft:
        child: LeftChild

    @dataclass
    class NestedRight:
        child: Target

    nested_left, nested_right = field_refs(NestedLeft, NestedRight)

    class Nested(Betwixt):
        left = NestedLeft
        right = NestedRight
        child = nested_rightward(
            left=nested_left.child, right=nested_right.child, via=Reverse, rightward=lambda value: value
        )

    assert Nested().rightward(NestedLeft(LeftChild(3))).child == RightChild(3, "source")


def test_snapshot_is_immutable_after_declaration() -> None:
    """Prevent field metadata mutation from changing an already declared mapping."""

    class Mapping(Betwixt):
        left = Source
        right = Target

    mapping = Mapping()
    with pytest.raises(TypeError):
        mapping._field_snapshots[0]["new"] = int  # ty: ignore[invalid-assignment]
    assert mapping.rightward(Source(4)) == Target(4, "source")


def test_nested_partial_shapes_and_partial_explicit_seed() -> None:
    """Validate every outer container shape and retain seeds when producers are unavailable."""

    class Inner(Betwixt):
        left = Source
        right = Target

    @dataclass
    class SourceShapes:
        scalar: Source
        optional: Source | None
        values: list[Source]
        pair: tuple[Source, Source]
        mapping: dict[str, Source]
        items: set[Source]

    @dataclass
    class TargetShapes:
        scalar: Target
        optional: Target | None
        values: list[Target]
        pair: tuple[Target, Target]
        mapping: dict[str, Target]
        items: set[Target]

    source, target = field_refs(SourceShapes, TargetShapes)

    class Shapes(Betwixt):
        left = SourceShapes
        right = TargetShapes
        scalar = nested_rightward(left=source.scalar, right=target.scalar, via=Inner, rightward=lambda value: value)
        optional = nested_rightward(
            left=source.optional, right=target.optional, via=Inner, rightward=lambda value: value
        )
        values = nested_rightward(left=source.values, right=target.values, via=Inner, rightward=lambda value: value)
        pair = nested_rightward(left=source.pair, right=target.pair, via=Inner, rightward=lambda value: value)
        mapping = nested_rightward(left=source.mapping, right=target.mapping, via=Inner, rightward=lambda value: value)
        items = nested_rightward(left=source.items, right=target.items, via=Inner, rightward=lambda value: value)

    mapping = Shapes()
    assert mapping.rightward_partial({"values": []}) == {"values": []}
    assert mapping.rightward_partial({"pair": ({}, {})}) == {"pair": ({}, {})}
    assert mapping.rightward_partial({"mapping": {}}) == {"mapping": {}}
    assert mapping.rightward_partial({"items": set()}) == {"items": set()}
    with pytest.raises(PartialInputError, match="values: expected list"):
        mapping.rightward_partial({"values": {"value": 1}})
    with pytest.raises(PartialInputError, match="pair: expected tuple of length 2"):
        mapping.rightward_partial({"pair": ({},)})
    with pytest.raises(PartialInputError, match="mapping: expected dict"):
        mapping.rightward_partial({"mapping": []})
    with pytest.raises(PartialInputError, match="scalar: expected a mapping"):
        mapping.rightward_partial({"scalar": 1})
    with pytest.raises(PartialInputError, match="pair: expected tuple"):
        mapping.rightward_partial({"pair": []})
    with pytest.raises(PartialInputError, match="items: expected set"):
        mapping.rightward_partial({"items": []})

    L, R = field_refs(Source, Target)

    class PartialProducer(Betwixt):
        left = Source
        right = Target
        value = map_pairwise(
            left=(L.number, L.text),
            right=R.number,
            rightward=lambda value, text: value + len(text),
            leftward=lambda value: value,
        )

    assert PartialProducer().rightward_partial({"number": 7}) == {"number": 7}
    assert PartialProducer().rightward_partial({"number": 7, "text": "xx"}) == {"number": 9, "text": "xx"}


def test_global_suppression_and_unmapped_diagnostics_are_actionable() -> None:
    """Explain global omission and include the complete required-field failure context."""

    class Suppressed(Betwixt):
        left = Source
        right = Target
        disable_implicit_mapping = True

    report = Suppressed().explain_rightward()
    value = next(entry for entry in report if entry.destination == "number")
    assert value.status == "omitted"
    assert value.reason == "implicit mapping disabled globally"
    with pytest.raises(UnmappedFieldError) as error:
        Suppressed().rightward(Source(1))
    assert error.value.direction == "rightward"
    assert error.value.source_type is Source
    assert error.value.destination_type is Target
    assert error.value.source_field == "number"
    assert error.value.destination_field == "number"
    assert error.value.source_annotation is int
    assert error.value.destination_annotation is int
    assert error.value.omission_reason == "implicit mapping disabled globally"
    assert error.value.explanation == "explain_rightward()"
    assert error.value.remedies == (
        "add an explicit mapping",
        "remove implicit-mapping suppression",
    )
    message = str(error.value)
    assert all(
        part in message
        for part in ("rightward", "Source", "Target", "'number'", "annotation", "explain_rightward", "explicit mapping")
    )
