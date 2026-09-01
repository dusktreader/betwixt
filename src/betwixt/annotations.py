"""Annotation normalization and compatibility helpers."""

import sys
import types
from collections.abc import Mapping
from typing import Annotated, Any, ForwardRef, Union, get_args, get_origin, get_type_hints


def normalize(annotation: Any, owner: type[Any] | None = None) -> Any:
    """Resolve an annotation, remove `Annotated`, and retain unresolved references."""
    if isinstance(annotation, str):
        annotation = ForwardRef(annotation)

    if isinstance(annotation, ForwardRef) and owner is not None:
        module = sys.modules.get(owner.__module__)
        try:
            annotation = eval(annotation.__forward_arg__, vars(module) if module else {}, vars(owner))
        except (NameError, SyntaxError, TypeError, AttributeError):
            return annotation

    if get_origin(annotation) is Annotated:
        return normalize(get_args(annotation)[0], owner)

    return annotation


def resolved_fields(type_: type[Any]) -> dict[str, Any]:
    """Return a class's annotations with forward references and metadata resolved."""
    try:
        return {name: normalize(value, type_) for (name, value) in get_type_hints(type_, include_extras=True).items()}
    except (NameError, TypeError, SyntaxError):
        return {name: normalize(value, type_) for (name, value) in getattr(type_, "__annotations__", {}).items()}


def compatible(source: Any, destination: Any) -> bool:
    """Return whether two annotations satisfy the implicit mapping rule."""
    source, destination = normalize(source), normalize(destination)

    if isinstance(source, ForwardRef) or isinstance(destination, ForwardRef):
        return False
    if source is Any or destination is Any:
        return True
    if source == destination:
        return True

    source_origin, destination_origin = get_origin(source), get_origin(destination)

    # Plain classes have no origin.  Check the subclass relationship before
    # entering generic compatibility; otherwise two ordinary classes are
    # incorrectly treated as an unsupported generic pair.
    if source_origin is None and destination_origin is None:
        try:
            return isinstance(source, type) and isinstance(destination, type) and issubclass(source, destination)
        except TypeError:
            return False

    source_union = source_origin in (Union, types.UnionType)
    destination_union = destination_origin in (Union, types.UnionType)

    if source_union or destination_union:
        source_args = get_args(source) if source_union else (source,)
        destination_args = get_args(destination) if destination_union else (destination,)
        return all(
            any(s is type(None) and d is type(None) or compatible(s, d) for d in destination_args) for s in source_args
        )

    if source_origin != destination_origin:
        try:
            return isinstance(source, type) and isinstance(destination, type) and issubclass(source, destination)
        except TypeError:
            return False

    source_args, destination_args = get_args(source), get_args(destination)

    if source_origin is tuple:
        source_variadic = len(source_args) == 2 and source_args[1] is Ellipsis
        destination_variadic = len(destination_args) == 2 and destination_args[1] is Ellipsis
        if source_variadic != destination_variadic:
            return False
        if source_variadic:
            return compatible(source_args[0], destination_args[0])
        return len(source_args) == len(destination_args) and all(
            compatible(s, d) for s, d in zip(source_args, destination_args)
        )

    if source_origin not in (list, set, dict, Mapping, tuple):
        return False

    return len(source_args) == len(destination_args) and all(
        compatible(s, d) for s, d in zip(source_args, destination_args)
    )


def nested_compatible(source: Any, destination: Any, inner_source: Any, inner_destination: Any) -> bool:
    """Validate an outer field shape against an inner mapping's two scalar types."""
    source, destination = (normalize(source), normalize(destination))
    source_args, destination_args = (get_args(source), get_args(destination))
    source_origin, destination_origin = (get_origin(source), get_origin(destination))
    source_is_union = source_origin in (Union, types.UnionType)
    destination_is_union = destination_origin in (Union, types.UnionType)

    if source_is_union or destination_is_union:
        if source_is_union and not destination_is_union:
            return False

        source_nonnull = [item for item in source_args if item is not type(None)]
        if not source_is_union:
            source_nonnull = [source]

        destination_nonnull = [item for item in destination_args if item is not type(None)]

        if len(source_nonnull) != 1 or len(destination_nonnull) != 1:
            return False

        return nested_compatible(source_nonnull[0], destination_nonnull[0], inner_source, inner_destination)

    if source is Any or destination is Any:
        return False

    if isinstance(source, ForwardRef) or isinstance(destination, ForwardRef):
        return False

    if source_origin is None or destination_origin is None:
        return compatible(source, inner_source) and compatible(inner_destination, destination)

    if source_origin != destination_origin:
        return False

    if source_origin is tuple and destination_origin is tuple:
        source_variadic = len(source_args) == 2 and source_args[1] is Ellipsis
        destination_variadic = len(destination_args) == 2 and destination_args[1] is Ellipsis

        if source_variadic and destination_variadic:
            return nested_compatible(source_args[0], destination_args[0], inner_source, inner_destination)

        # Fixed and variadic tuples are distinct shapes.  In particular, a
        # variadic source cannot satisfy a destination with a fixed arity (or
        # vice versa), even when every currently declared element matches.
        if source_variadic or destination_variadic:
            return False

        if len(source_args) != len(destination_args):
            return False

        return all(
            nested_compatible(s, d, inner_source, inner_destination) for (s, d) in zip(source_args, destination_args)
        )

    if source_origin in (list, set):
        return (
            len(source_args) == 1
            and len(destination_args) == 1
            and nested_compatible(source_args[0], destination_args[0], inner_source, inner_destination)
        )

    if source_origin in (dict, Mapping):
        return (
            len(source_args) == 2
            and len(destination_args) == 2
            and compatible(source_args[0], destination_args[0])
            and nested_compatible(source_args[1], destination_args[1], inner_source, inner_destination)
        )

    return False
