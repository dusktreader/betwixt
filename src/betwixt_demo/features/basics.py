"""Dependency-free introductory demos."""


def demo_builtin_mapping() -> None:
    """
    Start with the built-in dataclass adapter and implicit same-name mapping.

    Both dataclasses have the same field names and compatible types, so Betwixt can translate them without explicit
    mapping declarations.
    """
    from dataclasses import dataclass

    from betwixt import Betwixt

    @dataclass
    class Person:
        name: str
        age: int

    @dataclass
    class PersonView:
        name: str
        age: int

    class PersonTwixt(Betwixt):
        left = Person
        right = PersonView

    source = Person("Ada", 36)
    print(PersonTwixt().rightward(source))
