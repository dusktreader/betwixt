"""Process-local adapter registry."""

from dataclasses import is_dataclass
from typing import Any

from betwixt.adapters.base import optional_adapter
from betwixt.errors import AdapterError


class AdapterRegistry:
    """Resolve exact, MRO, and built-in adapters in deterministic order."""

    def __init__(self) -> None:
        self._registered: dict[type[Any], Any] = {}

    def register(self, type_: type[Any], adapter: Any, *, replace: bool = False) -> None:
        """Register `adapter` for `type_`, rejecting accidental replacement."""
        if type_ in self._registered and not replace:
            raise AdapterError(f"An adapter is already registered for {type_.__name__}")
        self._registered[type_] = adapter

    def lookup(self, type_: type[Any]) -> Any:
        """Resolve an adapter using exact registration, MRO, then built-ins."""
        if type_ in self._registered:
            return self._registered[type_]
        for base in type_.__mro__[1:]:
            if base in self._registered:
                return self._registered[base]
        if is_dataclass(type_):
            from betwixt.adapters.dataclass import DataclassAdapter

            return DataclassAdapter(type_)
        from betwixt.adapters.typeddict import TypedDictAdapter, is_typed_dict

        if is_typed_dict(type_):
            return TypedDictAdapter(type_)
        return optional_adapter(type_)


registry = AdapterRegistry()


def register_adapter(type_: type[Any], adapter: Any, *, replace: bool = False) -> None:
    """Register an adapter in the process-local registry."""
    registry.register(type_, adapter, replace=replace)


def get_adapter(type_: type[Any]) -> Any:
    """Resolve an adapter from the process-local registry."""
    return registry.lookup(type_)
