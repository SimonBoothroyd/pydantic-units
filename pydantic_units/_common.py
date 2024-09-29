"""Common functions for parsing and serializing quantities

Notes:
    * This module is based on functions from ``femto``.
"""

import ast
import operator
import re

import openmm.unit
from openmm.unit import Quantity, Unit, ampere, dimensionless

_UNIT_LOOKUP = {}

for __unit in openmm.unit.__dict__.values():
    if isinstance(__unit, Unit) and not __unit == ampere:
        _UNIT_LOOKUP[__unit.get_symbol()] = __unit
        _UNIT_LOOKUP[__unit.get_name()] = __unit

_UNIT_LOOKUP["amu"] = openmm.unit.atomic_mass_unit
del __unit


def _openmm_quantity_from_str(value: str) -> Quantity:
    def ast_parse(node: ast.expr):
        operators = {
            ast.Pow: operator.pow,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.USub: operator.neg,
        }

        if isinstance(node, ast.Name):
            if node.id not in _UNIT_LOOKUP:
                raise KeyError(f"unit could not be found: {node.id}")
            return _UNIT_LOOKUP[node.id]
        elif isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](ast_parse(node.operand))
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](ast_parse(node.left), ast_parse(node.right))
        else:  # pragma: no cover
            raise NotImplementedError(node)

    value = value.strip()
    value_match = re.match(r"^([0-9.\-+]+)[ ]*[a-zA-Z(\[]", value)

    if value_match:
        split_idx = value_match.regs[-1][-1]
        value = f"{value[:split_idx]} * {value[split_idx:]}"

    return ast_parse(ast.parse(value, mode="eval").body)


def quantity_validator(value: str | Quantity, expected_units: Unit) -> Quantity:
    """Validate a string or quantity as a quantity with expected units

    Args:
        value: The value to validate
        expected_units: The expected units

    Raises:
        ValueError: If the value is not a valid quantity or has the wrong units

    Returns:
        The validated quantity.
    """
    if isinstance(value, str):
        value = _openmm_quantity_from_str(value)

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
    unit = value.unit
    value = value.value_in_unit(unit)

    bases = list(reversed([*unit.iter_base_or_scaled_units()]))

    components = [
        (
            None if i == 0 else "*",
            base.symbol + ("" if exponent == 1 else f"**{int(exponent)}"),
        )
        for i, (base, exponent) in enumerate(bases)
    ]

    if unit == dimensionless:
        components = []

    unit_str = " ".join(
        v for component in components for v in component if v is not None
    )
    return f"{value} {unit_str}" if len(unit_str) > 0 else f"{value}"


__all__ = ["quantity_validator", "quantity_serializer"]
