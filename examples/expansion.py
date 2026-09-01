"""Reference expansion and reverse mapping for display names."""

from dataclasses import dataclass

from betwixt import Betwixt, expand_rightward, field_refs, map_leftward


@dataclass
class Profile:
    """Store a person's complete display name."""

    display_name: str


@dataclass
class ProfileView:
    """Expose a person's first and last names separately."""

    first_name: str
    last_name: str


class ProfileTwixt(Betwixt):
    """Expand one stored value and merge the two destination fields in reverse."""

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


profile_twixt = ProfileTwixt()
profile_view = profile_twixt.rightward(Profile("Ada Lovelace"))
profile_patch = profile_twixt.rightward_partial({"display_name": "Grace Hopper"})
profile = profile_twixt.leftward(ProfileView("Ada", "Lovelace"))
