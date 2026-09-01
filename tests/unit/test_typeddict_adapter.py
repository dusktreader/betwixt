"""Tests for the dependency-free TypedDict adapter."""

from dataclasses import dataclass
from typing import NotRequired, Required, TypedDict

import pytest
from betwixt.adapters.registry import AdapterRegistry

from betwixt import AdapterError, Betwixt, TypedDictAdapter, field_refs

pytestmark = pytest.mark.unit


class PersonView(TypedDict):
    """Represent a complete person view."""

    name: str
    age: int


class PartialPersonView(TypedDict, total=False):
    """Represent a sparse person view."""

    name: Required[str]
    age: NotRequired[int]


@dataclass
class Person:
    """Represent a person model."""

    name: str
    age: int


def test_adapter_exposes_fields_metadata_and_plain_dict_boundary() -> None:
    """Expose inherited annotations, requiredness, key reads, and native construction."""
    adapter = TypedDictAdapter(PersonView)

    assert adapter.fields() == {"name": str, "age": int}
    assert adapter.required("name")
    assert adapter.required("age")
    assert adapter.read({"name": "Ada", "age": 36}, "name") == "Ada"
    assert adapter.project({"name": "Ada", "age": 36}) == {"name": "Ada", "age": 36}
    assert adapter.construct({"name": "Ada", "age": 36}) == {"name": "Ada", "age": 36}


def test_optional_and_required_typed_dict_keys() -> None:
    """Honor Required and NotRequired metadata in a non-total TypedDict."""
    adapter = TypedDictAdapter(PartialPersonView)

    assert adapter.required("name")
    assert not adapter.required("age")


def test_adapter_rejects_non_typed_dict_and_supports_legacy_metadata() -> None:
    """Reject ordinary classes and use metadata fallback when the typing helper is unavailable."""
    with pytest.raises(AdapterError, match="not a TypedDict"):
        TypedDictAdapter(Person)

    class LegacyTypedDict(dict):
        value: int
        __required_keys__ = frozenset()
        __optional_keys__ = frozenset()
        __total__ = True

    adapter = TypedDictAdapter(LegacyTypedDict)
    assert adapter.required("value")


def test_registry_prefers_typed_dict_before_optional_adapters() -> None:
    """Resolve TypedDicts as built-in boundaries without importing optional packages."""
    adapter = AdapterRegistry().lookup(PersonView)

    assert isinstance(adapter, TypedDictAdapter)


def test_typed_dict_mapping_boundaries_reject_malformed_values() -> None:
    """Use Betwixt-owned errors for invalid reads and projections."""
    adapter = TypedDictAdapter(PersonView)

    with pytest.raises(AdapterError, match="non-mapping"):
        adapter.read(Person("Ada", 36), "name")
    with pytest.raises(AdapterError, match="TypedDict field"):
        adapter.read({"name": "Ada"}, "age")
    with pytest.raises(AdapterError, match="expected a mapping"):
        adapter.project(Person("Ada", 36))
    with pytest.raises(AdapterError, match="unknown fields"):
        adapter.project({"name": "Ada", "age": 36, "extra": True})
    with pytest.raises(AdapterError, match="unreadable field"):
        adapter.project({"name": "Ada"})


def test_dataclass_and_typed_dict_map_in_both_directions_and_partially() -> None:
    """Map full and sparse values between a dataclass and a TypedDict."""
    left, right = field_refs(Person, PersonView)

    class PersonTwixt(Betwixt):
        left = Person
        right = PersonView
        (L, R) = field_refs(left, right)

    mapping = PersonTwixt()
    assert mapping.rightward(Person("Ada", 36)) == {"name": "Ada", "age": 36}
    assert mapping.leftward({"name": "Ada", "age": 36}) == Person("Ada", 36)
    assert mapping.rightward_partial({"name": "Ada"}) == {"name": "Ada"}
    assert mapping.leftward_partial({"age": 36}) == {"age": 36}
    assert left.name.name == "name"
    assert right.age.name == "age"
