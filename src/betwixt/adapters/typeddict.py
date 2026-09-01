"""Standard-library and typing-extensions TypedDict adapter."""

from collections.abc import Mapping
from typing import Any, is_typeddict

from betwixt.annotations import resolved_fields
from betwixt.errors import AdapterError


def is_typed_dict(type_: type[Any]) -> bool:
    """Return whether `type_` is a TypedDict class on supported Python versions."""
    if is_typeddict(type_):
        return True
    return (
        isinstance(type_, type)
        and issubclass(type_, dict)
        and hasattr(type_, "__annotations__")
        and hasattr(type_, "__required_keys__")
        and hasattr(type_, "__optional_keys__")
        and hasattr(type_, "__total__")
    )


class TypedDictAdapter:
    """Adapt a TypedDict as a plain mapping boundary without runtime coercion."""

    def __init__(self, type_: type[Any]) -> None:
        if not is_typed_dict(type_):
            raise AdapterError(f"{type_.__name__} is not a TypedDict")
        self.type = type_
        self._fields = resolved_fields(type_)
        required = getattr(type_, "__required_keys__", frozenset())
        optional = getattr(type_, "__optional_keys__", frozenset())
        if not required and not optional:
            required = self._fields.keys() if getattr(type_, "__total__", True) else ()
        self._required = frozenset(required)

    def fields(self) -> dict[str, Any]:
        """Return canonical field annotations, including inherited fields."""
        return dict(self._fields)

    def read(self, value: Any, name: str) -> Any:
        """Read a canonical key from a TypedDict mapping."""
        if not isinstance(value, Mapping):
            raise AdapterError(f"cannot read {name!r} from a non-mapping {type(value).__name__}")
        try:
            return value[name]
        except (KeyError, TypeError) as error:
            raise AdapterError(f"cannot read TypedDict field {name!r}: {error}") from error

    def project(self, value: Any) -> Mapping[str, Any]:
        """Validate and copy a projected mapping through the TypedDict boundary."""
        if not isinstance(value, Mapping):
            raise AdapterError(f"projection returned {type(value).__name__}, expected a mapping")
        unknown = set(value) - set(self._fields)
        if unknown:
            raise AdapterError(f"projection returned unknown fields: {sorted(unknown)!r}")
        try:
            return {name: value[name] for name in self._fields}
        except (KeyError, TypeError) as error:
            raise AdapterError(f"projection returned an unreadable field: {error}") from error

    def construct(self, values: Mapping[str, Any]) -> dict[str, Any]:
        """Construct a plain dictionary from translated canonical values."""
        return dict(values)

    def required(self, name: str) -> bool:
        """Return whether native TypedDict construction requires `name`."""
        return name in self._required
