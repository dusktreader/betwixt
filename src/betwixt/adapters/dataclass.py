"""Standard-library dataclass adapter."""

from collections.abc import Mapping
from dataclasses import MISSING, fields, is_dataclass
from typing import Any

from betwixt.annotations import resolved_fields
from betwixt.errors import AdapterError


class DataclassAdapter:
    """Adapt a standard-library dataclass without adding coercion."""

    def __init__(self, type_: type[Any]) -> None:
        if not is_dataclass(type_):
            raise AdapterError(f"{type_.__name__} is not a dataclass")
        self.type = type_
        self._fields = {field.name: field for field in fields(type_)}

    def fields(self) -> dict[str, Any]:
        """Return canonical field annotations."""
        hints = resolved_fields(self.type)
        return {field.name: hints.get(field.name, field.type) for field in self._fields.values()}

    def read(self, value: Any, name: str) -> Any:
        """Read a canonical dataclass attribute."""
        return getattr(value, name)

    def project(self, value: Any) -> Mapping[str, Any]:
        """Validate and read a projected dataclass through its native boundary."""
        if not isinstance(value, self.type):
            raise AdapterError(f"projection returned {type(value).__name__}, expected {self.type.__name__}")
        names = set(self._fields)
        instance_fields = getattr(value, "__dict__", None)
        unknown = set(instance_fields or {}) - names
        if unknown:
            raise AdapterError(f"projection returned unknown fields: {sorted(unknown)!r}")
        try:
            return {name: self.read(value, name) for name in names}
        except AttributeError as error:
            raise AdapterError(f"projection returned an unreadable field: {error}") from error

    def construct(self, values: Mapping[str, Any]) -> Any:
        """Construct the destination through its native constructor."""
        return self.type(**values)

    def required(self, name: str) -> bool:
        """Return whether native construction requires `name`."""
        field = self._fields[name]
        return field.default is MISSING and field.default_factory is MISSING
