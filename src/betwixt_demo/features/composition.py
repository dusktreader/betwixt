"""Composition and declaration-order demo."""


def demo_declaration_order() -> None:
    """
    Show that declarations run in class-body order and later writes win.

    The first declaration writes `4`; the second writes `30`, replacing it. This makes declaration order an explicit
    part of a composed mapping's behavior.
    """
    from dataclasses import dataclass

    from betwixt import Betwixt, field_refs, map_rightward

    @dataclass
    class Source:
        value: int

    @dataclass
    class Destination:
        value: int

    class OrderedTwixt(Betwixt):
        left = Source
        right = Destination
        (L, R) = field_refs(left, right)
        first_write = map_rightward(left=L.value, right=R.value, rightward=lambda value: value + 1)
        second_write = map_rightward(left=L.value, right=R.value, rightward=lambda value: value * 10)

    print(OrderedTwixt().rightward(Source(3)))
