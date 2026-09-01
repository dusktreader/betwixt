"""Reference implicit same-name mapping from a dataclass to a TypedDict."""

from dataclasses import dataclass
from typing import TypedDict

from betwixt import Betwixt, field_refs


@dataclass
class Person:
    """Represent the source person."""

    name: str
    age: int


class PersonView(TypedDict):
    """Represent the destination person view."""

    name: str
    age: int


class PersonTwixt(Betwixt):
    """Map compatible same-name fields from a dataclass to a TypedDict."""

    left = Person
    right = PersonView
    (L, R) = field_refs(left, right)


person_view = PersonTwixt().rightward(Person(name="Ada", age=36))
person = PersonTwixt().leftward(person_view)
partial_view = PersonTwixt().rightward_partial({"name": "Ada"})
partial_person = PersonTwixt().leftward_partial({"age": 36})
