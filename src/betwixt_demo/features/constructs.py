"""Focused demos for Betwixt's core construct families."""


def demo_field_constructs() -> None:
    """
    Compare one-way and pairwise field mappings for renamed and transformed values.

    `map_rightward` and `map_leftward` are directional. Use `map_pairwise` when each direction needs its own callable.
    The source stores coordinates as integer hundredths while the wire model uses floats.
    """
    from dataclasses import dataclass

    from betwixt import (
        Betwixt,
        field_refs,
        map_leftward,
        map_pairwise,
        map_rightward,
    )

    @dataclass
    class Coordinates:
        latitude: int
        longitude: int
        label: str

    @dataclass
    class WireCoordinates:
        lat: float
        lon: float
        label: str

    class CoordinatesTwixt(Betwixt):
        left = Coordinates
        right = WireCoordinates
        (L, R) = field_refs(left, right)
        lat_rightward = map_rightward(left=L.latitude, right=R.lat, rightward=lambda value: round(value / 100, 2))
        lat_leftward = map_leftward(right=R.lat, left=L.latitude, leftward=lambda value: round(value * 100))
        lon_rightward = map_rightward(left=L.longitude, right=R.lon, rightward=lambda value: round(value / 100, 2))
        lon_leftward = map_leftward(right=R.lon, left=L.longitude, leftward=lambda value: round(value * 100))
        label = map_pairwise(
            left=L.label,
            right=R.label,
            rightward=str.upper,
            leftward=str.lower,
        )

    mapping = CoordinatesTwixt()
    print(mapping.rightward(Coordinates(4512, -12260, "home")))
    print(mapping.leftward(WireCoordinates(45.12, -122.60, "HOME")))


def demo_expansion_constructs() -> None:
    """
    Expand one display name into ordered first and last name fields.

    `expand_rightward` writes every tuple item to its corresponding destination field, while `map_leftward` combines
    those fields in the opposite direction. Partial operations require only the one source key and return all outputs.
    """
    from dataclasses import dataclass

    from betwixt import Betwixt, expand_rightward, field_refs, map_leftward

    @dataclass
    class Profile:
        display_name: str

    @dataclass
    class ProfileView:
        first_name: str
        last_name: str

    class ProfileTwixt(Betwixt):
        left = Profile
        right = ProfileView
        (L, R) = field_refs(left, right)
        split_name = expand_rightward(
            left=L.display_name,
            right=(R.first_name, R.last_name),
            rightward=lambda display_name: tuple(display_name.split(" ", 1)),
        )
        join_name = map_leftward(
            right=(R.first_name, R.last_name),
            left=L.display_name,
            leftward=lambda first_name, last_name: f"{first_name} {last_name}",
        )

    mapping = ProfileTwixt()
    print(mapping.rightward(Profile("Ada Lovelace")))
    print(mapping.rightward_partial({"display_name": "Grace Hopper"}))
    print(mapping.leftward(ProfileView("Ada", "Lovelace")))


def demo_object_constructs() -> None:
    """
    Use reductions for context and projections for whole-object boundary conversion.

    A reduction receives the complete source object, while a projection returns a complete destination object. These
    constructs are useful when a single field or callable needs to coordinate a whole boundary model.
    """
    from dataclasses import dataclass

    from betwixt import Betwixt, field_refs, project_leftward, project_rightward, reduce_leftward, reduce_rightward

    @dataclass
    class Report:
        title: str
        body: str

    @dataclass
    class Envelope:
        title: str
        body: str
        source: str

    class ReportTwixt(Betwixt):
        left = Report
        right = Envelope
        (L, R) = field_refs(left, right)
        source = reduce_rightward(right=R.source, rightward=lambda report, *, ctx: ctx)
        projected_envelope = project_rightward(
            rightward=lambda report: Envelope(report.title, report.body, "projected")
        )
        body = reduce_leftward(left=L.body, leftward=lambda envelope, *, ctx: f"{envelope.body} ({ctx})")
        projected_report = project_leftward(leftward=lambda envelope: Report(envelope.title, envelope.body))

    mapping = ReportTwixt()
    print(mapping.rightward(Report("Status", "All systems nominal"), context="monitor"))
    print(mapping.leftward(Envelope("Status", "All systems nominal", "monitor"), context="copied"))


def demo_nested_controls() -> None:
    """
    Combine nesting with implicit-mapping controls to make boundaries explicit.

    Nested mappings preserve the shape of supported containers. The destination model owns its `kind` default, while
    `disable_implicit_pairwise` prevents an accidental same-name write.
    """
    from dataclasses import dataclass

    from betwixt import Betwixt, disable_implicit_pairwise, field_refs, map_pairwise, nested_pairwise

    @dataclass
    class Name:
        first: str
        last: str

    @dataclass
    class NameView:
        display: str

    class NameTwixt(Betwixt):
        left = Name
        right = NameView
        (L, R) = field_refs(left, right)
        display = map_pairwise(
            left=L.first,
            right=R.display,
            rightward=lambda value: value,
            leftward=lambda value: value,
        )

    @dataclass
    class Profile:
        name: Name
        nickname: str

    @dataclass
    class ProfileView:
        name: NameView
        kind: str = "profile"
        nickname: str = "unknown"

    class ProfileTwixt(Betwixt):
        left = Profile
        right = ProfileView
        (L, R) = field_refs(left, right)
        disable_implicit_mapping = True
        name = nested_pairwise(
            left=L.name,
            right=R.name,
            via=NameTwixt,
            rightward=lambda value: value,
            leftward=lambda value: value,
        )
        disable_nickname = disable_implicit_pairwise(left=L.nickname, right=R.nickname)

    print(ProfileTwixt().rightward(Profile(Name("Ada", "Lovelace"), "analyst")))
    print(ProfileTwixt().rightward_partial({"name": {"first": "Grace"}}))
