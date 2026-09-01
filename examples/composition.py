"""Reference declaration composition and last-write-wins order."""

from dataclasses import dataclass

from betwixt import Betwixt, field_refs, map_rightward


@dataclass
class Source:
    """Represent a source value."""

    value: int


@dataclass
class Destination:
    """Represent a destination value."""

    value: int


class OrderedTwixt(Betwixt):
    """Show that a later declaration replaces an earlier write."""

    left = Source
    right = Destination
    (L, R) = field_refs(left, right)
    increment = map_rightward(left=L.value, right=R.value, rightward=lambda value: value + 1)
    final_value = map_rightward(left=L.value, right=R.value, rightward=lambda value: value * 10)


destination = OrderedTwixt().rightward(Source(3))
