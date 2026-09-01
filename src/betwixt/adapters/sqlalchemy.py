"""Optional SQLAlchemy mapped-class adapter."""

import types
from collections.abc import Mapping
from typing import Any, Union, get_args, get_origin, get_type_hints

from betwixt.errors import AdapterError, UnloadedFieldError


class SQLAlchemyAdapter:
    """Adapt mapped declarative classes using canonical Python attribute names."""

    def __init__(self, type_: type[Any]) -> None:
        try:
            from sqlalchemy import inspect
            from sqlalchemy.exc import NoInspectionAvailable
        except ImportError as error:
            raise ImportError("Install betwixt[sqlalchemy] to use SQLAlchemy mappings") from error
        self.type = type_
        try:
            self.mapper = inspect(type_)
        except (AttributeError, TypeError, NoInspectionAvailable) as error:
            raise AdapterError(f"{type_.__name__} is not a mapped SQLAlchemy class") from error
        self._fields = self.fields()

    def fields(self) -> dict[str, Any]:
        names = [attribute.key for attribute in self.mapper.column_attrs]
        names.extend(attribute.key for attribute in self.mapper.relationships)
        hints = get_type_hints(self.type, include_extras=True)
        result = {}
        for name in names:
            annotation = hints.get(name, Any)
            if get_origin(annotation) is not None and get_origin(annotation).__name__ == "Mapped":
                annotation = get_args(annotation)[0]
            result[name] = annotation
        return result

    def read(self, value: Any, name: str) -> Any:
        from sqlalchemy import inspect

        if name in inspect(value).unloaded:
            raise UnloadedFieldError(f"SQLAlchemy field {name!r} is unloaded")
        return getattr(value, name)

    def project(self, value: Any) -> Mapping[str, Any]:
        """Validate and read a projected mapped object through the adapter boundary."""
        if not isinstance(value, self.type):
            raise AdapterError(f"projection returned {type(value).__name__}, expected {self.type.__name__}")
        instance_fields = getattr(value, "__dict__", None)
        unknown = {name for name in (instance_fields or {}) if not name.startswith("_") and name not in self._fields}
        if unknown:
            raise AdapterError(f"projection returned unknown fields: {sorted(unknown)!r}")
        try:
            return {name: self.read(value, name) for name in self._fields}
        except (AttributeError, UnloadedFieldError) as error:
            raise AdapterError(f"projection returned an unreadable field: {error}") from error

    def construct(self, values: Mapping[str, Any]) -> Any:
        return self.type(**values)

    def required(self, name: str) -> bool:
        annotation = self._fields[name]
        origin = get_origin(annotation)
        if origin in (Union, types.UnionType) and type(None) in get_args(annotation):
            return False
        attribute = self.mapper.attrs[name]
        if hasattr(attribute, "columns"):
            column = attribute.columns[0]
            # A server default is not available to Betwixt before construction.
            return not column.nullable and column.default is None
        # SQLAlchemy's native constructor permits omitted relationships; a missing
        # relationship is therefore filled by its instrumentation/default behavior.
        return False
