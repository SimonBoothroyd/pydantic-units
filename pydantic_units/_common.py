from openff.units import Quantity as OpenFFQuantity
from openff.units.openmm import openmm_unit_to_string
from openff.units.openmm import to_openmm as openff_to_openmm
from openmm.unit import Quantity, Unit


def quantity_validator(
    value: str | Quantity | OpenFFQuantity, expected_units: Unit
) -> Quantity:
    if isinstance(value, str):
        value = OpenFFQuantity(value)
    if isinstance(value, OpenFFQuantity):
        value = openff_to_openmm(value)

    assert isinstance(value, Quantity), f"invalid type - {type(value)}"

    try:
        return value.in_units_of(expected_units)
    except TypeError as e:
        raise ValueError(
            f"invalid units {value.unit} - expected {expected_units}"
        ) from e


def quantity_serializer(value: Quantity) -> str:
    """Serialize a Quantity to a string

    Args:
        value: The quantity to serialize

    Returns:
        The serialized string
    """
    unit_str = openmm_unit_to_string(value.unit)
    return f"{value.value_in_unit(value.unit):.8f} {unit_str}"


__all__ = ["quantity_validator", "quantity_serializer"]
