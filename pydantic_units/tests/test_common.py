import pytest
from openmm import unit

from pydantic_units._common import quantity_serializer, quantity_validator


@pytest.mark.parametrize(
    "value, expected",
    [
        (1.0 * unit.angstrom, "1.0 A"),
        (1.0 * unit.angstrom**2, "1.0 A**2"),
        (1.0 * unit.atomic_mass_unit, "1.0 Da"),
        (1.0 * unit.kilojoules_per_mole, "1.0 kJ * mol**-1"),
        (1.0 * unit.nanometers, "1.0 nm"),
        (1.0 * unit.kilojoules_per_mole / unit.kelvin**2, "1.0 kJ * mol**-1 * K**-2"),
        (1.0 * unit.dimensionless, "1.0"),
    ],
)
def test_quantity_serializer(value, expected):
    assert quantity_serializer(value) == expected


@pytest.mark.parametrize(
    "value, expected",
    [
        ("2.0 A", 2.0 * unit.angstrom),
        ("2.0 Å", 2.0 * unit.angstrom),
        ("2.0 angstrom", 2.0 * unit.angstrom),
        ("2.0 kJ/mole", 2.0 * unit.kilojoules_per_mole),
        ("2.0 * A", 2.0 * unit.angstrom),
        ("-2.0 / A", -2.0 / unit.angstrom),
        ("-2.0 A", -2.0 * unit.angstrom),
        ("3.0A**2", 3.0 * unit.angstrom**2),
        ("4.0(kcal/(mol*A**2))", 4.0 * unit.kilocalorie_per_mole / unit.angstrom**2),
        ("5.0  amu", 5.0 * unit.atomic_mass_unit),
        ("   5.0*amu    ", 5.0 * unit.atomic_mass_unit),
    ],
)
def test_quantity_validator(value, expected):
    actual = quantity_validator(value, expected.unit)

    assert actual.unit == expected.unit

    assert actual.value_in_unit_system(unit.md_unit_system) == pytest.approx(
        expected.value_in_unit_system(unit.md_unit_system)
    )


def test_quantity_validator_bad_unit():
    with pytest.raises(KeyError, match="unit could not be found"):
        quantity_validator("1.0 * ampere", unit.ampere)
