"""Focused tests for the public mapping contract."""

from dataclasses import dataclass
from inspect import signature

import pytest

from betwixt import (
    Betwixt,
    DeclarationError,
    ExpansionError,
    PartialInputError,
    UnmappedFieldError,
    expand_leftward,
    expand_rightward,
    field_refs,
    map_pairwise,
    map_rightward,
    nested_rightward,
)


@dataclass
class Left:
    """Provide a source fixture."""

    value: int
    label: str = "left"


@dataclass
class Right:
    """Provide a destination fixture."""

    value: int
    label: str = "right"


def make_mapping() -> Betwixt:
    """Create a representative mapping."""
    left_refs, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        value_map = map_rightward(left=left_refs.value, right=right_refs.value, rightward=lambda value: value + 1)

    return Mapping()


def test_implicit_mapping_and_directional_explicit_write() -> None:
    """Map compatible implicit fields and allow explicit overrides."""
    mapping = make_mapping()
    assert mapping.rightward(Left(1)) == Right(2, "left")


def test_pairwise_callable_receives_reference_order() -> None:
    """Pass multiple source references in declaration order."""
    left_refs, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        value_map = map_pairwise(
            left=(left_refs.value, left_refs.label),
            right=right_refs.value,
            rightward=lambda value, label: value + len(label),
            leftward=lambda value: value - 1,
        )

    assert Mapping().rightward(Left(2, "abc")).value == 5


def test_partial_preserves_presence_and_native_defaults_apply_only_to_full_models() -> None:
    """Return only supplied values while native destination construction supplies model defaults."""
    class Mapping(Betwixt):
        left = Left
        right = Right

    mapping = Mapping()
    assert mapping.rightward_partial({"value": 3}) == {"value": 3}
    assert mapping.rightward_partial({"value": None}) == {"value": None}
    assert mapping.rightward(Left(3)).label == "left"
    with pytest.raises(PartialInputError):
        mapping.rightward_partial({"unknown": 1})


def test_full_operation_signatures_have_no_mapping_defaults_parameter() -> None:
    """Reject the removed operation-level defaults parameter while retaining context."""
    assert list(signature(Betwixt.rightward).parameters) == ["self", "value", "context"]
    assert list(signature(Betwixt.leftward).parameters) == ["self", "value", "context"]


def test_context_is_keyword_only_and_injected_by_name() -> None:
    """Inject context only into a final keyword-only parameter."""
    left_refs, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        value_map = map_rightward(
            left=left_refs.value, right=right_refs.value, rightward=lambda value, *, ctx: value + ctx
        )

    assert Mapping().rightward(Left(1), context=4).value == 5


def test_positional_context_parameter_is_rejected() -> None:
    """Reject context parameters that are not keyword-only."""
    left_refs, right_refs = field_refs(Left, Right)

    with pytest.raises(DeclarationError, match="final keyword-only"):

        class Invalid(Betwixt):
            left = Left
            right = Right
            value_map = map_rightward(
                left=left_refs.value, right=right_refs.value, rightward=lambda value, ctx: value + ctx
            )


def test_nested_translation_derives_context_once() -> None:
    """Reuse one derived context for every nested value."""
    calls: list[int] = []
    inner = make_mapping()

    @dataclass
    class BoxLeft:
        values: list[Left]

    @dataclass
    class BoxRight:
        values: list[Right]

    box_left, box_right = field_refs(BoxLeft, BoxRight)

    class Mapping(Betwixt):
        left = BoxLeft
        right = BoxRight
        values = nested_rightward(
            left=box_left.values,
            right=box_right.values,
            via=inner,
            rightward=lambda value: value,
            context_rightward=lambda context: calls.append(1) or context,
        )

    assert len(Mapping().rightward(BoxLeft([Left(1), Left(2)]), context=object()).values) == 2
    assert len(calls) == 1


def test_reduce_projection_and_explanation() -> None:
    """Execute whole-object producers and declaration reports."""
    from betwixt import project_rightward, reduce_rightward

    _, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        total = reduce_rightward(right=right_refs.value, rightward=lambda source: source.value * 2)
        projected = project_rightward(rightward=lambda source: Right(source.value + 5, source.label))

    mapping = Mapping()
    assert mapping.rightward(Left(2, "x")) == Right(7, "x")
    assert mapping.rightward_partial({"value": 2}) == {"value": 2}
    assert [entry.status for entry in mapping.explain_rightward().entries] == ["explicit", "explicit"]


def test_implicit_disable_is_directional() -> None:
    """Suppress one implicit direction without suppressing explicit declarations."""
    from betwixt import disable_implicit_rightward

    left_refs, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        disabled = disable_implicit_rightward(left=left_refs.label, right=right_refs.label)

    assert Mapping().rightward(Left(1, "x")).label == "right"
    assert Mapping().leftward(Right(1, "x")).label == "x"


def test_expansion_maps_one_value_to_multiple_fields_in_both_operations() -> None:
    """Write expansion results in destination declaration order for full and partial operations."""

    @dataclass
    class Split:
        first: str
        last: str

    @dataclass
    class Display:
        first: str
        last: str

    left_refs, right_refs = field_refs(Split, Display)

    class Mapping(Betwixt):
        left = Split
        right = Display
        display = expand_rightward(
            left=left_refs.first,
            right=(right_refs.first, right_refs.last),
            rightward=lambda value: tuple(value.split(" ", 1)),
        )
        reverse = expand_leftward(
            right=right_refs.first,
            left=(left_refs.first, left_refs.last),
            leftward=lambda value: tuple(value.split(" ", 1)),
        )

    mapping = Mapping()
    assert mapping.rightward(Split("Ada Lovelace", "ignored")) == Display("Ada", "Lovelace")
    assert mapping.rightward_partial({"first": "Ada Lovelace"}) == {"first": "Ada", "last": "Lovelace"}
    assert mapping.rightward_partial({"last": "ignored"}) == {"last": "ignored"}
    assert mapping.leftward(Display("Ada Lovelace", "unused")) == Split("Ada", "Lovelace")
    assert mapping.leftward_partial({"first": "Ada Lovelace"}) == {"first": "Ada", "last": "Lovelace"}


def test_expansion_is_directional_and_has_actionable_shape_errors() -> None:
    """Reject invalid expansion results and do not synthesize an inverse operation."""
    left_refs, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        expanded = expand_rightward(
            left=left_refs.value, right=(right_refs.value, right_refs.label), rightward=lambda value: (value, "ok")
        )

    mapping = Mapping()
    assert mapping.rightward(Left(3)) == Right(3, "ok")

    class RightOnly(Betwixt):
        left = Left
        right = Right
        disable_implicit_mapping = True
        expanded = expand_rightward(
            left=left_refs.value, right=(right_refs.value, right_refs.label), rightward=lambda value: (value, "ok")
        )

    with pytest.raises(UnmappedFieldError):
        RightOnly().leftward(Right(3, "ok"))

    class WrongType(Betwixt):
        left = Left
        right = Right
        expanded = expand_rightward(
            left=left_refs.value, right=(right_refs.value, right_refs.label), rightward=lambda value: value
        )

    with pytest.raises(ExpansionError, match="exactly 2.*int"):
        WrongType().rightward(Left(3))

    class WrongLength(Betwixt):
        left = Left
        right = Right
        expanded = expand_rightward(
            left=left_refs.value, right=(right_refs.value, right_refs.label), rightward=lambda value: (value,)
        )

    with pytest.raises(ExpansionError, match="exactly 2.*1"):
        WrongLength().rightward(Left(3))


def test_expansion_overlap_uses_declaration_order_and_destination_order() -> None:
    """Let a later expansion replace overlapping fields while preserving tuple destination order."""
    left_refs, right_refs = field_refs(Left, Right)

    class Mapping(Betwixt):
        left = Left
        right = Right
        first = expand_rightward(
            left=left_refs.value,
            right=(right_refs.label, right_refs.value),
            rightward=lambda value: ("first", value),
        )
        second = expand_rightward(
            left=left_refs.value,
            right=(right_refs.value, right_refs.label),
            rightward=lambda value: (value + 1, "second"),
        )

    assert Mapping().rightward(Left(3)) == Right(4, "second")


def test_expansion_declarations_validate_source_destination_and_callable() -> None:
    """Validate expansion arity and directional callable requirements during class declaration."""
    left_refs, right_refs = field_refs(Left, Right)
    with pytest.raises(DeclarationError, match="exactly one source"):

        class MultipleSources(Betwixt):
            left = Left
            right = Right
            expanded = expand_rightward(
                left=(left_refs.value, left_refs.label),  # ty: ignore[invalid-argument-type]
                right=(right_refs.value, right_refs.label),
                rightward=lambda value: (value, value),
            )

    with pytest.raises(DeclarationError, match="at least two destination"):

        class OneDestination(Betwixt):
            left = Left
            right = Right
            expanded = expand_rightward(
                left=left_refs.value, right=(right_refs.value,), rightward=lambda value: (value,)
            )

    with pytest.raises(DeclarationError, match="directional callable"):

        class MissingCallable(Betwixt):
            left = Left
            right = Right
            expanded = expand_rightward(
                left=left_refs.value, right=(right_refs.value, right_refs.label), rightward=None
            )
