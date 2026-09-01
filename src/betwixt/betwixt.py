"""The public Betwixt declaration and translation engine."""

from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from inspect import isabstract
from types import MappingProxyType
from typing import Any, ClassVar, cast

from betwixt.adapters.registry import registry
from betwixt.annotations import compatible, nested_compatible
from betwixt.compiler import call, validate_callable, validate_derivation
from betwixt.constructs import Construct
from betwixt.errors import (
    DeclarationError,
    ExpansionError,
    MissingAdapterError,
    PartialInputError,
    UnmappedFieldError,
)
from betwixt.types import Adapter


class Betwixt(ABC):
    """
    Declare and execute a bidirectional mapping between two structured types.

    Concrete subclasses define `left` and `right`, then define `(L, R) = field_refs(left, right)` in the class body
    before using those proxies in mapping constructs.
    """

    left: ClassVar[type[Any]]
    right: ClassVar[type[Any]]
    disable_implicit_mapping: ClassVar[bool] = False
    _declarations: ClassVar[tuple[Construct, ...]]
    left_adapter: ClassVar[Adapter]
    right_adapter: ClassVar[Adapter]
    _field_snapshots: ClassVar[tuple[Mapping[str, Any], Mapping[str, Any]]]

    @property
    @abstractmethod
    def left(self) -> type[Any]: ...

    @property
    @abstractmethod
    def right(self) -> type[Any]: ...

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        if any(isinstance(base, type) and not isabstract(base) for base in cls.__bases__ if issubclass(base, Betwixt)):
            raise DeclarationError("cannot subclass a concrete Betwixt mapping")
        cls._validate_declaration()

    @classmethod
    def _validate_declaration(cls) -> None:
        if not isinstance(getattr(cls, "left", None), type) or not isinstance(getattr(cls, "right", None), type):
            raise DeclarationError("Betwixt declarations require left and right types")
        if not isinstance(cls.disable_implicit_mapping, bool):
            raise DeclarationError("disable_implicit_mapping must be a boolean")
        left_type, right_type = cast(type[Any], cls.left), cast(type[Any], cls.right)
        left_adapter, right_adapter = registry.lookup(left_type), registry.lookup(right_type)
        if left_adapter is None or right_adapter is None:
            missing = left_type if left_adapter is None else right_type
            raise MissingAdapterError(
                f"No adapter is available for {missing.__name__}; register an Adapter or install its extra"
            )
        cls.left_adapter = left_adapter
        cls.right_adapter = right_adapter
        cls._declarations = tuple(item for item in cls.__dict__.values() if isinstance(item, Construct))
        left_fields, right_fields = left_adapter.fields(), right_adapter.fields()
        cls._field_snapshots = (MappingProxyType(dict(left_fields)), MappingProxyType(dict(right_fields)))
        for declaration in cls._declarations:
            _validate_construct_shape(declaration)
            refs = _refs(declaration.left) + _refs(declaration.right)
            if any(ref.side not in ("left", "right") for ref in refs):
                raise DeclarationError("field reference has an invalid side")
            if any(
                ref.side == "left" and ref.owner is not left_type or ref.side == "right" and ref.owner is not right_type
                for ref in refs
            ):
                raise DeclarationError("field reference belongs to a different declared type")
            if any(
                ref.side == "left"
                and ref.name not in left_fields
                or ref.side == "right"
                and ref.name not in right_fields
                for ref in refs
            ):
                raise DeclarationError("declaration references a field absent from its declared type")
            if declaration.kind.startswith("disable_implicit"):
                if len(_refs(declaration.left)) != 1 or len(_refs(declaration.right)) != 1:
                    raise DeclarationError("implicit-disable declarations require one field on each side")
                if _name(declaration.left) != _name(declaration.right):
                    raise DeclarationError("implicit-disable anchors must have equal canonical names")
            for function in (declaration.rightward, declaration.leftward):
                if function is not None:
                    validate_callable(function)
            if declaration.kind.startswith("nested"):
                validate_derivation(declaration.context_rightward)
                validate_derivation(declaration.context_leftward)
                if declaration.via is None:
                    raise DeclarationError("nested declarations require via")
                inner = (
                    declaration.via()
                    if isinstance(declaration.via, type) and issubclass(declaration.via, Betwixt)
                    else declaration.via
                )
                if not isinstance(inner, Betwixt):
                    raise DeclarationError("nested via must be a Betwixt mapping")
                outer_left = left_fields.get(_name(declaration.left))
                outer_right = right_fields.get(_name(declaration.right))
                if not nested_compatible(outer_left, outer_right, inner.left, inner.right):
                    raise DeclarationError(
                        f"nested field {_name(declaration.left)!r} does not match the inner Betwixt mapping"
                    )

    def _run(
        self, value: Any, *, direction: str, context: Any, partial: bool
    ) -> Any:
        source_adapter = self.left_adapter if direction == "rightward" else self.right_adapter
        destination_adapter = self.right_adapter if direction == "rightward" else self.left_adapter
        source_fields, destination_fields = (
            self._field_snapshots if direction == "rightward" else self._field_snapshots[::-1]
        )
        if partial:
            if not isinstance(value, Mapping):
                raise PartialInputError("partial operations accept mappings only")
            source = dict(value)
            unknown = set(source) - set(source_fields)
            if unknown:
                raise PartialInputError(f"unknown source fields: {sorted(unknown)!r}")
        else:
            source = value
        result: dict[str, Any] = {}
        explicit_names = {
            destination
            for declaration in self._declarations
            if (item := self._producer(declaration, direction)) and item[3].startswith(("map", "nested", "expand"))
            for destination in _destinations(item[0])
        }
        disabled = {
            _name(declaration.left if direction == "rightward" else declaration.right)
            for declaration in self._declarations
            if declaration.kind in ("disable_implicit_pairwise", f"disable_implicit_{direction}")
        }
        if not self.disable_implicit_mapping:
            for name, annotation in source_fields.items():
                present = name in source if partial else True
                if (
                    name in destination_fields
                    and (partial or name not in explicit_names)
                    and name not in disabled
                    and present
                    and compatible(annotation, destination_fields[name])
                ):
                    result[name] = source[name] if partial else source_adapter.read(source, name)
        for declaration in self._declarations:
            producer = self._producer(declaration, direction)
            if producer is None:
                continue
            destination, names, function, kind = producer
            if kind.startswith("project"):
                if partial:
                    continue
                projected = call(function, (source,), context)
                result.update(destination_adapter.project(projected))
                continue
            if kind.startswith("expand"):
                if not all(name in source if partial else True for name in names):
                    continue
                source_value = source[names[0]] if partial else source_adapter.read(source, names[0])
                expanded = call(function, (source_value,), context)
                if not isinstance(expanded, tuple) or len(expanded) != len(destination):
                    actual = len(expanded) if isinstance(expanded, tuple) else type(expanded).__name__
                    raise ExpansionError(
                        f"{kind} callable must return a tuple with exactly {len(destination)} values; received {actual}"
                    )
                result.update(zip(destination, expanded, strict=True))
                continue
            destination = cast(str, destination)
            if kind.startswith("reduce"):
                if partial and not set(source_fields).issubset(source):
                    continue
                args = (source if not partial else source_adapter.construct(source),)
            else:
                if not all(name in source if partial else True for name in names):
                    continue
                args = (
                    tuple(source[name] for name in names)
                    if partial
                    else tuple(source_adapter.read(source, name) for name in names)
                )
            if kind.startswith("nested"):
                inner = (
                    declaration.via()
                    if isinstance(declaration.via, type) and issubclass(declaration.via, Betwixt)
                    else declaration.via
                )
                derive = declaration.context_rightward if direction == "rightward" else declaration.context_leftward
                derived = None if derive is None else derive(context)
                try:
                    nested_result = _nested(
                        inner,
                        args[0],
                        direction,
                        derived,
                        partial,
                        destination,
                        source_fields.get(names[0]),
                    )
                    # The declaration callable is a directional wrapper around
                    # the inner operation.  It is deliberately invoked after
                    # recursive translation so `via` remains the source of the
                    # inner mapping semantics while callers can transform or
                    # observe its result.
                    result[destination] = call(function, (nested_result,), derived)
                except PartialInputError as error:
                    raise PartialInputError(f"{destination}: {error}") from error
            else:
                result[destination] = call(function, args, context)
        if partial:
            return result
        explanation = self._explain(direction)
        for name in destination_fields:
            if name not in result and destination_adapter.required(name):
                entry = next(item for item in explanation.entries if item.destination == name)
                source_detail = (
                    f"source field {entry.source!r} ({entry.source_annotation!r})"
                    if entry.source
                    else "no same-name source field"
                )
                reason = entry.reason or "no producer is declared"
                raise UnmappedFieldError(
                    f"{direction} cannot map required field {name!r} from "
                    f"{source_type_name(source_adapter)} to {destination_type_name(destination_adapter)}; "
                    f"destination annotation {entry.annotation!r}; {source_detail}; "
                    f"reason: {reason}. See explain_{direction}(); add an explicit mapping, "
                    "add an explicit mapping, or remove the implicit-mapping suppression.",
                    direction=direction,
                    source_type=self.left if direction == "rightward" else self.right,
                    destination_type=self.right if direction == "rightward" else self.left,
                    source_field=entry.source,
                    destination_field=entry.destination,
                    source_annotation=entry.source_annotation,
                    destination_annotation=entry.annotation,
                    omission_reason=entry.reason,
                    explanation=f"explain_{direction}()",
                    remedies=("add an explicit mapping", "remove implicit-mapping suppression"),
                )
        return destination_adapter.construct(result)

    def _producer(
        self, declaration: Construct, direction: str
    ) -> tuple[str | tuple[str, ...], tuple[str, ...], Any, str] | None:
        if direction == "rightward":
            if declaration.kind in ("map_pairwise", "map_rightward"):
                return (
                    _name(declaration.right),
                    tuple(_name(ref) for ref in _refs(declaration.left)),
                    declaration.rightward,
                    declaration.kind,
                )
            if declaration.kind == "reduce_rightward":
                return _name(declaration.right), (), declaration.rightward, declaration.kind
            if declaration.kind == "project_rightward":
                return "*", (), declaration.rightward, declaration.kind
            if declaration.kind == "expand_rightward":
                return (
                    tuple(_name(ref) for ref in _refs(declaration.right)),
                    (_name(declaration.left),),
                    declaration.rightward,
                    declaration.kind,
                )
            if declaration.kind in ("nested_pairwise", "nested_rightward"):
                return _name(declaration.right), (_name(declaration.left),), declaration.rightward, declaration.kind
        else:
            if declaration.kind in ("map_pairwise", "map_leftward"):
                return (
                    _name(_refs(declaration.left)[0]),
                    tuple(_name(ref) for ref in _refs(declaration.right)),
                    declaration.leftward,
                    declaration.kind,
                )
            if declaration.kind == "reduce_leftward":
                return _name(declaration.left), (), declaration.leftward, declaration.kind
            if declaration.kind == "project_leftward":
                return "*", (), declaration.leftward, declaration.kind
            if declaration.kind == "expand_leftward":
                return (
                    tuple(_name(ref) for ref in _refs(declaration.left)),
                    (_name(declaration.right),),
                    declaration.leftward,
                    declaration.kind,
                )
            if declaration.kind in ("nested_pairwise", "nested_leftward"):
                return _name(declaration.left), (_name(declaration.right),), declaration.leftward, declaration.kind
        return None

    def rightward(self, value: Any, *, context: Any = None) -> Any:
        """Translate a left instance into a right instance."""
        return self._run(value, direction="rightward", context=context, partial=False)

    def leftward(self, value: Any, *, context: Any = None) -> Any:
        """Translate a right instance into a left instance."""
        return self._run(value, direction="leftward", context=context, partial=False)

    def rightward_partial(self, value: Mapping[str, Any], *, context: Any = None) -> dict[str, Any]:
        """Translate a sparse left patch into a sparse right patch."""
        return self._run(value, direction="rightward", context=context, partial=True)

    def leftward_partial(self, value: Mapping[str, Any], *, context: Any = None) -> dict[str, Any]:
        """Translate a sparse right patch into a sparse left patch."""
        return self._run(value, direction="leftward", context=context, partial=True)

    def explain_rightward(self) -> "MappingExplanation":
        """Return a declaration-only rightward explanation."""
        return self._explain("rightward")

    def explain_leftward(self) -> "MappingExplanation":
        """Return a declaration-only leftward explanation."""
        return self._explain("leftward")

    def _explain(self, direction: str) -> "MappingExplanation":
        source_type, destination_type = (self.left, self.right) if direction == "rightward" else (self.right, self.left)
        source_fields, destination_fields = (
            self._field_snapshots if direction == "rightward" else self._field_snapshots[::-1]
        )
        report = MappingExplanation(direction, source_type, destination_type)
        disabled = {
            _name(declaration.left if direction == "rightward" else declaration.right)
            for declaration in self._declarations
            if declaration.kind in ("disable_implicit_pairwise", f"disable_implicit_{direction}")
        }
        for name, annotation in destination_fields.items():
            producer = next(
                (
                    candidate
                    for declaration in self._declarations[::-1]
                    if (candidate := self._producer(declaration, direction))
                    and (name in _destinations(candidate[0]) or candidate[3].startswith("project"))
                ),
                None,
            )
            if producer:
                report.entries.append(
                    MappingEntry(
                        name,
                        "explicit",
                        producer[1][0] if producer[1] else None,
                        annotation=annotation,
                        source_annotation=source_fields.get(producer[1][0]) if producer[1] else None,
                    )
                )
            elif name in disabled:
                report.entries.append(
                    MappingEntry(
                        name,
                        "omitted",
                        name,
                        "implicit mapping disabled",
                        annotation=annotation,
                        source_annotation=source_fields.get(name),
                    )
                )
            elif self.disable_implicit_mapping and name in source_fields:
                report.entries.append(
                    MappingEntry(
                        name,
                        "omitted",
                        name,
                        "implicit mapping disabled globally",
                        annotation=annotation,
                        source_annotation=source_fields[name],
                    )
                )
            elif name in source_fields and compatible(source_fields[name], annotation):
                report.entries.append(
                    MappingEntry(name, "implicit", name, annotation=annotation, source_annotation=source_fields[name])
                )
            elif name in source_fields:
                report.entries.append(
                    MappingEntry(
                        name,
                        "omitted",
                        name,
                        "incompatible annotations",
                        annotation=annotation,
                        source_annotation=source_fields[name],
                    )
                )
            else:
                report.entries.append(MappingEntry(name, "unmapped", annotation=annotation))
        return report


def _refs(ref: Any) -> tuple[Any, ...]:
    refs = () if ref is None else ref if isinstance(ref, tuple) else (ref,)
    if any(not hasattr(item, "side") or not hasattr(item, "name") for item in refs):
        raise DeclarationError("declarations require FieldRef values")
    return refs


def _validate_construct_shape(declaration: Construct) -> None:
    """Reject malformed low-level construct records before any mapping runs."""
    kind = declaration.kind
    if kind in {"map_pairwise", "map_rightward", "map_leftward"}:
        sources = declaration.left if kind != "map_leftward" else declaration.right
        if not _refs(sources):
            raise DeclarationError(f"{kind} requires at least one source field")
    if kind in {"expand_rightward", "expand_leftward"}:
        sources = declaration.left if kind == "expand_rightward" else declaration.right
        destinations = declaration.right if kind == "expand_rightward" else declaration.left
        if len(_refs(sources)) != 1:
            raise DeclarationError(f"{kind} requires exactly one source field")
        if len(_refs(destinations)) < 2:
            raise DeclarationError(f"{kind} requires at least two destination fields")
    required_callables = {
        "map_pairwise": declaration.rightward and declaration.leftward,
        "map_rightward": declaration.rightward,
        "map_leftward": declaration.leftward,
        "expand_rightward": declaration.rightward,
        "expand_leftward": declaration.leftward,
        "reduce_rightward": declaration.rightward,
        "reduce_leftward": declaration.leftward,
        "project_rightward": declaration.rightward,
        "project_leftward": declaration.leftward,
    }
    if kind in required_callables and not required_callables[kind]:
        raise DeclarationError(f"{kind} requires its directional callable(s)")


def _name(ref: Any) -> str:
    if ref is None:
        raise DeclarationError("a declaration is missing a field reference")
    return ref.name


def _destinations(value: str | tuple[str, ...]) -> tuple[str, ...]:
    """Normalize a producer destination to declaration order."""
    return value if isinstance(value, tuple) else (value,)


def _nested(
    inner: "Betwixt", value: Any, direction: str, context: Any, partial: bool, path: str = "value", shape: Any = None
) -> Any:
    """Traverse a nested value using the declaration's retained outer shape."""
    from typing import Union, get_args, get_origin

    origin = get_origin(shape)
    args = get_args(shape)
    if origin in (Union, __import__("types").UnionType):
        nonnull = [item for item in args if item is not type(None)]
        if value is None:
            if len(nonnull) == len(args):
                raise PartialInputError(f"{path}: null is not allowed")
            return None
        shape = nonnull[0] if len(nonnull) == 1 else shape
        origin = get_origin(shape)
        args = get_args(shape)
    if value is None:
        raise PartialInputError(f"{path}: null is not allowed")
    if origin is list:
        if not isinstance(value, list):
            raise PartialInputError(f"{path}: expected list")
        return [
            _nested(inner, item, direction, context, partial, f"{path}[{index}]", args[0])
            for index, item in enumerate(value)
        ]
    if origin is tuple:
        if not isinstance(value, tuple):
            raise PartialInputError(f"{path}: expected tuple")
        element_shapes = args[:-1] if len(args) == 2 and args[1] is Ellipsis else args
        if len(args) > 1 and args[-1] is not Ellipsis and len(value) != len(element_shapes):
            raise PartialInputError(f"{path}: expected tuple of length {len(element_shapes)}")
        element_shape = element_shapes[0] if len(args) == 2 and args[1] is Ellipsis else None
        return tuple(
            _nested(
                inner, item, direction, context, partial, f"{path}[{index}]", element_shape or element_shapes[index]
            )
            for index, item in enumerate(value)
        )
    if origin is dict:
        if not isinstance(value, dict):
            raise PartialInputError(f"{path}: expected dict")
        return {
            key: _nested(inner, item, direction, context, partial, f"{path}[{key!r}]", args[1])
            for key, item in value.items()
        }
    if origin is set:
        if not isinstance(value, set):
            raise PartialInputError(f"{path}: expected set")
        return {
            _nested(inner, item, direction, context, partial, f"{path}[{index}]", args[0])
            for index, item in enumerate(value)
        }
    if partial and not isinstance(value, Mapping):
        raise PartialInputError(f"{path}: expected a mapping")
    operation = (
        inner.rightward_partial
        if direction == "rightward" and partial
        else inner.leftward_partial
        if partial
        else inner.rightward
        if direction == "rightward"
        else inner.leftward
    )
    try:
        return operation(value, context=context)
    except PartialInputError as error:
        raise PartialInputError(f"{path}: {error}") from error


def destination_type_name(adapter: Any) -> str:
    """Return the stable destination type label used in diagnostics."""
    return adapter.type.__name__


def source_type_name(adapter: Any) -> str:
    """Return the stable source type label used in diagnostics."""
    return adapter.type.__name__


@dataclass(frozen=True)
class MappingEntry:
    """Describe one destination field in a mapping report."""

    destination: str
    status: str
    source: str | None = None
    reason: str | None = None
    annotation: Any = None
    source_annotation: Any = None


class MappingExplanation:
    """Describe a mapping without reading or constructing values."""

    def __init__(self, direction: str, source: type[Any], destination: type[Any]) -> None:
        self.direction, self.source_type, self.destination_type = direction, source, destination
        self.entries: list[MappingEntry] = []

    def __iter__(self):
        """Iterate over report entries."""
        return iter(self.entries)
