"""Optional Pydantic v2 adapter."""

from collections.abc import Mapping
from typing import Any

from betwixt.annotations import resolved_fields
from betwixt.errors import AdapterError


class PydanticAdapter:
    """Adapt a Pydantic model through its native constructor."""

    def __init__(self, type_: type[Any]) -> None:
        try:
            from pydantic import BaseModel
        except ImportError as error:
            raise ImportError("Install betwixt[pydantic] to use Pydantic mappings") from error
        if not isinstance(type_, type) or not issubclass(type_, BaseModel):
            raise AdapterError(f"{type_.__name__} is not a Pydantic BaseModel")
        self.type = type_

    def fields(self) -> dict[str, Any]:
        hints = resolved_fields(self.type)
        return {name: hints.get(name, field.annotation) for name, field in self.type.model_fields.items()}

    def read(self, value: Any, name: str) -> Any:
        return getattr(value, name)

    def project(self, value: Any) -> Mapping[str, Any]:
        """Validate and read a projected model through Pydantic's field boundary."""
        if not isinstance(value, self.type):
            raise AdapterError(f"projection returned {type(value).__name__}, expected {self.type.__name__}")
        unknown = set(value.model_extra or {})
        if unknown:
            raise AdapterError(f"projection returned unknown fields: {sorted(unknown)!r}")
        try:
            return {name: self.read(value, name) for name in self.type.model_fields}
        except AttributeError as error:
            raise AdapterError(f"projection returned an unreadable field: {error}") from error

    def construct(self, values: Mapping[str, Any]) -> Any:
        for name in values:
            field = self.type.model_fields[name]
            validation_alias = field.validation_alias
            accepts_name = bool(
                self.type.model_config.get("populate_by_name", False)
                or self.type.model_config.get("validate_by_name", False)
                or _validation_alias_accepts_name(validation_alias, name)
            )
            if validation_alias is not None and validation_alias != name and not accepts_name:
                raise AdapterError(
                    f"Pydantic destination {self.type.__name__} rejects canonical field {name!r}; "
                    "enable populate_by_name (or validate_by_name) or provide an explicit mapping"
                )
        return self.type(**values)

    def required(self, name: str) -> bool:
        return self.type.model_fields[name].is_required()


def _validation_alias_accepts_name(validation_alias: Any, name: str) -> bool:
    """Return whether a validation alias includes the canonical field name."""
    if validation_alias == name:
        return True
    return name in getattr(validation_alias, "choices", ())
