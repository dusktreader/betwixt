"""Optional Pydantic demo."""


def demo_pydantic() -> None:
    """
    Install `betwixt[pydantic]` for a dataclass-to-Pydantic mapping and canonical alias handling.

    The dataclass supplies the source object. Pydantic validates the native destination and keeps `name` as the
    canonical Betwixt field even when its serialized alias is `display_name`.
    """
    from dataclasses import dataclass

    from pydantic import BaseModel, ConfigDict, Field

    from betwixt import Betwixt, field_refs, map_pairwise

    @dataclass
    class Input:
        name: str
        score: int

    class ApiModel(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        name: str = Field(serialization_alias="display_name")
        score: int

    class PydanticTwixt(Betwixt):
        left = Input
        right = ApiModel
        (L, R) = field_refs(left, right)
        name = map_pairwise(left=L.name, right=R.name, rightward=str.title, leftward=str.lower)

    result = PydanticTwixt().rightward(Input(name="ada", score=10))
    print(result)
    print(result.model_dump(by_alias=True))
