"""Adapter lookup primitives."""

from typing import Any

from betwixt.errors import MissingAdapterError
from betwixt.types import Adapter


def optional_adapter(type_: type[Any]) -> Adapter | None:
    """Return a native optional adapter for `type_`, when its dependency is installed."""

    module = type_.__module__
    is_pydantic = module == "pydantic" or module.startswith("pydantic.")
    if not is_pydantic:
        try:
            from pydantic import BaseModel

            is_pydantic = isinstance(type_, type) and issubclass(type_, BaseModel)
        except ImportError:
            pass
    if is_pydantic:
        try:
            from betwixt.adapters.pydantic import PydanticAdapter
        except ImportError:
            return None
        return PydanticAdapter(type_)
    if module.startswith("sqlalchemy") or hasattr(type_, "__mapper__"):
        try:
            from betwixt.adapters.sqlalchemy import SQLAlchemyAdapter
        except ImportError:
            return None
        return SQLAlchemyAdapter(type_)
    return None


def require_adapter(type_: type[Any], registry: Any) -> Adapter:
    """Resolve an adapter or raise an actionable missing-adapter error."""

    adapter = registry.lookup(type_)
    if adapter is None:
        raise MissingAdapterError(
            f"No adapter is registered for {type_.__name__}; install the relevant Betwixt extra or register an Adapter"
        )
    return adapter
