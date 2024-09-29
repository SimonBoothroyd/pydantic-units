"""OpenMM Quantity type for Pydantic v1."""

from functools import partial
from typing import TYPE_CHECKING

from openmm.unit import Quantity

from pydantic_units._common import quantity_validator

try:
    import pydantic.v1 as pydantic
except ImportError:  # pragma: no cover
    import pydantic  # noqa: F401


class _OpenMMQuantityMeta(type):
    def __getitem__(self, t):
        return type("OpenMMQuantity", (OpenMMQuantity,), {"__unit__": t})


class OpenMMQuantity(Quantity, metaclass=_OpenMMQuantityMeta):
    """A pydantic safe OpenMM quantity type that validates unit compatibility."""

    @classmethod
    def __get_validators__(cls):
        yield partial(quantity_validator, expected_units=cls.__unit__)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


if TYPE_CHECKING:
    OpenMMQuantity = Quantity  # noqa: F811

__all__ = ["OpenMMQuantity"]
