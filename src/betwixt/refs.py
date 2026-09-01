"""Typed field references used in declarations."""

from dataclasses import dataclass
from typing import Any

from betwixt.constants import Side
from betwixt.errors import DeclarationError


@dataclass(frozen=True)
class FieldRef:
    """Identify one canonical field on one declared side."""

    side: Side
    owner: type[Any]
    name: str


class FieldProxy:
    """Create checked field references for a declared model type."""

    def __init__(self, side: Side, owner: type[Any]) -> None:
        self.side = side
        self.owner = owner

    def __getattr__(self, name: str) -> FieldRef:
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        annotations = getattr(self.owner, "__annotations__", {})
        model_fields = getattr(self.owner, "model_fields", {})
        if name not in annotations and name not in model_fields and not hasattr(self.owner, name):
            raise DeclarationError(f"{self.side} type {self.owner.__name__!r} has no field {name!r}")
        return FieldRef(self.side, self.owner, name)


def field_refs(left: type[Any], right: type[Any]) -> tuple[FieldProxy, FieldProxy]:
    """Return typed proxies for the left and right declaration types."""

    return FieldProxy("left", left), FieldProxy("right", right)
