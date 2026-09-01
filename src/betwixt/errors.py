"""Exceptions raised by Betwixt."""

from buzz import Buzz


class BetwixtError(Buzz):
    """Base class for Betwixt-owned errors."""


class DeclarationError(BetwixtError):
    """Report an invalid mapping declaration."""


class ExpansionError(DeclarationError):
    """Report an expansion callable returning an invalid shape."""


class AdapterError(BetwixtError):
    """Report an adapter lookup or configuration error."""


class MissingAdapterError(AdapterError):
    """Report a type whose optional adapter is unavailable."""


class UnmappedFieldError(BetwixtError):
    """Report a required destination field with no produced value."""

    def __init__(
        self,
        message: str,
        *,
        direction: str | None = None,
        source_type: type[object] | None = None,
        destination_type: type[object] | None = None,
        source_field: str | None = None,
        destination_field: str | None = None,
        source_annotation: object = None,
        destination_annotation: object = None,
        omission_reason: str | None = None,
        explanation: str | None = None,
        remedies: tuple[str, ...] = (),
    ) -> None:
        """Store the mapping contract details needed to correct an omission."""
        super().__init__(message)
        self.direction = direction
        self.source_type = source_type
        self.destination_type = destination_type
        self.source_field = source_field
        self.destination_field = destination_field
        self.source_annotation = source_annotation
        self.destination_annotation = destination_annotation
        self.omission_reason = omission_reason
        self.explanation = explanation
        self.remedies = remedies


class PartialInputError(BetwixtError):
    """Report malformed partial-operation input."""


class UnloadedFieldError(AdapterError):
    """Report an unloaded native field."""
