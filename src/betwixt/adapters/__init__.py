"""Built-in adapter exports."""

from betwixt.adapters.dataclass import DataclassAdapter
from betwixt.adapters.registry import AdapterRegistry, get_adapter, register_adapter, registry
from betwixt.adapters.typeddict import TypedDictAdapter

__all__ = ["AdapterRegistry", "DataclassAdapter", "TypedDictAdapter", "get_adapter", "register_adapter", "registry"]
