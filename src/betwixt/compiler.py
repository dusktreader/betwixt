"""Compile declarations into direction-specific producers."""

from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Any

from betwixt.errors import DeclarationError


@dataclass(frozen=True)
class Producer:
    """Represent one executable destination-field producer."""

    destination: str
    source: tuple[str, ...]
    function: Any
    kind: str
    via: Any = None
    derive: Any = None


def validate_callable(function: Any) -> None:
    """Require context parameters to be final keyword-only `ctx` parameters."""
    if function is None or not callable(function):
        raise DeclarationError("mapping callable must be callable")
    try:
        parameters = list(signature(function).parameters.values())
    except (TypeError, ValueError) as error:
        raise DeclarationError("mapping callable must have an inspectable signature") from error
    for index, parameter in enumerate(parameters):
        if parameter.name == "ctx" and (parameter.kind is not Parameter.KEYWORD_ONLY or index != len(parameters) - 1):
            raise DeclarationError("ctx must be the final keyword-only parameter")


def validate_derivation(function: Any) -> None:
    """Require a context derivation callable that accepts one positional value."""
    if function is None:
        return
    if not callable(function):
        raise DeclarationError("context derivation must be callable")
    try:
        signature(function).bind(object())
    except (TypeError, ValueError) as error:
        raise DeclarationError("context derivation must accept one positional context") from error


def call(function: Any, args: tuple[Any, ...], context: Any) -> Any:
    """Call a validated function with optional keyword-only context."""
    parameters = signature(function).parameters
    if "ctx" in parameters:
        return function(*args, ctx=context)
    return function(*args)
