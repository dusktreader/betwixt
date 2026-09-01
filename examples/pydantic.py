"""Reference a dataclass-to-Pydantic mapping with canonical aliases."""

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

from betwixt import Betwixt, field_refs, map_pairwise


@dataclass
class UserInput:
    """Represent a non-Pydantic source payload."""

    name: str
    score: int


class UserModel(BaseModel):
    """Validate a response while serializing canonical fields with aliases."""

    model_config = ConfigDict(populate_by_name=True)
    name: str = Field(serialization_alias="displayName")
    score: int


class UserTwixt(Betwixt):
    """Map dataclass attributes to Pydantic canonical field names."""

    left = UserInput
    right = UserModel
    (L, R) = field_refs(left, right)
    name = map_pairwise(left=L.name, right=R.name, rightward=str.title, leftward=str.lower)


user_twixt = UserTwixt()
user_model = user_twixt.rightward(UserInput("ada", 10))
serialized_user = user_model.model_dump(by_alias=True)
user_input = user_twixt.leftward(UserModel(name="Ada", score=10))
