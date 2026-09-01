"""Pydantic adapter contract tests."""

from typing import ClassVar

from betwixt.adapters.pydantic import PydanticAdapter
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, ValidationError
from pytest import raises

from betwixt import AdapterError, Betwixt, field_refs, map_pairwise, map_rightward


class Source(BaseModel):
    """Provide a source model."""

    value: int


class Destination(BaseModel):
    """Provide a destination model."""

    value: int


def test_user_defined_models_are_discovered() -> None:
    """Adapt models whose module is not named pydantic."""
    left_refs, right_refs = field_refs(Source, Destination)

    class Mapping(Betwixt):
        left = Source
        right = Destination
        value = map_rightward(left=left_refs.value, right=right_refs.value, rightward=lambda value: str(value))

    assert Mapping().rightward(Source(value=3)).value == 3


def test_leftward_full_and_partial_mapping_uses_context_and_native_construction() -> None:
    """Translate a Pydantic model leftward and preserve sparse canonical patches."""
    left_refs, right_refs = field_refs(Source, Destination)

    class Mapping(Betwixt):
        left = Source
        right = Destination
        value = map_pairwise(
            left=left_refs.value,
            right=right_refs.value,
            rightward=lambda value: value,
            leftward=lambda value, *, ctx=0: value + ctx,
        )

    mapping = Mapping()
    assert mapping.leftward(Destination(value=4), context=3) == Source(value=7)
    assert mapping.leftward_partial({"value": 4}, context=3) == {"value": 7}


def test_alias_only_destination_is_rejected() -> None:
    """Reject canonical values when a destination only accepts an alias."""

    class Aliased(BaseModel):
        model_config = ConfigDict(populate_by_name=False)
        value: int = Field(alias="v")

    left_refs, right_refs = field_refs(Source, Aliased)

    class Mapping(Betwixt):
        left = Source
        right = Aliased
        value = map_rightward(left=left_refs.value, right=right_refs.value, rightward=lambda value: value)

    with raises(AdapterError):
        Mapping().rightward(Source(value=3))


def test_alias_choices_accept_a_canonical_choice_without_populate_by_name() -> None:
    """Allow native construction when canonical input is one validation-alias choice."""

    class Aliased(BaseModel):
        value: int = Field(validation_alias=AliasChoices("wire_value", "value"))

    adapter = PydanticAdapter(Aliased)

    assert adapter.construct({"value": "3"}).value == 3
    assert adapter.construct({"value": 4}).value == 4

    class ExplicitCanonicalAlias(BaseModel):
        value: int = Field(validation_alias="value")

    assert PydanticAdapter(ExplicitCanonicalAlias).construct({"value": 5}).value == 5


def test_validation_alias_choices_without_canonical_name_remain_rejected() -> None:
    """Reject an AliasChoices declaration that truly excludes the canonical name."""

    class Aliased(BaseModel):
        value: int = Field(validation_alias=AliasChoices("wire_value", "other_value"))

    with raises(AdapterError, match="rejects canonical field"):
        PydanticAdapter(Aliased).construct({"value": 3})


def test_native_pydantic_validation_errors_propagate_unchanged() -> None:
    """Leave destination validation failures at the native Pydantic boundary."""

    class Positive(BaseModel):
        value: int = Field(gt=0)

    with raises(ValidationError):
        PydanticAdapter(Positive).construct({"value": "not-an-integer"})


def test_alias_matrix_preserves_canonical_partial_keys_and_defaults() -> None:
    """Keep references and sparse patches canonical across validation and serialization aliases."""

    class Aliased(BaseModel):
        model_config = ConfigDict(populate_by_name=False)
        value: int = Field(
            validation_alias=AliasChoices("wire_value", "value"),
            serialization_alias="output_value",
        )
        with_default: int = 9

    refs_left, refs_right = field_refs(Source, Aliased)

    class Mapping(Betwixt):
        left = Source
        right = Aliased
        value = map_rightward(left=refs_left.value, right=refs_right.value, rightward=lambda value: value)

    assert refs_right.value.name == "value"
    assert Mapping().rightward_partial({"value": "8"}) == {"value": "8"}
    result = Mapping().rightward(Source(value="7"))
    assert result.value == 7
    assert result.with_default == 9


def test_alias_metadata_does_not_change_canonical_references() -> None:
    """Keep field references and partial patches on Python names."""

    class Aliased(BaseModel):
        model_config = ConfigDict(populate_by_name=True)
        value: int = Field(validation_alias="input_value", serialization_alias="output_value")
        with_default: int = 7

    class SourceWithAliases(BaseModel):
        value: int = Field(validation_alias="input_value", serialization_alias="output_value")
        with_default: int = 3

    left_refs, right_refs = field_refs(SourceWithAliases, Aliased)

    class Mapping(Betwixt):
        left = SourceWithAliases
        right = Aliased
        value = map_rightward(left=left_refs.value, right=right_refs.value, rightward=lambda value: value)

    assert right_refs.value.name == "value"
    assert Mapping().rightward_partial({"value": "4"}) == {"value": "4"}
    assert Mapping().rightward(SourceWithAliases(input_value="4")).value == 4


def test_pydantic_adapter_rejects_non_models() -> None:
    """Report an adapter configuration error for a non-Pydantic type."""
    with raises(AdapterError, match="BaseModel"):
        PydanticAdapter(str)


def test_pydantic_required_uses_native_field_metadata() -> None:
    """Expose Pydantic's required-field decision without adding validation."""

    class Model(BaseModel):
        required: int
        optional: int = 1

    adapter = PydanticAdapter(Model)
    assert adapter.required("required") is True
    assert adapter.required("optional") is False


def test_pydantic_fields_exclude_class_variables() -> None:
    """Expose only Pydantic input fields, not class-level annotations."""

    class Model(BaseModel):
        value: int
        kind: ClassVar[str] = "constant"

    adapter = PydanticAdapter(Model)

    assert adapter.fields() == {"value": int}
    assert set(Model.model_fields) == {"value"}
    assert adapter.required("value") is True
    assert adapter.construct({"value": 3}) == Model(value=3)


def test_pydantic_projection_uses_only_validated_model_fields() -> None:
    """Accept a model projection and reject wrong or extra model values."""

    class Model(BaseModel):
        model_config = ConfigDict(extra="allow")
        value: int

    adapter = PydanticAdapter(Model)
    assert adapter.project(Model(value=3)) == {"value": 3}
    with raises(AdapterError, match="expected Model"):
        adapter.project({"value": 3})
    with raises(AdapterError, match="unknown fields"):
        adapter.project(Model(value=3, extra=True))
    unreadable = Model(value=3)
    object.__delattr__(unreadable, "value")
    with raises(AdapterError, match="unreadable field"):
        adapter.project(unreadable)
