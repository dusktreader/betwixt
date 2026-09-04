"""Regression coverage for the executable checkout case study."""

import runpy
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).parents[2]


def test_checkout_example_validates_names_and_declared_totals() -> None:
    """Run the happy path and retain the checkout validation and reduction invariants."""
    namespace = runpy.run_path(str(ROOT / "examples" / "checkout.py"))

    checkout_request = namespace["CheckoutRequest"]
    request = namespace["request"]
    with pytest.raises(ValidationError, match="recipientName"):
        checkout_request.model_validate(request.model_dump(by_alias=True) | {"recipientName": "Ada"})

    inconsistent_request = request.model_copy(update={"total_dollars": 24.00})
    with pytest.raises(ValueError, match="declared checkout total is 2400 cents"):
        namespace["mapping"].rightward(inconsistent_request, context=namespace["context"])
