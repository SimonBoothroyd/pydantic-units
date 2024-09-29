import importlib

import pydantic
import pytest
from openmm.unit import Quantity, angstrom, kelvin, nanometer


def test_pydantic_units():
    assert importlib.import_module("pydantic_units") is not None


def _validate_v1_model(model, model_cls):
    model_json = model.json()
    assert model_json == '{"a": "1 A", "b": "0.1 nm"}'

    model_schema = model.schema()
    assert model_schema == {
        "properties": {
            "a": {"title": "A", "type": "string"},
            "b": {"title": "B", "type": "string"},
        },
        "required": ["a", "b"],
        "title": "Model",
        "type": "object",
    }

    model_from_json = model_cls.parse_raw(model_json)
    assert model_from_json.a.unit == angstrom
    assert model_from_json.a.value_in_unit(angstrom) == pytest.approx(1.0)

    assert model_from_json.b.unit == nanometer
    assert model_from_json.b.value_in_unit(nanometer) == pytest.approx(0.1)


def test_v1():
    if not pydantic.__version__.startswith("1."):
        pytest.skip("pydantic is not version 1.x")

    from pydantic_units import OpenMMQuantity, quantity_serializer

    class Model(pydantic.BaseModel):
        class Config:
            json_encoders = {Quantity: quantity_serializer}

        a: OpenMMQuantity[angstrom]
        b: OpenMMQuantity[nanometer]

    _validate_v1_model(Model(a=1 * angstrom, b=1 * angstrom), Model)


def test_v1_compat():
    import pydantic

    if not pydantic.__version__.startswith("2."):
        pytest.skip("pydantic is not version 2.x")

    import pydantic.v1

    from pydantic_units import quantity_serializer
    from pydantic_units.v1 import OpenMMQuantity

    class Model(pydantic.v1.BaseModel):
        class Config:
            json_encoders = {Quantity: quantity_serializer}

        a: OpenMMQuantity[angstrom]
        b: OpenMMQuantity[nanometer]

    _validate_v1_model(Model(a=1 * angstrom, b=1 * angstrom), Model)


def test_v2():
    if pydantic.__version__.startswith("1."):
        pytest.skip("pydantic has version 1.x")

    from pydantic_units import OpenMMQuantity

    class Model(pydantic.BaseModel):
        a: OpenMMQuantity[angstrom]
        b: OpenMMQuantity[nanometer]

    model = Model(a=1 * angstrom, b=1 * angstrom)

    model_json = model.model_dump_json()
    assert model_json == '{"a":"1 A","b":"0.1 nm"}'

    model_schema = model.model_json_schema()
    assert model_schema == {
        "properties": {
            "a": {"title": "A", "type": "string"},
            "b": {"title": "B", "type": "string"},
        },
        "required": ["a", "b"],
        "title": "Model",
        "type": "object",
    }

    model_from_json = Model.model_validate_json(model_json)
    assert model_from_json.a.unit == angstrom
    assert model_from_json.a.value_in_unit(angstrom) == pytest.approx(1.0)

    assert model_from_json.b.unit == nanometer
    assert model_from_json.b.value_in_unit(nanometer) == pytest.approx(0.1)


def test_invalid_units():
    if pydantic.__version__.startswith("1."):
        pytest.skip("pydantic has version 1.x")

    from pydantic_units import OpenMMQuantity

    class Model(pydantic.BaseModel):
        a: OpenMMQuantity[angstrom]

    with pytest.raises(pydantic.ValidationError):
        Model(a=1.0 * kelvin)

    with pytest.raises(pydantic.ValidationError):
        Model.model_validate_json('{"a":"1.00000000 kelvin"}')
