"""Public structural types used by Betwixt."""

from collections.abc import Callable, Mapping
from typing import Any, Protocol, TypeVar

T = TypeVar("T")


class Adapter(Protocol):
    """
    Adapt one boundary model to the operations required by a Betwixt mapping.

    An adapter:
      * defines the model's canonical Python fields and annotations
      * reads values from an existing instance
      * extracts values from a projection
      * constructs a native instance from translated values
      * reports which fields must be present for construction.

    Adapters keep Betwixt independent of any particular dataclass, validation, or
    persistence library while leaving native construction and validation at the model boundary.
    """

    type: type[Any]

    def fields(self) -> Mapping[str, Any]: ...

    def read(self, value: Any, name: str) -> Any: ...

    def project(self, value: Any) -> Mapping[str, Any]: ...

    def construct(self, values: Mapping[str, Any]) -> Any: ...

    def required(self, name: str) -> bool: ...


ContextCallable = Callable[..., Any]
