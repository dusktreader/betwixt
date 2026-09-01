"""Declarative construct factories."""

from dataclasses import dataclass
from typing import Any

from betwixt.refs import FieldRef


@dataclass(frozen=True)
class Construct:
    """Represent one declarative mapping construct."""

    kind: str
    left: FieldRef | tuple[FieldRef, ...] | None = None
    right: FieldRef | tuple[FieldRef, ...] | None = None
    rightward: Any = None
    leftward: Any = None
    via: Any = None
    context_rightward: Any = None
    context_leftward: Any = None


def map_pairwise(*, left: FieldRef | tuple[FieldRef, ...], right: FieldRef, rightward: Any, leftward: Any) -> Construct:
    """Map referenced fields with independent callables in both directions."""
    return Construct(map_pairwise.__name__, left=left, right=right, rightward=rightward, leftward=leftward)


def map_rightward(*, left: FieldRef | tuple[FieldRef, ...], right: FieldRef, rightward: Any) -> Construct:
    """Map referenced left fields to one right field."""
    return Construct(map_rightward.__name__, left=left, right=right, rightward=rightward)


def map_leftward(*, right: FieldRef | tuple[FieldRef, ...], left: FieldRef, leftward: Any) -> Construct:
    """Map referenced right fields to one left field."""
    return Construct(map_leftward.__name__, left=left, right=right, leftward=leftward)


def expand_rightward(*, left: FieldRef, right: tuple[FieldRef, ...], rightward: Any) -> Construct:
    """Expand one left-side source value into multiple right-side fields."""
    return Construct(expand_rightward.__name__, left=left, right=right, rightward=rightward)


def expand_leftward(*, right: FieldRef, left: tuple[FieldRef, ...], leftward: Any) -> Construct:
    """Expand one right-side source value into multiple left-side fields."""
    return Construct(expand_leftward.__name__, left=left, right=right, leftward=leftward)


def reduce_rightward(*, right: FieldRef, rightward: Any) -> Construct:
    """Reduce a complete left object to one right field."""
    return Construct(reduce_rightward.__name__, right=right, rightward=rightward)


def reduce_leftward(*, left: FieldRef, leftward: Any) -> Construct:
    """Reduce a complete right object to one left field."""
    return Construct(reduce_leftward.__name__, left=left, leftward=leftward)


def project_rightward(*, rightward: Any) -> Construct:
    """Project a complete left object into a right object."""
    return Construct(project_rightward.__name__, rightward=rightward)


def project_leftward(*, leftward: Any) -> Construct:
    """Project a complete right object into a left object."""
    return Construct(project_leftward.__name__, leftward=leftward)


def nested_pairwise(
    *,
    left: FieldRef,
    right: FieldRef,
    via: Any,
    rightward: Any,
    leftward: Any,
    context_rightward: Any = None,
    context_leftward: Any = None,
) -> Construct:
    """Map one nested value in both directions through another Betwixt declaration."""
    return Construct(
        nested_pairwise.__name__,
        left=left,
        right=right,
        via=via,
        rightward=rightward,
        leftward=leftward,
        context_rightward=context_rightward,
        context_leftward=context_leftward,
    )


def nested_rightward(
    *, left: FieldRef, right: FieldRef, via: Any, rightward: Any, context_rightward: Any = None
) -> Construct:
    """Map one nested value from left to right through another Betwixt declaration."""
    return Construct(
        nested_rightward.__name__,
        left=left,
        right=right,
        via=via,
        rightward=rightward,
        context_rightward=context_rightward,
    )


def nested_leftward(
    *, right: FieldRef, left: FieldRef, via: Any, leftward: Any, context_leftward: Any = None
) -> Construct:
    """Map one nested value from right to left through another Betwixt declaration."""
    return Construct(
        nested_leftward.__name__, left=left, right=right, via=via, leftward=leftward, context_leftward=context_leftward
    )


def disable_implicit_pairwise(*, left: FieldRef, right: FieldRef) -> Construct:
    """Disable implicit mapping for a field pair in both directions."""
    return Construct(disable_implicit_pairwise.__name__, left=left, right=right)


def disable_implicit_rightward(*, left: FieldRef, right: FieldRef) -> Construct:
    """Disable implicit mapping from a left field to a right field."""
    return Construct(disable_implicit_rightward.__name__, left=left, right=right)


def disable_implicit_leftward(*, left: FieldRef, right: FieldRef) -> Construct:
    """Disable implicit mapping from a right field to a left field."""
    return Construct(disable_implicit_leftward.__name__, left=left, right=right)
