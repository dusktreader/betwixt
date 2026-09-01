"""Reference the core Betwixt construct families."""

from dataclasses import dataclass

from betwixt import (
    Betwixt,
    disable_implicit_pairwise,
    field_refs,
    map_leftward,
    map_pairwise,
    map_rightward,
    nested_pairwise,
    project_leftward,
    project_rightward,
    reduce_leftward,
    reduce_rightward,
)


@dataclass
class Coordinates:
    """Store coordinates as integer hundredths."""

    latitude: int
    longitude: int
    label: str


@dataclass
class WireCoordinates:
    """Expose coordinates as decimal degrees."""

    lat: float
    lon: float
    label: str


class CoordinatesTwixt(Betwixt):
    """Show directional and pairwise field mappings with model construction."""

    left = Coordinates
    right = WireCoordinates
    (L, R) = field_refs(left, right)
    lat_rightward = map_rightward(left=L.latitude, right=R.lat, rightward=lambda value: value / 100)
    lat_leftward = map_leftward(right=R.lat, left=L.latitude, leftward=lambda value: round(value * 100))
    lon_rightward = map_rightward(left=L.longitude, right=R.lon, rightward=lambda value: value / 100)
    lon_leftward = map_leftward(right=R.lon, left=L.longitude, leftward=lambda value: round(value * 100))
    label = map_pairwise(left=L.label, right=R.label, rightward=str.upper, leftward=str.lower)


coordinates = CoordinatesTwixt().rightward(Coordinates(4512, -12260, "home"))
original_coordinates = CoordinatesTwixt().leftward(coordinates)


@dataclass
class Report:
    """Represent a report before it crosses an object boundary."""

    title: str
    body: str


@dataclass
class Envelope:
    """Represent a report envelope with boundary metadata."""

    title: str
    body: str
    source: str


class ReportTwixt(Betwixt):
    """Use reductions for one field and projections for complete objects."""

    left = Report
    right = Envelope
    (L, R) = field_refs(left, right)
    source = reduce_rightward(right=R.source, rightward=lambda report, *, ctx: ctx)
    body = reduce_leftward(left=L.body, leftward=lambda envelope, *, ctx: f"{envelope.body} ({ctx})")
    projected_envelope = project_rightward(rightward=lambda report: Envelope(report.title, report.body, "projected"))
    projected_report = project_leftward(leftward=lambda envelope: Report(envelope.title, envelope.body))


report_twixt = ReportTwixt()
envelope = report_twixt.rightward(Report("Status", "Nominal"), context="monitor")
report = report_twixt.leftward(envelope, context="copied")


@dataclass
class Name:
    """Store a person's separate names."""

    first: str
    last: str


@dataclass
class NameView:
    """Expose a person's display name."""

    display: str


class NameTwixt(Betwixt):
    """Map a nested name value in both directions."""

    left = Name
    right = NameView
    (L, R) = field_refs(left, right)
    display = map_pairwise(
        left=(L.first, L.last),
        right=R.display,
        rightward=lambda first, last: f"{first} {last}",
        leftward=lambda display: tuple(display.split(" ", 1)),
    )


@dataclass
class Profile:
    """Represent a profile with a nested name."""

    name: Name
    nickname: str


@dataclass
class ProfileView:
    """Represent a profile response with a model-owned kind default."""

    name: NameView
    kind: str = "profile"
    nickname: str = "unknown"


class ProfileTwixt(Betwixt):
    """Combine nesting and explicit implicit-mapping control."""

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


profile_twixt = ProfileTwixt()
profile_view = profile_twixt.rightward(Profile(Name("Ada", "Lovelace"), "analyst"))
profile_patch = profile_twixt.rightward_partial({"name": {"first": "Grace"}})
